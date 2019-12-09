from models.audio_file import AudioFile
import matplotlib.pyplot as plt
from models.filter import *
from audio import *
from models.instrument import *

if __name__ == "__main__":
  record('test.wav', 1)
  plt.figure(figsize=(20,9))
  audio_file = AudioFile('test.wav')

  # add filters to find peaks
  audio_file.add_peak_filter(FrequencyFilter(60, 2000)) # check frequency is within frequencies that a guitar could produce
  audio_file.add_peak_filter(IntensityFilter(0.1))
  audio_file.add_peak_filter(ModeFilter(2)) # check n points on either side to see if the point is the tallest
  audio_file.add_peak_filter(RelativeHeightFilter(2))

  audio_file.find_peaks()

  audio_file.add_note_filter(FrequencyFilter(75, 700))
  audio_file.add_note_filter(BestMatchFilter())
  audio_file.add_note_filter(AccuracyFilter(30))
  # audio_file.add_note_filter(OvertoneCountFilter(2, 0.06))

  audio_file.find_notes()
  
  print(len(audio_file.notes))
  plt.subplot(211)
  audio_file.plot_fft()
  audio_file.set_note_axes()
  audio_file.annotate_notes()
  audio_file.annotate_filtered_peaks()
  plt.gca().set_xlim(Note('D#2').frequency, Note('B6').frequency)
  audio_file.add_title()

  plt.subplot(212)
  guitar = Guitar()
  guitar.draw()
  for note in audio_file.notes:
    guitar.draw_note(note, octaves=False)
  
  
  plt.show()