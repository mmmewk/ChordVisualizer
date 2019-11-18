import numpy as np
from numbers import Number
import re
from audio import play

Notes               = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ScaleNotes          = ['1', '2b', '2', '3b', '3', '4', '5b', '5', '6b', '6', '7b', '7', '8']
Octave              = 12
A4                   = 440.0
C4                   = 261.626

class Note(object):
  def __init__(self, data):
    if isinstance(data, Note):
      self.frequency = data.frequency
      self.clean_frequency = data.clean_frequency
      self.note = data.note
      self.octave = data.octave
      self.accuracy = data.accuracy
    elif isinstance(data, Number):
      self.frequency = data
      clean_note = Note.guess(self.frequency)
      self.clean_frequency = clean_note.frequency
      self.note = clean_note.note
      self.octave = clean_note.octave
      self.accuracy = Note.get_distance(self.frequency, clean_note)
    else:
      matches = re.search(r'([a-gA-G]#?)([0-9]+)?\+?([\-0-9\.]+)?', data)
      self.note = matches.group(1).upper() if matches.group(1) else 'A'
      self.octave = int(matches.group(2)) if matches.group(2) else 4
      self.accuracy = float(matches.group(3)) if matches.group(3) else 0.0
      self.clean_frequency = Note.get_frequency(self.note, self.octave)
      self.frequency = self.clean_frequency * Note.frequency_multiplier(self.accuracy / 100)

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
    forward_note.set_octave(root_note.octave)
    if (forward_note.frequency < root_note.frequency):
      forward_note.set_octave(forward_note.octave + 1)

    return Note.get_distance(root_note, forward_note, metric=metric)

  def set_octave(self, octave):
    self.octave = octave
    self.frequency = Note.get_frequency(self.note, self.octave)

  def note_at_distance(self, halfsteps):
    frequency = self.frequency * Note.frequency_multiplier(halfsteps)
    return Note(frequency)

  def scale_position(self, note):
    halfsteps = int(np.round(Note.get_forward_distance(self, Note(note), metric='halfsteps')))
    return ScaleNotes[halfsteps]

  def play(self, time=1):
    play(self.frequency, time=time)
          
  def __gt__(self, o):
    return self.frequency > o

  def __lt__(self, o):
    return self.frequency < o

  def __eq__(self, o):
    return self.frequency == o

  def __mul__(self, o):
    return o * self.frequency

  def __div__(self, o):
    return o / self.frequency

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