from models.instrument import *
from models.progression import *
from models.note import *
from models.audio_file import *
import matplotlib.pyplot as plt
import sys

if __name__ == '__main__':
  audio_file = AudioFile(sys.argv[1])
  plt.figure(figsize=(20,9))
  audio_file.plot_fft()
  audio_file.set_note_axes()
  plt.gca().set_xlim(Note('D#2').frequency, Note('B4').frequency)


  plt.show()