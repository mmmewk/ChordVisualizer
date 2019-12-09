from models.audio_file import AudioFile
from models.filter import *
from models.progression import *
import matplotlib.pyplot as plt

if __name__ == "__main__":
  chords_to_plot = ['A','B','C','E','F','G']
  chord_types = ['Major', 'Minor']
  
  for index, chord_type in enumerate(chord_types):
    plt.figure(index, figsize=(20,9))
    for index, chord in enumerate(chords_to_plot):
      plt.subplot('23%d' % (index + 1))

      # load file
      audio_file = AudioFile('GuitarChords/%s%s.wav' % (chord, chord_type))
      accuracy = 30
      n = 8
      audio_file.decompose(n=n, accuracy=accuracy)
      while(audio_file.select_note(min_increase=0.05, n=n, accuracy=accuracy) > 0):
        audio_file.decompose(n=n, accuracy=accuracy)
      
      best_chord = audio_file.guess()
      
      audio_file.plot_fft()
      audio_file.set_note_axes()
      plt.gca().set_xlim(Note('D#2').frequency, Note('B4').frequency)
      plt.title(str(best_chord))
  
  plt.show()