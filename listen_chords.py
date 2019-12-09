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
    record('tuner.wav', 2)
    audio_file = AudioFile('tuner.wav')
    if audio_file.max_intensity < 1.3e8:
      plt.pause(0.1)
      continue

    chord = audio_file.guess_chord(n=4)
    
    if audio_file.explained_percent > -0.15:
      old_title = plt.gca().get_title()
      plt.clf()
      audio_file.plot_fft(overlay=chord)
      plt.title(str(chord.name) + str(list(map(str, chord.notes))))
      audio_file.set_note_axes()
      plt.gca().set_xlim(Note('D#2').frequency, Note('B5').frequency)
      plt.draw()

    plt.pause(0.01)