from models.audio_file import AudioFile
import matplotlib.pyplot as plt
from models.filter import *

if __name__ == "__main__":
  strings_to_plot = ['lowE82', 'A110','D146', 'G196', 'B246','highE329']
  plt.figure(figsize=(20,9))
  for index, string in enumerate(strings_to_plot):
    plt.subplot('23%d' % (index + 1))
    audio_file = AudioFile('GuitarStrings/%s.wav' % string)
    
    audio_file.decompose(n=4)
    audio_file.select_note(n=4, min_increase=0)
    note = audio_file.notes[0]

    audio_file.plot_fft(overlay=note, accuracy=30)
    audio_file.set_note_axes()
    # audio_file.annotate_notes()
    plt.gca().set_xlim(Note('D#2').frequency, Note('B5').frequency)
    plt.title(str(note) + ' ' + str(audio_file.percent_match(note, accuracy=30)))
    # audio_file.add_title()
  
  plt.show()

    # add filters to find peaks
    # audio_file.add_peak_filter(FrequencyFilter(60, 2000)) # check frequency is within frequencies that a guitar could produce
    # audio_file.add_peak_filter(IntensityFilter(0.01))
    # audio_file.add_peak_filter(ModeFilter(2)) # check n points on either side to see if the point is the tallest
    # audio_file.add_peak_filter(RelativeHeightFilter(2.5))
    
    # audio_file.find_peaks()


    # audio_file.add_note_filter(FrequencyFilter(75, 700))
    # audio_file.add_note_filter(BestMatchFilter())
    # audio_file.add_note_filter(AccuracyFilter(25))
    # audio_file.add_note_filter(OvertoneCountFilter(3, 0.03))

    # audio_file.find_notes()