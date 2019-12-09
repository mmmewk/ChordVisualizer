from audio import *
from models.instrument import *
from models.progression import *
from models.note import *
from models.audio_file import *
import matplotlib.pyplot as plt
import sys


if __name__ == '__main__':
  plt.figure(figsize=(20,9))
  plt.show(block=False)
  
  while True:
    record('tuner.wav', 1)
    audio_file = AudioFile('tuner.wav')
    audio_file.decompose()
    audio_file.select_note()

    plt.clf()
    if len(audio_file.notes) > 0:
      note = audio_file.notes[0]
      audio_file.plot_fft(overlay=note)
      plt.title(str(note))
    else:
      audio_file.plot_fft()

    audio_file.set_note_axes()
    plt.gca().set_xlim(Note('D#2').frequency, Note('B5').frequency)
    plt.draw()
    plt.pause(0.01)