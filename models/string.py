import numpy as np
from models.note import Note, Octave
from models.fret import Fret

class String(object):
  def __init__(self, data, max_fret=18, index=0):
    if isinstance(data, String):
      self.root = data.root
    else:
      self.root = Note(data)
    
    self.max_fret = max_fret
    self.index = index

  def get_fret_position(self, fret):
    return 1.0 - ( 1.0 / Note.frequency_multiplier(fret) )

  def get_fret(self, fret_number):
    return Fret(self, fret_number)

  def find_note(self, note, octaves=True):
    note = Note(note)
    instances = []
    if octaves:
      halfsteps = int(np.round(Note.get_forward_distance(self.root, note, metric='halfsteps')))

      while halfsteps <= self.max_fret:
        instances.append(self.get_fret(halfsteps))
        halfsteps += Octave

    else:
      halfsteps = int(np.round(Note.get_distance(self.root, note, metric='halfsteps')))
      if halfsteps >= 0 and halfsteps <= self.max_fret:
        instances.append(self.get_fret(halfsteps))

    return instances

  def play(self, time=1, fret=0):
    Fret(self, fret).play(time=time)

  def __str__(self):
    return str(self.root)