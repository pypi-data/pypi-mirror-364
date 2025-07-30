# ReaderDAS

## Installazione

Installare attraverso PyPi:

```cmd
pip install readerDAS
pip install readerDAS --upgrade
```

## Caricamento dati

Caricamento in memoria dei dati. Le funzioni sotto restituiscono entrambe un oggetto di tipo `Data`.

Importare:

```python
from readerDAS import h5info, from_file, DataFolder
```

### Singolo file

Per leggere dati da un singolo file.

```python
filename = 'file_di_prova.h5'
h5info(filename)
data_single = from_file(filename=filename, section='full', start_s=0, count_s=20)
```

andando quindi ad indicare il nome della `sezione` (usare la funzione `h5info` per vedere che sezioni sono disponibili) e la sezione temporale che si vuole importare; di default la sezione caricata è `full`, ovvero nel caso in cui non si siano impostate sezioni nel programma di acquisizione. Di default parte da inizio file se `start_s` non è fornito; arriva fino a fine file se `count_s` non è fornito.e

### Multipli files in una cartella

Per caricare dati da più files, specificando un intervallo temporale e un intervallo di posizioni contenute in una sezione.

> ATTENZIONE: l'assunzione è che tutti i files contenuti nella cartella siano stati salvati con continuità e con stessi parametri.

Prima si inizializza la cartella, andando a caricare le informazioni e i parametri dell'acquisizione.

```python
folder = 'Downloads/DAS_Misure'
folder_obj = DataFolder(folder=folder)
print(folder_obj)
```

Successivamente è possibile utilizzare l'oggetto `folder_obj` per caricare i dati desiderati:

```python
start_time = datetime(2024,10,7,9,10,0,tzinfo=timezone.utc)
stop_time = datetime(2024,10,7,9,35,0,tzinfo=timezone.utc)
loaded_data,info_slice = folder_obj.get_data(type='phase',section='full',start_position_m=20, stop_position_m=370, start_time=start_time, stop_time=stop_time)
print(loaded_data)
```

Si può selezionare il tipo di dato da caricare, con parametro `type`: `phase` (default) o `magnitude`.

Se si vuole lavorare in secondi, invece che datetime, al momento si deve fare:

```python
from datetime import datetime, timedelta

# rispetto ad inizio file:
start_time = datetime.fromtimestamp(a.first_measure_ms/1000, timezone.utc) + timedelta(seconds=10)
stop_time = start_time + timedelta(seconds=200)
```

## Elaborazione

L'oggetto `Data` espone alcuni metodi per elaborare dato, che andranno eventualmente espansi.

### Energia

Calcolata su finestre temporali `window_s` e come somma del modulo quadro, posizione per posizione lungo la fibra.

```python
energy_window_s = 0.512
energy, axis_time_energy = loaded_data.energy(window_s=energy_window_s)
```

Come esempio, seguente codice per plot waterfall dell'energia utilizzando la libreria `plotly`:

```python
import plotly.graph_objects as go

colormap = 'Viridis'
fig_energy = go.Figure(layout=dict(title=f"Energy of '{loaded_data.type}', window: {energy_window_s}s",xaxis_title='Position (m)',
                                   height=800,))
fig_energy.add_trace(go.Heatmap(x=loaded_data.axis_position_m,y=axis_time_energy,z=energy,
                         #zsmooth='best',
                         colorscale=colormap, showscale=False,
                         zmax=50,zmin=0,zauto=False))
fig_energy.show()
```

### Singolo punto spaziale

Un helper method per estrarre l'andamento temporale di un solo punto lungo la fibra, espresso in metri. Sotto per esempio il metro 92, con esempio di plot in `plotly`.

```python
from plotly.subplots import make_subplots

position_data, actual_position, position_index = loaded_data.filter_by_position(position_m=92)

yaxis_label = "Phase (rad)" if loaded_data.type == "phase" else "Magnitude (a.u.)"
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=loaded_data.axis_time_utc,y=position_data, name=yaxis_label))
fig.add_trace(go.Scatter(x=axis_time_energy, y=energy[:,position_index],name='energy'),secondary_y=True)
fig.update_yaxes(title_text=yaxis_label, secondary_y=False)
fig.update_yaxes(title='Energy (a.u.)', secondary_y=True)
fig.update_xaxes(title='UTC Time')
fig.update_layout(title=f"Position: {actual_position:.02f}m",showlegend=False)
fig.show()
```

## Sottocampionamento temporale

E' possibile importare i dati contenuti nei files di una cartella, decimarli temporalmente e risalvari in un singolo file h5. Per farlo utilizzare la funzione `sottocampionamento.decimate_folder`

```python

from readerDAS.sottocampionamento import decimate_folder

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
```

## TODO

- sottocampionamento spaziale, senza proprio caricare quei punti in memoria. Dubbia utilità dal punto di vista della velocità perché tanto il chunk viene caricato tutto in memoria e poi indicizzato...ma sicuramente la memoria complessiva viene ridotta.
