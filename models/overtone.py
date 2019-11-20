from models.note import Note, C4
import numpy as np
from matplotlib.colors import hsv_to_rgb

class Overtone(Note):
  def __init__(self, data, intensity, group_accuracy):
    Note.__init__(self, data)
    self.intensity = intensity
    self.group_accuracy = group_accuracy

  def unique_color(self):
    cents = Note.get_forward_distance(C4, self)
    h = cents / 1200
    s = self.intensity
    v = 1 - 1.0 / np.exp(self.octave / 2)
    return hsv_to_rgb((h,s,v))