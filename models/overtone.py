from models.note import Note

class Overtone(Note):
  def __init__(self, data, intensity, group_accuracy):
    Note.__init__(self, data)
    self.intensity = intensity
    self.group_accuracy = group_accuracy