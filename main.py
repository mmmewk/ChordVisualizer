from models.audio_file import AudioFile
import matplotlib.pyplot as plt



if __name__ == "__main__":
  chords_to_plot = ['A','C','D','E','G']
  plt.figure(figsize=(20,10))
  for index, chord in enumerate(chords_to_plot):
    plt.subplot('23%d' % (index + 1))
    audio_file = AudioFile('GuitarChords/%sMajor.wav' % chord)
    audio_file.plotfft()
    audio_file.annotate_overtones()
    audio_file.add_title()
  
  plt.show()
