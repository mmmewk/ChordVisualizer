import numpy as np
from numbers import Number
import re
from audio import play
from matplotlib.colors import hsv_to_rgb
from models.frequency_range import FrequencyRange

Notes               = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ScaleNotes          = ['1', '2b', '2', '3b', '3', '4', '5b', '5', '6b', '6', '7b', '7', '8']
ScaleNoteNames      = ['Root', 'Minor Second', 'Second', 'Minor Third', 'Third', 'Fourth', 'Minor Fifth', 'Fifth', 'Minor Sixth', 'Sixth', 'Minor Seventh', 'Seventh', 'Octave']
Octave              = 12
A4                   = 440.0
C4                   = 261.626
C1                   = 32.70325
B0                   = 30.86775

class Note(object):
  def __init__(self, data):
    if isinstance(data, Note):
      self.frequency = data.frequency
      self.note = data.note
      self.octave = data.octave
      self.accuracy = data.accuracy
      self.clean_frequency = data.clean_frequency
    elif isinstance(data, Number):
      self.frequency = data
      if self.frequency < B0:
        self.set_defaults()
      else:
        clean_note = Note.guess(self.frequency)
        self.note = clean_note.note
        self.octave = clean_note.octave
        self.accuracy = Note.get_distance(clean_note, self.frequency)
        self.clean_frequency = clean_note.frequency
    else:
      matches = re.search(r'([a-gA-G]#?)([0-9]+)?\+?([\-0-9\.]+)?', data)
      self.note = matches.group(1).upper() if matches.group(1) else 'A'
      self.octave = int(matches.group(2)) if matches.group(2) else 4
      if self.octave < 1:
        self.set_defaults()
        self.frequency = B0
      else:
        self.accuracy = float(matches.group(3)) if matches.group(3) else 0.0
        self.clean_frequency = Note.get_frequency(self.note, self.octave)
        self.frequency = self.clean_frequency * Note.frequency_multiplier(self.accuracy / 100)

  # if frequency is less than c1 just assume it isn't a real note
  def set_defaults(self):
    self.note = 'B'
    self.octave = 0
    self.accuracy = 50
    self.clean_frequency = C1

  def clean_note(self):
    return Note(self.clean_frequency)

  @staticmethod
  def range(start, end, step=1):
    notes = []
    end = Note(end)
    note = Note(start)
    while note.frequency < end.frequency:
      notes.append(note)
      note = note + step

    return notes

  @staticmethod
  def frequency_multiplier(halfsteps):
    return np.power(2.0, (halfsteps / float(Octave)))

  @staticmethod
  def get_frequency(note, octave):
    halfsteps = Octave * (octave - 4) + Notes.index(note.upper())
    return C4 * Note.frequency_multiplier(halfsteps)

  @staticmethod
  def guess(frequency):
    halfsteps = int(np.round(Note.get_distance(C4, frequency, metric='halfsteps')))
    pos_in_scale = halfsteps % Octave
    octave = int(np.floor(halfsteps / Octave)) + 4
    return Note(Notes[pos_in_scale] + str(octave))

  @staticmethod
  def get_distance(root_note, other_note, metric='cents'):
    ratio = float(other_note) / float(root_note)

    if metric == 'ratio':
      return ratio
    
    d_octave = np.log2(ratio)
    if metric == 'octaves':
        return d_octave 
        
    d_halfstep = d_octave * 12
    if metric == 'halfsteps':
        return d_halfstep 
        
    d_cents = d_halfstep * 100
    if metric == 'cents':
        return d_cents

  @staticmethod
  def get_forward_distance(root_note, forward_note, metric='cents'):
    root_note = Note(root_note)
    forward_note = Note(forward_note)
    forward_note.set_octave(root_note.octave)
    if (forward_note.frequency < root_note.frequency):
      forward_note.set_octave(forward_note.octave + 1)

    return Note.get_distance(root_note, forward_note, metric=metric)

  @staticmethod
  def get_scale_number(key, note):
    return ScaleNotes[int(np.round(Note.get_forward_distance(key, note, metric='halfsteps')))]

  def unique_color(self):
    cents = Note.get_forward_distance(C4, self)
    h = cents / 1200
    s = 1
    v = 1 - 1.0 / np.exp(self.octave / 2)
    return hsv_to_rgb((h,s,v))

  def set_octave(self, octave):
    self.octave = octave
    self.frequency = Note.get_frequency(self.note, self.octave)

  def note_at_distance(self, halfsteps):
    frequency = self.frequency * Note.frequency_multiplier(halfsteps)
    return Note(frequency)

  def scale_position(self, note):
    halfsteps = int(np.round(Note.get_forward_distance(self, Note(note), metric='halfsteps')))
    return ScaleNotes[halfsteps]

  def scale_position_name(self, note):
    halfsteps = int(np.round(Note.get_forward_distance(self, Note(note), metric='halfsteps')))
    return ScaleNoteNames[halfsteps]

  def overtones(self, n):
    overtones = []
    for multiplier in range(1, n + 1):
      overtones.append(Note(multiplier * self.frequency))

    return overtones

  def frequency_range(self, accuracy):
    start = (self - np.abs(accuracy / 100)).frequency
    end = (self + np.abs(accuracy / 100)).frequency
    return FrequencyRange(start, end)

  def overtone_ranges(self, n, accuracy):
    ranges = []
    for overtone in self.overtones(n):
      ranges.append(overtone.frequency_range(accuracy))

    return ranges

  def contains(self, frequency, n, accuracy):
    ranges = self.overtone_ranges(n, accuracy)
    return any(map(lambda r: r.contains(frequency), ranges))

  def play(self, time=1):
    play(self.frequency, time=time)
          
  def __gt__(self, o):
    return self.frequency > o

  def __ge__(self, o):
    return self.frequency >= o

  def __lt__(self, o):
    return self.frequency < o

  def __le__(self, o):
    return self.frequency <= o

  def __eq__(self, o):
    return self.frequency == o

  def __mul__(self, o):
    return o * self.frequency

  def __truediv__(self, other):
        return self.frequency / other

  def __rtruediv__(self, other):
      return other / self.frequency

  def __add__(self, o):
    if isinstance(o, Number):
      return self.note_at_distance(o)
    elif isinstance(o, Note):
      return Note(self.frequency + o.frequency)

  def __sub__(self, o):
    if isinstance(o, Number):
      return self.note_at_distance(-1 * o)
    elif isinstance(o, Note):
      return float(Note.get_distance(o, self))

  def __str__(self):
    string = self.note
    string += str(self.octave)
    if np.round(self.accuracy):
      string += '+' if self.accuracy > 0 else ''
      string += "%.0f" % self.accuracy

    return string

  def __float__(self):
    return float(self.frequency)