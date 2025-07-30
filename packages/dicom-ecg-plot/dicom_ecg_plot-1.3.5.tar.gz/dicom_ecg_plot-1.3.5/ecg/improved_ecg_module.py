# -*- coding: utf-8 -*-
"""ECG (waveform) DICOM module

Read and plot images from DICOM ECG waveforms.
Enhanced version with improved error handling, type hints, and modern Python practices.
"""

"""
The MIT License (MIT)

Copyright (c) 2013 Marco De Benedetto <debe@galliera.it>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import numpy as np
import pydicom as dicom
import struct
import io
import os
import requests
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import logging
import re

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gestione backend matplotlib
from matplotlib import use
from scipy.signal import butter, lfilter

if os.environ.get('DISPLAY', '') == '':
    use('Agg')

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

# Configurazione predefinita
try:
    from ecgconfig import WADO_SERVER, LAYOUT, INSTITUTION
except ImportError:
    WADO_SERVER = "http://example.com"
    LAYOUT = {
        '3x4_1': [[0, 3, 6, 9], [1, 4, 7, 10], [2, 5, 8, 11], [1]],
        '3x4': [[0, 3, 6, 9], [1, 4, 7, 10], [2, 5, 8, 11]],
        '6x2': [[0, 6], [1, 7], [2, 8], [3, 9], [4, 10], [5, 11]],
        '12x1': [[i] for i in range(12)]
    }
    INSTITUTION = None

__author__ = "Marco De Benedetto and Simone Ferretti"
__license__ = "MIT"
__credits__ = ["Marco De Benedetto", "Simone Ferretti", "Francesco Formisano"]
__email__ = "debe@galliera.it"
__version__ = "2.0.0"


@dataclass
class ECGConfig:
    """Configurazione per l'ECG plot"""
    paper_width: float = 297.0
    paper_height: float = 210.0
    plot_width: float = 250.0
    plot_height: float = 170.0
    margin_bottom: float = 10.0
    dpi: int = 300
    
    @property
    def margin_left(self) -> float:
        return 0.5 * (self.paper_width - self.plot_width)
    
    @property
    def margin_right(self) -> float:
        return self.margin_left
    
    @property
    def normalized_left(self) -> float:
        return self.margin_left / self.paper_width
    
    @property
    def normalized_right(self) -> float:
        return self.normalized_left + self.plot_width / self.paper_width
    
    @property
    def normalized_bottom(self) -> float:
        return self.margin_bottom / self.paper_height
    
    @property
    def normalized_top(self) -> float:
        return self.normalized_bottom + self.plot_height / self.paper_height


class ECGReadFileError(dicom.filereader.InvalidDicomError):
    """Eccezione personalizzata per errori di lettura file ECG"""
    pass


class WADOClient:
    """Client per interrogazione server WADO"""
    
    def __init__(self, server_url: str = WADO_SERVER):
        self.server_url = server_url
        self.session = requests.Session()
    
    def get_dicom(self, study_uid: str, series_uid: str, object_uid: str) -> io.BytesIO:
        """Recupera un oggetto DICOM dal server WADO"""
        payload = {
            'requestType': 'WADO',
            'contentType': 'application/dicom',
            'studyUID': study_uid,
            'seriesUID': series_uid,
            'objectUID': object_uid
        }
        
        try:
            response = self.session.get(self.server_url, params=payload, timeout=30)
            response.raise_for_status()
            return io.BytesIO(response.content)
        except requests.RequestException as e:
            logger.error(f"Errore durante il recupero DICOM: {e}")
            raise ECGReadFileError(f"Errore WADO: {e}")


class SignalProcessor:
    """Processore per i segnali ECG"""
    
    @staticmethod
    def butter_lowpass(highcut: float, sampling_freq: float, order: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """Crea un filtro passa-basso Butterworth"""
        nyquist_freq = 0.5 * sampling_freq
        high = highcut / nyquist_freq
        return butter(order, high, btype='lowpass')
    
    @staticmethod
    def apply_lowpass_filter(data: np.ndarray, highcut: float, sampling_freq: float, order: int = 2) -> np.ndarray:
        """Applica un filtro passa-basso ai dati"""
        num, denom = SignalProcessor.butter_lowpass(highcut, sampling_freq, order)
        return lfilter(num, denom, data)


class ECGPlotter:
    """Classe per il plotting degli ECG"""
    
    def __init__(self, config: ECGConfig):
        self.config = config
        self.colors = {
            'minor_grid': '#ff5333',
            'major_grid': '#d43d1a',
            'signal': 'black'
        }
        self.linewidths = {
            'minor_grid': 0.1,
            'major_grid': 0.2,
            'signal': 0.6
        }
    
    def create_figure(self, samples: int) -> Tuple[Figure, Axes]:
        """Crea la figura e gli assi per il plot"""
        fig, axes = plt.subplots(figsize=(11.69, 8.27))
        
        fig.subplots_adjust(
            left=self.config.normalized_left,
            right=self.config.normalized_right,
            top=self.config.normalized_top,
            bottom=self.config.normalized_bottom
        )
        
        axes.set_ylim([0, self.config.plot_height])
        axes.set_xlim([0, samples - 1])
        
        return fig, axes
    
    def draw_grid(self, axes: Axes, minor_axis: bool = False):
        """Disegna la griglia nell'area di plotting"""
        if minor_axis:
            axes.xaxis.set_minor_locator(plt.LinearLocator(int(self.config.plot_width + 1)))
            axes.yaxis.set_minor_locator(plt.LinearLocator(int(self.config.plot_height + 1)))
        
        axes.xaxis.set_major_locator(plt.LinearLocator(int(self.config.plot_width / 5 + 1)))
        axes.yaxis.set_major_locator(plt.LinearLocator(int(self.config.plot_height / 5 + 1)))
        
        for axis in ['x', 'y']:
            for which in ['major', 'minor']:
                if which == 'minor' and not minor_axis:
                    continue
                    
                axes.grid(
                    which=which,
                    axis=axis,
                    linestyle='-',
                    linewidth=self.linewidths[f'{which}_grid'],
                    color=self.colors[f'{which}_grid']
                )
                
                axes.tick_params(
                    which=which,
                    axis=axis,
                    color=self.colors[f'{which}_grid'],
                    bottom=False,
                    top=False,
                    left=False,
                    right=False
                )
        
        axes.set_xticklabels([])
        axes.set_yticklabels([])


class ECG:
    """Classe principale per la gestione degli ECG DICOM"""
    
    def __init__(self, source: Union[str, Dict[str, str], io.IOBase], config: Optional[ECGConfig] = None):
        """
        Costruttore della classe ECG.
        
        Args:
            source: Sorgente ECG (filename, buffer, o dict con stu/ser/obj)
            config: Configurazione personalizzata
        """
        self.config = config or ECGConfig()
        self.wado_client = WADOClient()
        self.signal_processor = SignalProcessor()
        self.plotter = ECGPlotter(self.config)
        
        # Carica il file DICOM
        self.dicom = self._load_dicom(source)
        
        # Inizializza i dati ECG
        self._initialize_ecg_data()
        
        # Crea la figura
        self.fig, self.axis = self.plotter.create_figure(self.samples)
    
    def _load_dicom(self, source: Union[str, Dict[str, str], io.IOBase]) -> dicom.FileDataset:
        """Carica il file DICOM dalla sorgente specificata"""
        try:
            if isinstance(source, dict):
                if set(source.keys()) == {'stu', 'ser', 'obj'}:
                    inputdata = self.wado_client.get_dicom(**source)
                else:
                    raise ValueError("Il dizionario deve contenere le chiavi 'stu', 'ser' e 'obj'")
            elif isinstance(source, (str, Path)):
                inputdata = str(source)
            elif hasattr(source, 'read'):
                inputdata = source
            else:
                raise ValueError("Sorgente non supportata")
            
            return dicom.read_file(inputdata)
            
        except dicom.filereader.InvalidDicomError as e:
            logger.error(f"Errore lettura file DICOM: {e}")
            raise ECGReadFileError(f"File DICOM non valido: {e}")
        except Exception as e:
            logger.error(f"Errore generico durante il caricamento: {e}")
            raise ECGReadFileError(f"Errore durante il caricamento: {e}")
    
    def _initialize_ecg_data(self):
        """Inizializza i dati ECG dal file DICOM"""
        try:
            sequence_item = self.dicom.WaveformSequence[0]
            
            # Validazione dati
            if sequence_item.WaveformSampleInterpretation != 'SS':
                raise ValueError("Interpretazione campioni non supportata")
            if sequence_item.WaveformBitsAllocated != 16:
                raise ValueError("Allocazione bit non supportata")
            
            # Estrazione dati
            self.channel_definitions = sequence_item.ChannelDefinitionSequence
            self.waveform_data = sequence_item.WaveformData
            self.channels_no = sequence_item.NumberOfWaveformChannels
            self.samples = sequence_item.NumberOfWaveformSamples
            self.sampling_frequency = sequence_item.SamplingFrequency
            
            # Calcoli derivati
            self.duration = self.samples / self.sampling_frequency
            self.mm_s = self.config.plot_width / self.duration
            
            # Processamento segnali
            self.signals = self._process_signals()
            
        except (KeyError, IndexError, AttributeError) as e:
            logger.error(f"Errore durante l'inizializzazione dati ECG: {e}")
            raise ECGReadFileError(f"Struttura DICOM non valida: {e}")
    
    def _process_signals(self) -> np.ndarray:
        """Processa i segnali ECG dal DICOM"""
        # Inizializzazione fattori e baseline
        factors = np.ones(self.channels_no)
        baselines = np.zeros(self.channels_no)
        units = []
        
        # Estrazione parametri per ogni canale
        for idx in range(self.channels_no):
            definition = self.channel_definitions[idx]
            
            if definition.WaveformBitsStored != 16:
                raise ValueError(f"Bit stored non supportati per il canale {idx}")
            
            # Sensibilità
            if definition.get('ChannelSensitivity'):
                factors[idx] = (
                    float(definition.ChannelSensitivity) *
                    float(definition.ChannelSensitivityCorrectionFactor)
                )
            
            # Baseline
            if definition.get('ChannelBaseline'):
                baselines[idx] = float(definition.ChannelBaseline)
            
            # Unità di misura
            units.append(
                definition.ChannelSensitivityUnitsSequence[0].CodeValue
            )
        
        # Decodifica dati waveform
        unpack_fmt = f'<{len(self.waveform_data) // 2}h'
        unpacked_data = struct.unpack(unpack_fmt, self.waveform_data)
        
        # Reshape e trasposizione
        signals = np.asarray(unpacked_data, dtype=np.float32).reshape(
            self.samples, self.channels_no
        ).transpose()
        
        # Applicazione fattori di conversione
        for channel in range(self.channels_no):
            signals[channel] = (signals[channel] + baselines[channel]) * factors[channel]
        
        # Filtraggio e conversione unità
        millivolts_conversion = {'uV': 1000.0, 'mV': 1.0}
        
        for i, signal in enumerate(signals):
            # Applicazione filtro passa-basso
            filtered_signal = self.signal_processor.apply_lowpass_filter(
                signal, highcut=40.0, sampling_freq=self.sampling_frequency
            )
            
            # Conversione in millivolt
            unit = units[i]
            conversion_factor = millivolts_conversion.get(unit, 1.0)
            signals[i] = filtered_signal / conversion_factor
        
        return signals
    
    def get_patient_info(self) -> Dict[str, str]:
        """Estrae le informazioni del paziente dal DICOM"""
        info = {}
        
        # Nome paziente
        try:
            parts = str(self.dicom.PatientName).split('^')
            surname = parts[0] if parts else ''
            firstname = parts[1].title() if len(parts) > 1 else ''
            info['name'] = f"{surname} {firstname}".strip()
        except (AttributeError, IndexError):
            info['name'] = ''
        
        # Altre informazioni
        info['id'] = str(self.dicom.get('PatientID', ''))
        info['sex'] = str(self.dicom.get('PatientSex', ''))
        info['age'] = str(self.dicom.get('PatientAge', '')).strip('Y')
        
        # Data di nascita
        try:
            birth_date = datetime.strptime(
                self.dicom.PatientBirthDate, '%Y%m%d'
            ).strftime("%e %b %Y")
            info['birth_date'] = birth_date
        except (ValueError, AttributeError):
            info['birth_date'] = ''
        
        # Data acquisizione
        try:
            # Rimozione microsecondi
            acquisition_dt = re.sub(r'\.\d+$', '', self.dicom.AcquisitionDateTime)
            acquisition_date = datetime.strptime(
                acquisition_dt, '%Y%m%d%H%M%S'
            ).strftime('%d %b %Y %H:%M')
            info['acquisition_date'] = acquisition_date
        except (ValueError, AttributeError):
            info['acquisition_date'] = ''
        
        return info
    
    def get_ecg_measurements(self) -> Dict[str, str]:
        """Estrae le misurazioni ECG"""
        if not hasattr(self.dicom, 'WaveformAnnotationSequence'):
            return {}
        
        measurements = {}
        target_measurements = {
            'QT Interval', 'QTc Interval', 'RR Interval', 'VRate',
            'QRS Duration', 'QRS Axis', 'T Axis', 'P Axis', 'PR Interval'
        }
        
        for annotation in self.dicom.WaveformAnnotationSequence:
            if annotation.get('ConceptNameCodeSequence'):
                concept = annotation.ConceptNameCodeSequence[0]
                if concept.CodeMeaning in target_measurements:
                    measurements[concept.CodeMeaning] = str(annotation.NumericValue)
        
        # Calcolo frequenza ventricolare se non presente
        if 'VRate' not in measurements:
            try:
                rr_interval = float(measurements.get('RR Interval', 0))
                if rr_interval > 0:
                    vrate = 60.0 / self.duration * self.samples / rr_interval
                    measurements['VRate'] = f"{vrate:.1f}"
            except (ValueError, ZeroDivisionError):
                measurements['VRate'] = "(unknown)"
        
        return measurements
    
    def get_interpretation(self) -> str:
        """Restituisce l'interpretazione automatica dello studio"""
        if not hasattr(self.dicom, 'WaveformAnnotationSequence'):
            return ''
        
        interpretations = []
        for annotation in self.dicom.WaveformAnnotationSequence:
            if hasattr(annotation, 'UnformattedTextValue') and annotation.UnformattedTextValue:
                interpretations.append(annotation.UnformattedTextValue)
        
        return '\n'.join(interpretations)
    
    def plot_signals(self, layout_id: str, mm_mv: float = 10.0):
        """Plotta i segnali ECG"""
        if layout_id not in LAYOUT:
            raise ValueError(f"Layout {layout_id} non supportato")
        
        layout = LAYOUT[layout_id]
        rows = len(layout)
        
        for row_idx, row in enumerate(layout):
            columns = len(row)
            row_height = self.config.plot_height / rows
            
            # Spostamento orizzontale per etichette e separatori
            h_delta = self.samples / columns
            
            # Spostamento verticale dell'origine
            v_delta = round(
                self.config.plot_height * (1.0 - 1.0 / (rows * 2)) -
                row_idx * (self.config.plot_height / rows)
            )
            
            # Allineamento su multipli di 5mm
            v_delta = (v_delta + 2.5) - (v_delta + 2.5) % 5
            
            # Lunghezza di un chunk di segnale
            chunk_size = int(self.samples / len(row))
            
            for col_idx, signal_num in enumerate(row):
                left = col_idx * chunk_size
                right = (col_idx + 1) * chunk_size
                
                # Chunk del segnale, spostato verticalmente e scalato
                signal_chunk = v_delta + mm_mv * self.signals[signal_num][left:right]
                
                # Plot del segnale
                self.axis.plot(
                    list(range(left, right)),
                    signal_chunk,
                    clip_on=False,
                    linewidth=self.plotter.linewidths['signal'],
                    color=self.plotter.colors['signal'],
                    zorder=10
                )
                
                # Etichetta del canale
                channel_def = self.channel_definitions[signal_num]
                channel_source = channel_def.ChannelSourceSequence[0]
                label = channel_source.CodeMeaning.replace('Lead', '').replace('(Einthoven)', '')
                
                # Linea di riferimento
                h_pos = h_delta * col_idx
                v_pos = v_delta + row_height / 2.6
                
                plt.plot(
                    [h_pos, h_pos],
                    [v_pos - 3, v_pos],
                    linewidth=0.6,
                    color=self.plotter.colors['signal'],
                    zorder=50
                )
                
                # Testo etichetta
                self.axis.text(
                    h_pos + 40,
                    v_delta + row_height / 3,
                    label,
                    zorder=50,
                    fontsize=8
                )
    
    def add_info_text(self, interpretation: bool = False):
        """Aggiunge le informazioni testuali al plot"""
        patient_info = self.get_patient_info()
        measurements = self.get_ecg_measurements()
        
        # Informazioni paziente
        info_text = f"{patient_info['name']}\n"
        info_text += f"ID: {patient_info['id']}\n"
        info_text += f"Sesso: {patient_info['sex']}\n"
        info_text += f"Data nascita: {patient_info['birth_date']} ({patient_info['age']} anni)\n"
        info_text += f"Acquisizione: {patient_info['acquisition_date']}"
        
        plt.figtext(0.08, 0.87, info_text, fontsize=8)
        
        # Misurazioni ECG
        if measurements:
            vrate = measurements.get('VRate', '(unknown)')
            measurements_text = f"Freq. ventricolare: {vrate} BPM\n"
            measurements_text += f"PR: {measurements.get('PR Interval', '')} ms\n"
            measurements_text += f"QRS: {measurements.get('QRS Duration', '')} ms\n"
            measurements_text += f"QT/QTc: {measurements.get('QT Interval', '')}/"
            measurements_text += f"{measurements.get('QTc Interval', '')} ms\n"
            measurements_text += f"Assi P/QRS/T: {measurements.get('P Axis', '')} "
            measurements_text += f"{measurements.get('QRS Axis', '')} {measurements.get('T Axis', '')}"
            
            plt.figtext(0.30, 0.87, measurements_text, fontsize=8)
        
        # Interpretazione
        if interpretation:
            interpretation_text = self.get_interpretation()
            plt.figtext(0.45, 0.87, interpretation_text, fontsize=8)
        
        # Informazioni tecniche
        tech_info = f"Durata: {self.duration:.2f} s Freq. campionamento: {self.sampling_frequency} Hz"
        plt.figtext(0.08, 0.025, tech_info, fontsize=8)
        
        # Istituzione
        institution = INSTITUTION or self.dicom.get('InstitutionName', '')
        plt.figtext(0.38, 0.025, str(institution), fontsize=8)
        
        # Parametri di visualizzazione
        display_info = f"{self.mm_s:.1f} mm/s 10 mm/mV 0.05-40 Hz"
        plt.figtext(0.76, 0.025, display_info, fontsize=8)
    
    def draw(self, layout_id: str = '3x4', mm_mv: float = 10.0, 
             minor_axis: bool = False, interpretation: bool = False):
        """Disegna l'ECG completo"""
        self.plotter.draw_grid(self.axis, minor_axis)
        self.plot_signals(layout_id, mm_mv)
        self.add_info_text(interpretation)
    
    def save(self, output_file: Optional[str] = None, 
             format: str = 'png') -> Optional[bytes]:
        """Salva il plot"""
        if output_file:
            plt.savefig(
                output_file,
                dpi=self.config.dpi,
                format=format,
                orientation='landscape',
                bbox_inches='tight'
            )
            logger.info(f"ECG salvato in {output_file}")
        else:
            buffer = io.BytesIO()
            plt.savefig(
                buffer,
                dpi=self.config.dpi,
                format=format,
                orientation='landscape',
                bbox_inches='tight'
            )
            return buffer.getvalue()
    
    @contextmanager
    def plot_context(self):
        """Context manager per la gestione delle figure matplotlib"""
        try:
            yield self
        finally:
            plt.close(self.fig)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        plt.close(self.fig)


# Esempio di utilizzo
if __name__ == "__main__":
    try:
        # Caricamento da file
        with ECG("sample_files/anonymous_ecg.dcm") as ecg:
            ecg.draw(layout_id='3x4', mm_mv=10.0, interpretation=True)
            ecg.save("output.pdf", format="pdf")
        
        # Caricamento da server WADO
        wado_params = {
            'stu': 'study_uid',
            'ser': 'series_uid', 
            'obj': 'object_uid'
        }
        
        with ECG(wado_params) as ecg:
            ecg.draw(layout_id='12x1', minor_axis=True)
            pdf_data = ecg.save(format='pdf')
            
    except ECGReadFileError as e:
        logger.error(f"Errore lettura ECG: {e}")
    except Exception as e:
        logger.error(f"Errore generico: {e}")
