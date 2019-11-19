from models.note import Note

class Fret(Note):
  def __init__(self, string, fret_number):
    Note.__init__(self, string.root + fret_number)
    self.string = string
    self.ypos = string.index + 1
    self.xpos = string.get_fret_position(fret_number + 0.5)