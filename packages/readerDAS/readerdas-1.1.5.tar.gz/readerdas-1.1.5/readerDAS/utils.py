import numpy as np
import numpy.typing as npt
from scipy.signal import medfilt2d

from typing import Annotated
import warnings

import plotly.graph_objects as go
from plotly.subplots import make_subplots

wavelength_m = 1550e-9
n_g = 1.468  # indice di rifrazione. G.657.A1 SM fiber at 1550 nm
xi = 0.78  # fattore di conversione effetto foto-elastico.


def median_filter(data: npt.ArrayLike, kernel_size: tuple[int, int]) -> npt.ArrayLike:
    """Applica 2d median filter alla matrice, utilizzando medfilt2d di scipy.
    Ref: https://doi.org/10.1038/s41467-024-50604-6 e il notebook
    https://github.com/smouellet/hhdas/blob/main/01_LF-DAS_processing.ipynb

    :param data: np.array 2D da filtrare.
    :param kernel_size: dimensione della finestra, in campioni.

    :return: np.array 2D filtrato.
    :rtype: npt.ArrayLike
    """

    return medfilt2d(data, kernel_size=kernel_size)


def phase_to_strain(data: npt.ArrayLike, gauge_length_m: float) -> npt.ArrayLike:
    """Converte fase (rad) a strain.

    :param npt.ArrayLike data: matrice 2d della fase, espressa in radianti.
    :param float gauge_length_m: gauge length espressa in metri.
    :return: dati convertiti in strain.
    :rtype: npt.ArrayLike"""

    warnings.warn("Funzione in sviluppo", UserWarning)
    conversion_factor = wavelength_m / (4 * np.pi * n_g * gauge_length_m * xi)
    return data * conversion_factor


def strain_to_strainrate(
    data: npt.ArrayLike, time_step_s: float, differential_time_s: float
) -> npt.ArrayLike:
    """Converte in strain rate, calcolando la derivata temporale dello strain
    utilizzando metodo "central differences" tra elementi temporali consecutivi
    della funzione numpy.gradient.

    :param npt.ArrayLike data: matrice 2d dello strain.
    :param float time_step_s: passo temporale, in secondi.
    :param float differential_time_s: passo temporale per il calcolo della derivata, in secondi.
    :return: dati convertiti in strain rate.
    :rtype: npt.ArrayLike"""

    warnings.warn("Funzione in sviluppo", UserWarning)
    delta_samples = int(time_step_s / differential_time_s)
    return np.gradient(data, delta_samples, axis=0)


Energy = Annotated[npt.ArrayLike, "Energy. 2d array (times, position)."]
AxisTime = Annotated[npt.ArrayLike, "Time axis, UTC"]


def plot_energy_bands(
    energies: dict[str, Energy],
    axis_time_utc: AxisTime,
    axis_position_m: npt.ArrayLike,
    log_scale: bool = False,
    zmax: float = None,
) -> go.Figure:
    """Plot delle bande di energia.

    :param dict[str,Energy] energies: dizionario con le matrice 2d delle energie.
    :param AxisTime axis_time_utc: asse temporale, UTC.
    :param npt.ArrayLike axis_position_m: asse delle posizioni, metri.
    :param float zmax: valore massimo dell'asse z. Se None, viene calcolato come massimo globale tra tutte le bande.
    :return: figura plotly con le bande di energia.
    :rtype: go.Figure"""

    warnings.warn("Funzione in sviluppo", UserWarning)

    fig = make_subplots(
        rows=1,
        cols=len(energies),
        subplot_titles=list(energies.keys()),
        horizontal_spacing=0.05,
        shared_xaxes=True,
        shared_yaxes=True,
    )

    if zmax is None:
        zmax = 0
        for energy in energies.values():
            zmax = max(np.max(energy), zmax)
        if log_scale:
            zmax = 20 * np.log10(zmax)

    for i, (_, energy) in enumerate(energies.items()):
        fig.add_trace(
            go.Heatmap(
                z=energy if not log_scale else 20 * np.log10(energy),
                y=axis_time_utc,
                x=axis_position_m,
                colorscale="Viridis",
                showscale=False,
                zmax=zmax,
                zmin=0,
                zauto=False,
            ),
            row=1,
            col=i + 1,
        )

    fig.update_layout(
        title=(
            "Energy Bands, linear scale" if not log_scale else "Energy Bands, log scale"
        ),
        yaxis_title="Time (UTC)",
        xaxis_title="Position (m)",
    )
    return fig
