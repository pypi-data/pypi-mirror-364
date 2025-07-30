from glob import glob
from os import path, PathLike
import logging
from datetime import datetime, timezone

import h5py
import numpy as np
import numpy.typing as npt
from scipy.signal import decimate

from tqdm import tqdm
from typing import Literal
import json

from .main import h5info

logger = logging.getLogger(name="readerDAS")

"""
Parametri sono nell'if in fondo al file.
Non sto prendendo il buffer DOPO, solo prima, per fare filtro. Andrebbe sistemato, anche se onestamente non vedo nessuna distorsione particolare, probabilmente solo perché ordine del filtro è basso.
Il tempo stringa della prima e ultima misura stanno cambiando offset timezone...boh, al massimo sistemo a posteriori.  
Non cicla sulle sezioni per ora, anche se dovrebbe essere solo necessario aggiungere un nested for loop nella funzione run.

!!! Prima di eliminare dati meglio provare a fare confronti, tipo guardando waterfall e simili per vedere che non abbia introdotto qualche cavolata. !!!
"""


def _read_attributes(file: str | PathLike) -> tuple[dict, dict]:
    with h5py.File(file, "r") as f:
        general_attributes = dict(f.attrs.items())
        sections_attributes = dict()
        for section in general_attributes["sections"]:
            sections_attributes[section] = dict(f[section].attrs.items())

    return general_attributes, sections_attributes


def _remove_block_steps(
    data: npt.ArrayLike, scans_per_block: int = 256
) -> npt.ArrayLike:
    """Rimozione dei gradini tra ogni blocco, nella fase."""
    block_size = scans_per_block
    fine_blocchi = data[block_size - 1 :: block_size, :][:-1, :]
    fine_blocchi = np.insert(fine_blocchi, 0, 0, axis=0)
    inizio_blocchi = data[::block_size, :]

    delta_blocchi = fine_blocchi - inizio_blocchi
    delta_blocchi_cum = np.cumsum(delta_blocchi, axis=0)
    matrix_offset = np.repeat(delta_blocchi_cum, block_size, axis=0)
    return data + matrix_offset


def _undersample(
    data: npt.ArrayLike,
    downsample_factor: int,
    filter_order: int,
    buffer: npt.ArrayLike = None,
) -> npt.ArrayLike:

    if buffer is not None:
        data = np.vstack((buffer - buffer[-1], data))

    decimated_data = decimate(
        data, downsample_factor, n=filter_order, ftype="fir", axis=0
    )

    if buffer is not None:
        decimated_data = decimated_data[
            int(np.shape(buffer)[0] / downsample_factor) :, :
        ]

    return decimated_data


def _create_h5(
    file: str | PathLike, general_attributes: dict, sections_attributes: dict
):

    with h5py.File(file, "w") as f:
        for attribute in general_attributes.items():
            try:
                f.attrs[attribute[0]] = attribute[1]
            except TypeError:
                logger.info(f"TypeError with {attribute}")

        for section in sections_attributes:
            section_grp = f.create_group(section)
            for attribute in sections_attributes[section].items():
                section_grp.attrs[attribute[0]] = attribute[1]


def _create_dataset(
    file: str | PathLike,
    type: Literal["magnitude", "phase"],
    data: npt.ArrayLike,
    section: str,
):
    with h5py.File(file, "a") as f:
        f[section].create_dataset(
            type,
            data=data,
            compression="gzip",
            dtype="f4" if type == "phase" else "i2",
            maxshape=(None, data.shape[1]),
        )


def _append_to_dataset(
    file: str | PathLike,
    type: Literal["magnitude", "phase"],
    data: npt.ArrayLike,
    section: str,
):
    with h5py.File(file, "a") as f:
        dataset_ref = f[section][type]
        rows_to_add = np.shape(data)[0]
        dataset_ref.resize(dataset_ref.shape[0] + rows_to_add, axis=0)
        dataset_ref[-rows_to_add:, :] = data


def _update_final_attributes(
    file: str | PathLike,
    downsample_factor: int,
):
    with h5py.File(file, "a") as f:
        f.attrs["time_step_s"] = f.attrs["time_step_s"] * downsample_factor
        temp_settings = json.loads(f.attrs["settings"])
        temp_settings["analyze"]["resample"]["time_step_s"] = f.attrs["time_step_s"]
        temp_settings["analyze"]["resample"]["time_factor"] = (
            temp_settings["analyze"]["resample"]["time_factor"] * downsample_factor
        )
        f.attrs["settings"] = json.dumps(temp_settings)

        n_rows = f[f.attrs["sections"][0]]["phase"].shape[0]

        last_measure_ms = (
            f.attrs["first_measure_ms"] + n_rows * f.attrs["time_step_s"] * 1000
        )
        f.attrs["last_measure_ms"] = last_measure_ms
        f.attrs["last_measure"] = (
            datetime.fromtimestamp(last_measure_ms / 1000, tz=timezone.utc)
            .astimezone()
            .isoformat(timespec="milliseconds")
        )


def decimate_folder(
    folder: str | PathLike,
    output_file: str | PathLike,
    target_frequency_Hz: int,
    section_index: int,
    last_position_index: int,
):
    """
    Funzione per sottocampionare temporalmente i files in un cartella e salvare nuovi dati in un singolo file. La decimazione avviene temporalmente e attraverso funzione `decimate` di scipy.signal.

    :param str|PathLike folder: cartella i cui file verranno caricati e decimati.
    :param str|PathLike output_file: nome del file h5 che verrà creato con i dati decimati.
    :param float target_frequency_Hz: Frequenza target dei dati decimati, in Hz.
    :param int section_index: indici della sezione di cui importare dati. TODO: implementare caricamento di tutte sezioni o alcune.
    :param int last_position_index: fine fibra, espresso come indici/campione. Utile per evitare di salvare dati riferiti a rumore, perché fibra già finita.
    :return: None.
    :rtype: None
    """

    files = glob(path.join(folder, "*.h5"))

    info = h5info(filename=files[0])
    downsample_factor = int((1 / target_frequency_Hz) / info["time_step_s"])
    logger.info(f"{downsample_factor=}")
    filter_order = 5

    general_attributes, sections_attributes = _read_attributes(file=files[0])
    _create_h5(output_file, general_attributes, sections_attributes)

    first = True
    for file in tqdm(files, desc="File"):
        logger.debug(f"loading {file}")
        with h5py.File(file, "r") as f:
            section_name = info["sections"][section_index]
            magnitude_temp = np.squeeze(
                f[section_name]["magnitude"][:, :last_position_index]
            )
            phase_temp = np.squeeze(f[section_name]["phase"][:, :last_position_index])
            logger.debug(
                f"Loaded {file}. Phase: {phase_temp.shape}, Magnitude: {magnitude_temp.shape}."
            )
            phase_temp = _remove_block_steps(phase_temp)
            if first:
                phase = _undersample(
                    phase_temp,
                    downsample_factor=downsample_factor,
                    filter_order=filter_order,
                )
                _create_dataset(output_file, "phase", phase, section_name)
                magnitude = _undersample(
                    magnitude_temp,
                    downsample_factor=downsample_factor,
                    filter_order=filter_order,
                )
                _create_dataset(output_file, "magnitude", magnitude, section_name)
                first = False
            else:
                phase_temp = _undersample(
                    phase_temp,
                    buffer=phase_end_buffer,
                    downsample_factor=downsample_factor,
                    filter_order=filter_order,
                )
                # phase = np.vstack((phase, phase_temp + phase[-1, :]))
                phase = phase_temp + phase[-1, :]
                _append_to_dataset(output_file, "phase", phase, section_name)
                magnitude_temp = _undersample(
                    magnitude_temp,
                    buffer=magnitude_end_buffer,
                    downsample_factor=downsample_factor,
                    filter_order=filter_order,
                )
                # magnitude = np.vstack((magnitude, magnitude_temp))
                magnitude = magnitude_temp
                _append_to_dataset(output_file, "magnitude", magnitude, section_name)

            phase_end_buffer = phase_temp[-filter_order ^ 2 :, :]
            magnitude_end_buffer = magnitude_temp[-filter_order ^ 2 :, :]

    _update_final_attributes(file=output_file, downsample_factor=downsample_factor)


if __name__ == "__main__":

    logger.basicConfig(level=logging.INFO)

    folder = "Traffico_Weekend"
    last_position_index: int = 460  # 450
    target_frequency_Hz = 10  # Hz
    output_file = "prova.h5"

    decimate_folder(
        folder=folder,
        output_file=output_file,
        target_frequency_Hz=target_frequency_Hz,
        last_position_index=last_position_index,
        section_index=0,
    )
