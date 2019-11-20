from models.overtone import Overtone
from models.note import Note
import numpy as np

class OvertoneSet(object):
  def __init__(self, note, intensity, width=0.03, accuracy_weight=50, intensity_weight=2):
    self.root = self.create_overtone(note, intensity)
    self.max_intensity = self.root.intensity
    self.overtones = {}
    self.overtones[str(note.octave)] = self.root
    self.count = 1
    self.width = width
    self.accuracy_weight = accuracy_weight
    self.intensity_weight = intensity_weight

  def create_overtone(self, note, intensity):
    return Overtone(note, intensity, self.get_accuracy(note))

  # how close is this note to an exact multiple of the root
  def get_accuracy(self, note):
    if not hasattr(self, 'root'):
      return 0

    note = Note(note)
    accuracy = (note / self.root) % 1

    return np.min([accuracy, 1 - accuracy])

  def match(self, note):
    if (note.octave <= self.root.octave):
      return False

    return self.get_accuracy(note) < self.width
  
  def has_octave(self, octave):
    return str(octave) in self.overtones

  def can_overwrite(self, note, intensity):
    if self.has_octave(note.octave):
      curr_overtone = self.overtones[str(note.octave)]
      new_overtone = self.create_overtone(note, intensity)
      intensity_diff = (new_overtone.intensity - curr_overtone.intensity) * self.intensity_weight
      accuracy_diff = (curr_overtone.group_accuracy - new_overtone.group_accuracy) * self.accuracy_weight
      return (intensity_diff + accuracy_diff) > 0
    else:
      return True

  def add_note(self, note, intensity):
    if (self.match(note) and self.can_overwrite(note, intensity)):
      if not self.has_octave(note.octave):
        self.count += 1

      self.overtones[str(note.octave)] = self.create_overtone(note, intensity)
      if intensity > self.max_intensity:
        self.max_intensity = intensity
        
      return True

    return False