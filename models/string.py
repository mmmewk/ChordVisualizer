import numpy as np
from models.note import Note, Octave

class String(object):
  def __init__(self, data):
    if isinstance(data, String):
      self.root = data.root
    else:
      self.root = Note(data)

  def get_note_at_fret(self, fret):
    return self.root + fret

  def get_frequency_at_fret(self, fret):
    return self.get_note_at_fret(fret).frequency

  def get_fret_of_note(self, note):
    return int(np.round(Note.get_distance(self.root, Note(note), metric='halfsteps')))

  def get_instances_of(self, note, include_octaves=True, max_fret=18):
    instances = []
    distance = self.get_fret_of_note(note)
    
    if include_octaves:
      distance = distance % 12

      while distance < max_fret:
        instances.append(distance)
        distance += Octave
    elif distance >= 0 and distance < max_fret:
      instances.append(distance)

    return instances

  def get_first_instance_of(self, note):
    return self.get_fret_of_note(note) % 12

  def get_physical_position_of_note(self, note):
    fret = self.get_fret_of_note(note)
    return 1.0 - ( 1.0 / Note.frequency_multiplier(fret) )

  def play(self, time=1, fret=0):
    self.get_note_at_fret(fret).play(time=time)

  def __str__(self):
    return str(self.root)