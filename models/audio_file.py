from scipy.io import wavfile as wav
from scipy.fftpack import fft
import numpy as np
import matplotlib.pyplot as plt
from models.note import Note
from models.overtone_set import OvertoneSet

class AudioFile(object):
  def __init__(self, file):
    self.rate, data = wav.read(file)
    self.intensity = data[:]
    self.count = len(self.intensity)
    self.duration = float(self.count) / self.rate

    # x space in time
    self.xt = np.linspace(0, self.duration, self.count)
    self.time_step = self.xt[2] - self.xt[1]

    self.fft_computed = False

  def compute_fft(self, max_frequency=2000):
    # crop data down to only frequencies we care about
    crop_fraction = int(self.rate / max_frequency)
    self.fft_count = self.count // crop_fraction
    self.fft_max = max_frequency

    # x space in frequency
    self.xf = np.linspace(0.0, self.rate / crop_fraction, self.fft_count)
    self.frequency_step = self.xf[2] - self.xf[1]
    fft_out = fft(self.intensity)
    fft_out = fft_out[0:self.fft_count]
    fft_out = np.abs(fft_out)
    self.fft_out = fft_out / np.max(fft_out)
    self.fft_computed = True

  def plot(self):
    plt.plot(self.xt, self.intensity)

  def plotfft(self):
    if self.fft_computed == False:
      self.compute_fft()

    plt.plot(self.xf, self.fft_out)

  def find_peaks(self, intensity_threshold=0, mode_width=20, prominence_threshold=2, prominence_width=40, accuracy_threshold=30, min_frequency=60):
    if self.fft_computed == False:
      self.compute_fft()
      
    self.peaks = []
    self.freq_filtered = []
    self.intensity_filtered = []
    self.accuracy_filtered = []
    self.prominence_filtered = []
    self.mode_filtered = []
    for index, frequency in enumerate(self.xf):
      if frequency < min_frequency:
        self.freq_filtered.append(index)
        continue
      if self.fft_out[index] < intensity_threshold:
        self.intensity_filtered.append(index)
        continue
      if frequency == 0 or np.abs(Note(frequency).accuracy) > accuracy_threshold:
        self.accuracy_filtered.append(index)
        continue
      if self.prominence(index, prominence_width) < prominence_threshold:
        self.prominence_filtered.append(index)
        continue
      if not self.is_mode(index, mode_width):
        self.mode_filtered.append(index)
        continue
      self.peaks.append(index)

  def get_index_of_frequency(self, frequency):
    return int(np.round(frequency / self.frequency_step))

  def get_edges_of_range(self, index, width):
    frequency = self.xf[index]
    start_frequency = (Note(frequency) - (width / 100)).frequency
    index_width = int((frequency - start_frequency) // self.frequency_step)
    return (np.max([0, index - index_width]), np.min([index + index_width, self.fft_count]))

  # width is in cents
  def prominence(self, index, width):
    start, end = self.get_edges_of_range(index, width)
    return self.fft_out[index] / np.mean(self.fft_out[start:end])

  def is_mode(self, index, width):
    start, end = self.get_edges_of_range(index, width)
    return np.max(self.fft_out[start:end]) == self.fft_out[index]

  def annotate_peaks(self):
    if not hasattr(self, 'peaks'):
      self.find_peaks()

    for index in self.peaks:
      intensity = self.fft_out[index]
      frequency = self.xf[index]
      note = Note(frequency)

      plt.text(frequency, intensity, str(note))

  def annotate_filtered(self, frequency=True, intensity=True, accuracy=True, prominence=True, mode=True):
    if len(self.freq_filtered) > 0:
      xf, intensity = list(zip(*[(self.xf[index], self.fft_out[index]) for index in self.freq_filtered]))
      plt.scatter(xf, intensity, marker='x', c='r', label='Frequency Filtered')
    if len(self.intensity_filtered) > 0:
      xf, intensity = list(zip(*[(self.xf[index], self.fft_out[index]) for index in self.intensity_filtered]))
      plt.scatter(xf, intensity, marker='x', c='g', label='Intensity Filtered')
    if len(self.accuracy_filtered) > 0:
      xf, intensity = list(zip(*[(self.xf[index], self.fft_out[index]) for index in self.accuracy_filtered]))
      plt.scatter(xf, intensity, marker='x', c='b', label='Accuracy Filtered')
    if len(self.prominence_filtered) > 0:
      xf, intensity = list(zip(*[(self.xf[index], self.fft_out[index]) for index in self.prominence_filtered]))
      plt.scatter(xf, intensity, marker='x', c='k', label='Prominence Filtered')
    if len(self.mode_filtered) > 0:
      xf, intensity = list(zip(*[(self.xf[index], self.fft_out[index]) for index in self.mode_filtered]))
      plt.scatter(xf, intensity, marker='x', c='y', label='Mode Filtered')
    plt.legend()