from models.string import String
from audio import play_multiple
import os
import multiprocessing as mp

class Instrument(object):
  tunings = {}
  def __init__(self, tuning='standard'):
    self.name = 'instrument'
    self.tuning = tuning
    self.strings = list(map(String, self.tunings[self.tuning]))

  def tune(self, tuning):
    self.__init__(self, tuning)

  def get_frequencies(self, pos):
    frequencies = []
    for string_index, fret in enumerate(pos):
      string = self.strings[string_index]
      frequency = string.get_frequency_at_fret(fret)
      frequencies.append(frequency)
    
    return frequencies

  def get_notes(self, pos):
    notes = []
    for string_index, fret in enumerate(pos):
      string = self.strings[string_index]
      frequency = string.get_note_at_fret(fret)
      notes.append(frequency)
    
    return notes

  def play(self, pos, time=1):
    play_multiple(self.get_frequencies(pos), time=time)

  def strum(self, pos, time=1, dir='down', delay=0.05):
    frequencies = self.get_frequencies(pos)
    if dir == 'up':
      frequencies.reverse()

    play_multiple(frequencies, delay=delay, time=time)

  def __str__(self):
    return self.name.title() + ' tuning:' + self.tuning.title() + ' strings:' +','.join(map(str, self.strings))

class Guitar(Instrument):
  tunings = {
    'standard'        : ['E2', 'A2', 'D3', 'G3', 'B3', 'E4'],
    'drop-d'          : ['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],
    'double-drop-d'   : ['D2', 'A2', 'D3', 'G3', 'B3', 'D4'],
    'open-g'          : ['D2', 'G2', 'D3', 'G3', 'B3', 'D4'],
    'open-d'          : ['D2', 'A2', 'D3', 'F#3', 'A3', 'D4'],
    'open-e'          : ['E2', 'B2', 'E3', 'G3', 'B3', 'E4'],
    'open-a'          : ['E2', 'A2', 'E3', 'A3', 'C#4', 'E4'],
  }

  def __init__(self, name='guitar'):
    Instrument.__init__(self)
    self.name = name

class Ukulele(Instrument):
  tunings = {
    'standard' : ['G4', 'C4', 'E4', 'A4'],
  }

  def __init__(self, name='ukulele'):
    Instrument.__init__(self)
    self.name = name

class Bass(Instrument):
  tunings = {
    'standard'        : ['E1', 'A1', 'D2', 'G2'],
  }

  def __init__(self, name='bass'):
    Instrument.__init__(self)
    self.name = name
