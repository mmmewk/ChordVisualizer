from scipy.io import wavfile as wav
from scipy.fftpack import fft
import numpy as np
import matplotlib.pyplot as plt
from models.note import Note, ScaleNotes, Notes
from models.overtone_set import OvertoneSet
from models.progression import Chord
from models.frequency_range import FrequencyRange

class AudioFile(object):
  def __init__(self, file, max_frequency=2000):
    self.rate, data = wav.read(file)
    self.intensity = data[:]
    self.max_intensity = np.max(self.intensity)
    self.count = len(self.intensity)
    self.duration = float(self.count) / self.rate

    # x space in time
    self.xt = np.linspace(0, self.duration, self.count)
    self.time_step = self.xt[2] - self.xt[1]

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
    self.fft_out_d1 = np.gradient(self.fft_out)
    self.fft_out_d2 = np.gradient(self.fft_out_d1)

    self.peak_filters = []
    self.note_filters = []
    self.ranges = {}
    self.max_intensities = {}
    self.average_intensities = {}
    self.best_accuracies = {}

  def plot(self):
    plt.plot(self.xt, self.intensity)

  def plot_fft(self, overlay=None, n=20, accuracy=20):
    if overlay is None:
      plt.plot(self.xf, self.fft_out)
    else:
      note_ranges = overlay.overtone_ranges(n=n, accuracy=accuracy)
      self.plot_subset_fft(note_ranges, c='b')
      inverse_ranges = FrequencyRange.inverse(note_ranges)
      self.plot_subset_fft(inverse_ranges, c='r')

  def plot_subset_fft(self, ranges, c='k'):
    for frequency_range in ranges:
      start = self.get_index_of_frequency(frequency_range.start)
      start = np.max([0, start])
      end = self.get_index_of_frequency(frequency_range.end)
      end = np.min([self.fft_count, end + 1])
      intensities = list(self.fft_out[start:end])
      frequencies = list(self.xf[start:end])
      plt.plot(frequencies, intensities, c=c)

  def decompose(self, n=4, accuracy=30):
    if not hasattr(self, 'notes'):
      self.notes = []
    if not hasattr(self, 'frequency_ranges'):
      self.frequency_ranges = []
    
    self.note_integrals = {}
    self.note_counts = {}
    total_integral = 0
    all_notes = Note.range('E2', 'B5')

    self.total_integral = sum(self.fft_out)
    for note in all_notes:
      self.note_integrals[str(note)] = 0

      ranges = [*note.overtone_ranges(n, accuracy)]
      for chosen_note in self.notes:
        ranges = [*ranges, *chosen_note.overtone_ranges(n, accuracy)]
      ranges = FrequencyRange.simplify(ranges)
      
      for note_range in ranges:
        if note_range.start > self.fft_max:
          break
        start = self.get_index_of_frequency(note_range.start)
        start = np.max([0, start])
        end = self.get_index_of_frequency(note_range.end)
        end = np.min([self.fft_count, end])
        self.note_counts[str(note)] = end - start
        self.note_integrals[str(note)] += sum(list(self.fft_out[start:end]))

    for key in self.note_integrals:
      self.note_integrals[key] = (self.note_integrals[key] / self.total_integral) - (self.note_counts[key] / self.fft_count)
    
  def select_note(self, min_increase=0.2, n=4, accuracy=30):
    if not hasattr(self, 'notes'):
      self.notes = []
    if not hasattr(self, 'explained_percent'):
      self.explained_percent = 0
    if not hasattr(self, 'frequency_ranges'):
      self.frequency_ranges = []
    
    best_value = 0
    best_note = 'E2'
    for key in self.note_integrals:
      if self.note_integrals[key] > best_value:
        best_value = self.note_integrals[key]
        best_note = key

    value_increase = best_value - self.explained_percent
    if value_increase > min_increase:
      print(best_note)
      print(best_value)
      best_note = Note(best_note)
      self.notes.append(best_note)
      self.explained_percent = best_value
      return value_increase
    else:
      return 0

  def percent_match(self, progression, n=20, accuracy=30):
    cursor = 0
    integral = 0
    progression_integral = 0
    progression_count = 0
    for note_range in progression.overtone_ranges(n, accuracy):
      start = self.get_index_of_frequency(note_range.start)
      start = np.max([0, start])
      end = self.get_index_of_frequency(note_range.end)
      end = np.min([self.fft_count, end])
      progression_count += end - start
      integral1 = sum(list(self.fft_out[cursor:start])) * self.frequency_step
      integral2 = sum(list(self.fft_out[start:end])) * self.frequency_step
      integral += integral1 + integral2
      progression_integral += integral2
      cursor = end
    
    return (progression_integral / integral) - (progression_count / ( self.fft_count ))
  
  def set_note_axes(self):
    plt.grid(True, which='major', axis='x')
    plt.grid(True, linestyle='--', which='minor', axis='x')

    major_tick_notes = Note.range(Note('E2'), Note('E7'), step=12)
    minor_tick_notes = list(filter(lambda n: n.note != 'E', Note.range(Note('E2'), Note('E7'), step=1)))
    ax = plt.gca()

    ax.set_xticks(list(map(lambda n: n.frequency, minor_tick_notes)), minor=True)
    ax.set_xticklabels(list(map(str, minor_tick_notes)), fontsize=5, rotation=90, minor=True)

    ax.set_xticks(list(map(lambda n: n.frequency, major_tick_notes)), minor=False)
    ax.set_xticklabels(list(map(str, major_tick_notes)), fontsize=10, rotation=90, minor=False)

  def add_peak_filter(self, filt):
    self.peak_filters.append(filt)
    filt.set_parent(self)

  def add_note_filter(self, filt):
    self.note_filters.append(filt)
    filt.set_parent(self)

  def get_range_for(self, note):
    note = Note(note).clean_note()
    if not str(note) in self.ranges:
      start = self.get_index_of_frequency((note - .5).frequency)
      end = self.get_index_of_frequency((note + .5).frequency)
      self.ranges[str(note)] = range(start, end)

    return self.ranges[str(note)]

  def max_intensity_for(self, note):
    note = Note(note).clean_note()
    if not str(note) in self.max_intensities:
      self.max_intensities[str(note)] = np.max([self.fft_out[i] for i in self.get_range_for(note)])

    return self.max_intensities[str(note)]

  def average_intensity_for(self, note):
    note = Note(note).clean_note()
    if not str(note) in self.average_intensities:
      self.average_intensities[str(note)] = np.mean([self.fft_out[i] for i in self.get_range_for(note)])

    return self.average_intensities[str(note)]

  def best_accuracy_for(self, note):
    note = Note(note).clean_note()
    if not str(note) in self.best_accuracies:
      note_range = self.get_range_for(note)
      peaks_to_check = [index for index in self.peaks if index in note_range] 
      if len(peaks_to_check) == 0:
        self.best_accuracies[str(note)] = 50
      else:
        self.best_accuracies[str(note)] = np.min([np.abs(Note(self.xf[i]).accuracy) for i in peaks_to_check])

    return self.best_accuracies[str(note)]

  def find_peaks(self):
    self.peaks = []
    for index in range(len(self.xf)):
      # if all filters pass add point as peak
      if all(map(lambda f: f.is_valid(index), self.peak_filters)):
        self.peaks.append(index)
          
  def get_index_of_frequency(self, frequency):
    guess = int(np.round(frequency / self.frequency_step))
    guess = np.max([0, guess])
    guess = np.min([self.fft_count, guess])
    return guess

  # def find_overtone_sets(self, width=0.04, accuracy_weight=50, intensity_weight=2, intensity_threshold=0.4, accuracy_threshold=30, min_overtones=3):
  #   if not hasattr(self, 'peaks'):
  #     self.find_peaks()

  #   self.overtone_sets = []

  #   for index in self.peaks:
  #     intensity = self.fft_out[index]
  #     note = Note(self.xf[index])
  #     set_found = False

  #     for overtone_set in self.overtone_sets:
  #       if overtone_set.add_note(note, intensity):
  #         set_found = True

  #     if not set_found:
  #       self.overtone_sets.append(OvertoneSet(note, intensity, width=width, accuracy_weight=accuracy_weight, intensity_weight=intensity_weight))

  #   self.filter_overtone_sets(intensity_threshold=intensity_threshold, accuracy_threshold=accuracy_threshold, min_overtones=min_overtones)

  # def filter_overtone_sets(self, intensity_threshold=0.4, accuracy_threshold=30, min_overtones=3):
  #   sets_to_keep = []
  #   self.intensity_filtered_os = []
  #   self.accuracy_filtered_os = []
  #   self.count_filtered_os = []
  #   for overtone_set in self.overtone_sets:
  #     if overtone_set.max_intensity < intensity_threshold:
  #       self.intensity_filtered_os.append(overtone_set)
  #       continue
  #     if overtone_set.root.accuracy > accuracy_threshold:
  #       self.accuracy_filtered_os.append(overtone_set)
  #       continue
  #     if overtone_set.count < min_overtones:
  #       self.count_filtered_os.append(overtone_set)
  #       continue
  #     sets_to_keep.append(overtone_set)

  #   self.overtone_sets = sets_to_keep

   
  def find_notes(self):
    if not hasattr(self, 'peaks'):
      self.find_peaks()
    
    self.notes = []
    for index in self.peaks:
      if all(map(lambda f: f.is_valid(index), self.note_filters)):
        self.notes.append(Note(self.xf[index]))

    return self.notes

  def pitches(self):
    pitches = sorted(set([note.note for note in self.notes]))

    return list(map(Note, pitches))

  def guess_chord(self, n=20, accuracy=30):
    self.chord_matches = {}
    chords = Chord.all()
    best_chord = chords[0]
    best_match = self.percent_match(chords[0], n=n, accuracy=accuracy)
    self.chord_matches[chords[0].key + ' ' + chords[0].title] = best_match

    for chord in Chord.all():
      if chord.title == 'Major' or chord.title == 'Minor':
        match_value = self.percent_match(chord, n=n, accuracy=accuracy)
        self.chord_matches[chord.key + ' ' + chord.title] = match_value
        if match_value > best_match:
          best_match = match_value
          best_chord = chord

    self.explained_percent = best_match

    return best_chord

    

  def guess(self):
    pitches = self.notes
    if len(pitches) == 0:
      return 'White Noise'

    if len(pitches) == 1:
      return str(pitches[0])

    if len(pitches) == 2:
      if pitches[0] < pitches[1]:
        root = pitches[0]
        top = pitches[1]
      else:
        root = pitches[1]
        top = pitches[0]

      if root.note == top.note:
        return 'Octave'
        
      return root.scale_position_name(top)

    if len(pitches) > 2:
      return Chord.guess(pitches)

  def annotate_peaks(self):
    if not hasattr(self, 'peaks'):
      self.find_peaks()

    for index in self.peaks:
      intensity = self.fft_out[index]
      frequency = self.xf[index]
      note = Note(frequency)
      plt.text(frequency, intensity, str(note), fontsize=8, clip_on=True)

  def annotate_filtered_peaks(self):
    for filt in self.peak_filters:
      if len(filt.filtered) > 0:
        xf, intensity = list(zip(*[(self.xf[index], self.fft_out[index]) for index in filt.filtered]))
        plt.scatter(xf, intensity, marker='x', label=filt.name())

    plt.legend()

  def overtone_count(self, index, width=0.03):
    frequency = self.xf[index]
    count = 0
    found_ratios = []
    for overtone_index in self.peaks:
      overtone_frequency = self.xf[overtone_index]
      if (overtone_frequency / frequency) < 1:
        continue

      ratio = int(np.round(overtone_frequency / frequency))
      overtone_accuracy = (overtone_frequency / frequency) % 1
      overtone_accuracy = np.min([overtone_accuracy, 1 - overtone_accuracy])


      # exclude overtones that can't be differentiated from other notes
      if (ratio % 2 != 0) and (not ratio in found_ratios) and overtone_accuracy < width:
        count += 1
        found_ratios.append(ratio)

    return count

  def annotate_notes(self):
    if not hasattr(self, 'notes'):
      self.find_notes()

    for root in self.notes:
      # for overtone in overtone_set.overtones.values():
      color = root.unique_color()
      label = str(root)
      index = self.get_index_of_frequency(root.frequency)
      intensity = self.fft_out[index]
      plt.text(root.frequency, intensity, str(root), c=color,label=label)

  def annotate_filtered_notes(self):
    for filt in self.note_filters:
      if len(filt.filtered) > 0:
        xf, intensity = list(zip(*[(self.xf[index], self.fft_out[index]) for index in filt.filtered]))
        plt.scatter(xf, intensity, marker='x', label=filt.name())

    plt.legend()

  # def annotate_theoretical_overtone_positions(self):
  #   if not hasattr(self, 'overtone_sets'):
  #     self.find_overtone_sets()

  #   for overtone_set in self.overtone_sets:
  #     note = overtone_set.root
  #     color = note.unique_color()
  #     frequencies = [note.frequency]
  #     intensities = [0]
  #     n = 2
  #     frequency = note.frequency * n
  #     while frequency < 2000:
  #       frequencies.append(frequency)
  #       intensities.append(0)
  #       n += 1
  #       frequency = note.frequency * n

  #     plt.scatter(frequencies, intensities, marker='x', c=color, label=str(note))

  def add_title(self):
    title = self.guess()
    title += ' Notes: ' + ', '.join(list(map(str, self.notes)))

    plt.title(title, fontsize=8)