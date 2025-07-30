import logging
import errno
import json

from datetime import datetime, timedelta, timezone
from tzlocal import get_localzone
from packaging.version import Version
from glob import glob
from os import PathLike, path, strerror, getcwd
import numpy as np
import numpy.typing as npt
import h5py
from itertools import compress

from .errors import (
    NoFilesSelected,
    FolderNotFound,
    TemporalMisalignment,
    SectionNotFound,
    DataTypeNotAvailable,
)

from .classes import Parameters, SectionInfo, SliceFile, DataType, Data
from .versioning import parse_version, check_if_remove_steps


logger = logging.getLogger(name="readerDAS")


def h5info(filename: str | PathLike):
    if not path.isfile(filename):
        raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), filename)

    info = dict()
    with h5py.File(filename, "r") as f:
        info["sections"] = f.attrs["sections"]
        info["starttime_utc"] = datetime.fromtimestamp(
            f.attrs["first_measure_ms"] / 1000, timezone.utc
        )

        phase_shape = f[info["sections"][0]]["phase"].shape
        magnitude_shape = f[info["sections"][0]]["magnitude"].shape
        info["position_step_m"] = f.attrs["position_step_m"]
        info["time_step_s"] = f.attrs["time_step_s"]
        info["duration_s"] = (
            max([phase_shape[0], magnitude_shape[0]]) * info["time_step_s"]
        )
        info["data_available"] = [
            type
            for type in ["phase", "magnitude"]
            if f[info["sections"][0]][type].shape[0] > 0
        ]
        # info["settings"] = json.loads(f.attrs["settings"])

    return info


def from_file(
    filename: str | PathLike,
    section: str = "full",
    data_type: DataType = "phase",
    start_s: float = 0,
    count_s: float = None,
    remove_steps: bool = True,
) -> Data:
    """
    Carica dati da un singolo file.

    :param str|PathLike filename: filename del file da cui caricare dati.
    :param str section: nome della sezione da cui caricare dati. Default: "full".
    :param str data_type: tipo di dato da caricare. Supportati: "magnitude", "phase". Default: "phase".
    :type data_type: str, optional.
    :param float start_s: istante, in secondi, da cui iniziare a caricare dati. Arrotondato al multiplo del blocco più vicino. Default: 0, da inizio file.
    :param float count_s: durata, in secondi, della finestra temporale da caricare. Arrotondato al multiplo del blocco più vicino. Default: fino a fine file.
    :param bool remove_steps: se rimuovere gli step di fase tra blocchi, ignorato per versioni >=1.2 del sw LabVIEW.
    :return: dati importati.
    :rtype: Data
    :raises FileNotFoundError: se il file non esiste.
    :raises SectionNotFound: se la sezione non esiste nel file.
    :raises DataTypeNotAvailable: se il tipo di dato non esiste nel file.
    """
    if not path.isfile(filename):
        raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), filename)

    with h5py.File(filename, "r") as f:
        if section not in f.attrs["sections"]:
            raise SectionNotFound(sections=f.attrs["sections"], section=section)

        data_available = h5info(filename=filename)["data_available"]
        if data_type not in data_available:
            raise DataTypeNotAvailable(
                requested_type=data_type, available_types=data_available
            )
        version = parse_version(f.attrs["sw_version"])
        settings = json.loads(f.attrs["settings"])
        position_step_m = f.attrs["position_step_m"]
        time_step_s = f.attrs["time_step_s"]

        first_measure = f.attrs["first_measure_ms"]

        actual_scan_rate_Hz = settings["hardware"]["board"]["scan_rate_Hz"] / max(
            settings["analyze"]["resample"]["time_factor"], int(1)
        )
        actual_scans_per_block = settings["hardware"]["board"]["scans_per_read"] / max(
            settings["analyze"]["resample"]["time_factor"], int(1)
        )

        start_slow_index = int(
            (start_s / time_step_s) // actual_scans_per_block * actual_scans_per_block
        )
        start_time = datetime.fromtimestamp(
            first_measure / 1000, timezone.utc
        ) + timedelta(seconds=start_s)

        if not count_s:
            # leggo fino alla fine, pazienza se è più di quello che c'è, tanto python ignora.
            count_s = h5info(filename=filename)["duration_s"]

        slow_to_read = (
            (count_s * actual_scan_rate_Hz + actual_scans_per_block - 1)
            // actual_scans_per_block
        ) * actual_scans_per_block
        stop_slow_index = int(start_slow_index + slow_to_read)

        data = f[section][data_type][start_slow_index:stop_slow_index, :]

        axis_time_utc = [
            start_time + timedelta(seconds=i * time_step_s)
            for i in range(np.shape(data)[0])
        ]

        position_start_m = f[section].attrs["real_start_m"]
        position_size = np.shape(data)[1]
        axis_position_m = np.linspace(
            start=position_start_m,
            stop=position_start_m + position_size * position_step_m,
            num=position_size,
        )

        data = Data(
            files=[filename],
            section=section,
            type=data_type,
            data=data,
            parameters=Parameters(
                settings=settings,
                position_step_m=position_step_m,
                time_step_s=time_step_s,
                position_start_m=position_start_m,
                start_time=datetime.fromtimestamp(first_measure / 1000, timezone.utc)
                + timedelta(seconds=start_s),
                scans_per_block=int(actual_scans_per_block),
            ),
            axis_position_m=axis_position_m,
            axis_time_utc=axis_time_utc,
            remove_steps=check_if_remove_steps(version, remove_steps),
        )

        return data


class DataFolder:

    folder: PathLike
    files: list[PathLike]
    settings: dict
    position_step_m: float
    time_step_s: float
    block_time_samples: int
    data_available: list[DataType]
    sections: dict[SectionInfo]
    first_measure_ms: int  # da attributo in primo file della cartella
    _first_timestamp_files_approx: (
        npt.ArrayLike
    )  # i timestamps approssimativi contenuti, come attributo, in ogni file.
    time_samples: npt.ArrayLike
    file_duration_ms: npt.ArrayLike
    first_timestamp_files: npt.ArrayLike
    version: Version

    def __init__(self, folder: str | PathLike, max_disalignment_ms: int = 5000):

        if not folder:
            folder = getcwd()

        if not path.isdir(folder):
            FolderNotFound(folder=folder)

        self.folder = folder
        self.files = glob(path.join(folder, "*.h5"))
        if len(self.files) == 0:
            NoFilesSelected(folder=folder)

        logger.debug(f"Found {len(self.files)} files in folder {self.folder}.")

        self._get_general_info()
        self._get_files_timing()
        self._check_time_continuity(max_disalignment_ms=max_disalignment_ms)

    def _get_general_info(self):
        """Legge dal primo file nella cartella le informazioni generali, quali tipo di dato, time_step, position_step, sezioni e lunghezza delle sezioni"""
        with h5py.File(self.files[0], "r") as f:
            self.settings = json.loads(f.attrs["settings"])
            section_names = f.attrs["sections"]
            self.data_available = [
                type
                for type in ["phase", "magnitude"]
                if f[section_names[0]][type].shape[0] > 0
            ]
            self.time_step_s = f.attrs["time_step_s"]
            self.position_step_m = f.attrs["position_step_m"]
            self.block_time_samples = f[section_names[0]][
                self.data_available[0]
            ].chunks[0]
            self.first_measure_ms = f.attrs["first_measure_ms"]
            self.version = parse_version(f.attrs["sw_version"])

            self.sections = dict()
            for section in section_names:
                self.sections[section] = SectionInfo(
                    name=section,
                    start_m=f[section].attrs["real_start_m"],
                    stop_m=f[section].attrs["real_start_m"]
                    + f[section][self.data_available[0]].shape[1]
                    * self.position_step_m,
                    position_samples=f[section][self.data_available[0]].shape[1],
                )

    def _get_files_timing(self):
        """Sniffa i files nella cartella per salvare i tempi di inizio e durate, in ms, di ognuno."""
        self.time_samples = np.array([], dtype=int)
        self._first_timestamp_files_approx = np.array([])
        for i, file in enumerate(self.files):
            try:
                with h5py.File(file, "r") as f:
                    first_section = f.attrs["sections"][0]
                    self._first_timestamp_files_approx = np.append(
                        self._first_timestamp_files_approx, f.attrs["first_measure_ms"]
                    )
                    file_time_samples = int(
                        f[first_section][self.data_available[0]].shape[0]
                    )
                    self.time_samples = np.append(self.time_samples, file_time_samples)
            except OSError:
                # l'idea è che sia ultimo file ancora in uso da LabVIEW
                self.files = self.files[:i]
                break

        self.file_duration_ms = 1000 * self.time_samples * self.time_step_s
        self.first_timestamp_files = self.first_measure_ms + np.append(
            0, np.cumsum(self.file_duration_ms[:-1])
        )

    def _check_time_continuity(self, max_disalignment_ms: int = 5000) -> npt.ArrayLike:
        """Verifica che non ci siano salti temporali tra due files consecutivi."""
        expected_start_time = self.first_measure_ms + np.append(
            0, np.cumsum(self.file_duration_ms[:-1])
        )
        delta_time_ms = np.diff(
            self._first_timestamp_files_approx - expected_start_time
        )
        check_time = delta_time_ms >= max_disalignment_ms
        self.time_mode = "continuous"
        if any(check_time):
            self.time_mode = "discrete"
            # FIXME: in realtà non è un warning ma interrompe proprio...
            raise TemporalMisalignment(
                folder=self.folder,
                list_of_files=list(compress(self.files[1:], check_time)),
            )
        return delta_time_ms

    def _find_time_start_stop(
        self, start_time: datetime, stop_time: datetime
    ) -> tuple[int, int, int, int]:
        """Trovo primo elemento del primo file e ultimo elemento dell'ultimo file in base a timestamp forniti."""
        if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
            # se timestamps sono naive, assumo siano con timezone locale e la assegno.
            local_timezone = get_localzone()
            start_time.replace(tzinfo=local_timezone)
            stop_time.replace(tzinfo=local_timezone)

        start_time_ms = int(start_time.timestamp() * 1e3)
        stop_time_ms = int(stop_time.timestamp() * 1e3)

        if start_time_ms == self.first_measure_ms:
            first_file_index = 0
        else:
            first_file_index = (
                np.searchsorted(self.first_timestamp_files, start_time_ms, side="left")
                - 1
            )
        last_file_index = (
            np.searchsorted(self.first_timestamp_files, stop_time_ms, side="right") - 1
        )

        first_file_start_sample = int(
            (
                (start_time_ms - self.first_timestamp_files[first_file_index])
                / (1000 * self.time_step_s)
                // self.block_time_samples
            )
            * self.block_time_samples
        )
        last_file_stop_sample = int(
            np.ceil(
                (stop_time_ms - self.first_timestamp_files[last_file_index])
                / (1000 * self.time_step_s)
                // self.block_time_samples
            )
            * self.block_time_samples
        )

        logger.debug(
            f"FIRST: file index={first_file_index}, sample={first_file_start_sample}. LAST: file_index={last_file_index}, sample={last_file_stop_sample}."
        )

        return (
            first_file_index,
            last_file_index,
            first_file_start_sample,
            last_file_stop_sample,
        )

    def _create_list_of_time_slices(
        self,
        first_file_index,
        last_file_index,
        first_file_start_sample,
        last_file_stop_sample,
    ) -> tuple[list[SliceFile], datetime, int]:

        if first_file_index == last_file_index:
            list_of_time_slices = [
                SliceFile(
                    file_index=first_file_index,
                    file_name=self.files[first_file_index],
                    first_sample=first_file_start_sample,
                    last_sample=last_file_stop_sample,
                )
            ]
            number_of_samples = int(last_file_stop_sample - first_file_start_sample)
            actual_start_ms = (
                first_file_start_sample * self.time_step_s * 1000
                + np.sum(self.file_duration_ms[:first_file_index])
                + self.first_measure_ms
            )
            actual_start_datetime = datetime.fromtimestamp(
                actual_start_ms / 1000,
                timezone.utc,
            )
        else:
            list_of_time_slices = [
                SliceFile(
                    file_index=first_file_index,
                    file_name=self.files[first_file_index],
                    first_sample=first_file_start_sample,
                    last_sample=self.time_samples[first_file_index],
                )
            ]

            middle_files_index = range(first_file_index + 1, last_file_index, 1)
            for file_index in middle_files_index:
                list_of_time_slices.append(
                    SliceFile(
                        file_index=file_index,
                        file_name=self.files[file_index],
                        first_sample=0,
                        last_sample=self.time_samples[file_index],
                    )
                )

            list_of_time_slices.append(
                SliceFile(
                    file_index=last_file_index,
                    file_name=self.files[last_file_index],
                    first_sample=0,
                    last_sample=last_file_stop_sample,
                )
            )

            number_of_samples = np.sum(
                [
                    slice.last_sample - slice.first_sample
                    for slice in list_of_time_slices
                ]
            )
            actual_start_ms = (
                self.first_measure_ms
                + np.sum(self.file_duration_ms[:first_file_index])
                + list_of_time_slices[0].first_sample * self.time_step_s * 1000
            )
            actual_start_datetime = datetime.fromtimestamp(
                actual_start_ms / 1000, timezone.utc
            )

        logger.debug(
            f"{actual_start_ms=}, {actual_start_datetime=}, {number_of_samples=}"
        )

        return list_of_time_slices, actual_start_datetime, number_of_samples

    def _find_position_slice(
        self,
        section: SectionInfo,
        start_position_m: float = 0,
        stop_position_m: float = None,
    ) -> tuple[int, int]:

        logger.debug(
            f"Searching position indexes from {start_position_m=} to {stop_position_m=}..."
        )
        start_position_index = 0
        if start_position_m is not None:
            start_position_index = int(
                np.floor((start_position_m - section["start_m"]) / self.position_step_m)
            )
        if stop_position_m is not None:
            stop_position_index = int(
                np.ceil((stop_position_m - section["start_m"]) / self.position_step_m)
            )
        else:
            stop_position_index = section["position_samples"]

        logger.debug(
            f"Position slice: from {start_position_index} to {stop_position_index} (samples)."
        )

        return start_position_index, stop_position_index

    def get_data(
        self,
        type: DataType,
        section: str = None,
        start_position_m: float = None,
        stop_position_m: float = None,
        start_time: datetime = None,
        stop_time: datetime = None,
        remove_steps: bool = True,
    ) -> Data:
        """
        Carica in memoria una slice temporale e spaziale del tipo di dato richiesto.

        :param str type: tipo di dato da caricare. Supportati: "magnitude", "phase"
        :param str section: nome della sezione da cui caricare dati. Se non fornita si utilizza la prima sezione disponibile
        :param float start_position_m: Posizione ASSOLUTA in metri da cui partire con slice spaziale. Se non fornito si parte da inizio della sezione.
        :param float stop_position_m: Posizione ASSOLUTA in metri cui finire con slice spaziale. Se non fornito si arriva in fondo alla sezione.
        :param datetime.datetime start_time: datetime da cui iniziare a caricare dati. Arrotondato al multiplo del blocco più vicino. Se non fornito si utilizza primo timestamp disponibile nella cartella.
        :param datetime.datetime stop_time: datetime fino a cui caricare dati. Arrotondato al multiplo del blocco più vicino. Se non fornito si utilizza ultimo timestamp disponibile nella cartella.
        :param bool remove_steps: se rimuovere gli step di fase tra blocchi, ignorato per versioni >=1.2 del sw LabVIEW.
        :return: dati importati.
        :rtype: Data
        :raises SectionNotFound: se la sezione non esiste nel file.
        :raises DataTypeNotAvailable: se il tipo di dato non esiste nel file.
        """

        if type not in self.data_available:
            raise DataTypeNotAvailable(
                requested_type=type, available_types=self.data_available
            )

        if section is None:
            section = self.sections.keys()[0]
        if section not in self.sections.keys():
            raise SectionNotFound(sections=self.sections.keys(), section=section)

        if start_time is None:
            start_time = datetime.fromtimestamp(
                self.first_measure_ms / 1000, timezone.utc
            )
        if stop_time is None:
            stop_time = datetime.fromtimestamp(
                (self.first_measure_ms + np.sum(self.file_duration_ms)) / 1000,
                timezone.utc,
            )

        section_to_load = self.sections[section]
        start_position_sample, stop_position_sample = self._find_position_slice(
            section=section_to_load,
            start_position_m=start_position_m,
            stop_position_m=stop_position_m,
        )

        list_of_time_slices, actual_start_datetime, number_of_time_samples = (
            self._create_list_of_time_slices(
                *self._find_time_start_stop(start_time=start_time, stop_time=stop_time)
            )
        )

        to_stack = list()
        for slice in list_of_time_slices:
            with h5py.File(slice.file_name, "r") as f:
                data_slice = f[section][type][
                    slice.first_sample : slice.last_sample,
                    start_position_sample:stop_position_sample,
                ]
                to_stack.append(data_slice)
                logger.debug(
                    f"Loading data...file_index: {slice.file_index} - shape: {np.shape(data_slice)}, max: {np.max(data_slice)}, min: {np.min(data_slice)}"
                )
        loaded_data = np.vstack(to_stack)

        axis_datetime = [
            actual_start_datetime + timedelta(seconds=i * self.time_step_s)
            for i in range(np.shape(loaded_data)[0])
        ]

        position_size = np.shape(loaded_data)[1]
        logger.debug(
            f"Position: {start_position_sample=}, {position_size=}, {self.position_step_m=}"
        )
        axis_position_m = (
            np.linspace(
                start=start_position_sample * self.position_step_m,
                stop=start_position_sample * self.position_step_m
                + position_size * self.position_step_m,
                num=position_size,
            )
            + section_to_load["start_m"]
        )

        return Data(
            files=[slice.file_name for slice in list_of_time_slices],
            section=section,
            type=type,
            data=loaded_data,
            parameters=Parameters(
                position_step_m=self.position_step_m,
                time_step_s=self.time_step_s,
                position_start_m=axis_position_m[0],
                start_time=actual_start_datetime,
                scans_per_block=self.block_time_samples,
                settings=self.settings,
            ),
            axis_time_utc=axis_datetime,
            axis_position_m=axis_position_m,
            remove_steps=check_if_remove_steps(self.version, remove_steps),
        )

    def __str__(self) -> str:
        stringa = (
            f"Folder: {self.folder}, {len(self.files)} files."
            + f"\nfrom {datetime.fromtimestamp(self.first_measure_ms/1000,timezone.utc)} to {datetime.fromtimestamp((self.first_measure_ms+np.sum(self.file_duration_ms))/1000,timezone.utc)}"
            + f"\nPosition step: {self.position_step_m:.3f} m, Time step: {self.time_step_s:.3f} s."
            + f"\nData types available: {self.data_available}."
            + f"\nSections:"
        )
        stringa_sections = "".join(
            [
                f"\n\t- '{section["name"]}': from {section["start_m"]:.2f} m to {section["stop_m"]:.2f} m"
                for section in self.sections.values()
            ]
        )
        return stringa + stringa_sections
