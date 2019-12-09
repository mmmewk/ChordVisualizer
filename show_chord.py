from models.instrument import *
from models.progression import *
from models.note import *
import matplotlib.pyplot as plt
import sys

if __name__ == '__main__':
  chord = Chord(sys.argv[1], sys.argv[2])
  plt.figure(chord.name, figsize=(20,9))
  guitar = Guitar()
  guitar.draw()
  guitar.draw_chord(chord)

  plt.show()