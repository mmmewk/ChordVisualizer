from models.audio_file import AudioFile
from models.filter import *
from models.progression import *
import matplotlib.pyplot as plt

if __name__ == "__main__":
  chords_to_plot = ['A','B','C','E','F','G']
  chord_types = ['Major', 'Minor', '7']
  
  for chord_type in chord_types:
    plt.figure("%s Chords" % chord_type, figsize=(20,9))
    for index, chord in enumerate(chords_to_plot):
      plt.subplot('23%d' % (index + 1))

      # load file
      audio_file = AudioFile('GuitarChords/%s%s.wav' % (chord, chord_type))
      accuracy = 30
      n_overtones = 8

      best_chord = audio_file.guess_chord(n=8, accuracy=30)
      best_match = audio_file.chord_matches[best_chord.key + ' ' + best_chord.title]
      
      audio_file.plot_fft(overlay=best_chord, accuracy=accuracy, n=n_overtones)
      audio_file.set_note_axes()

      plt.gca().set_xlim(Note('D#2').frequency, Note('B4').frequency)
      notes = str(list(map(lambda n: n.note, Chord(chord, chord_type).notes)))
      plt.title("%s %s %s %.2f" % (str(best_chord.key), str(best_chord.title), notes, best_match))
  
  plt.show()

    # # add filters to find peaks
    # audio_file.add_peak_filter(FrequencyFilter(60, 2000)) # check frequency is within frequencies that a guitar could produce
    # audio_file.add_peak_filter(IntensityFilter(0.01))
    # audio_file.add_peak_filter(ModeFilter(2)) # check n points on either side to see if the point is the tallest
    # audio_file.add_peak_filter(RelativeHeightFilter(2.5))

    # audio_file.find_peaks()

    # audio_file.add_note_filter(FrequencyFilter(75, 700))
    # audio_file.add_note_filter(BestMatchFilter())
    # audio_file.add_note_filter(AccuracyFilter(25))
    # audio_file.add_note_filter(OvertoneCountFilter(3, 0.06))

    # audio_file.find_notes()
    
    # print(len(audio_file.notes))
    # audio_file.annotate_notes()
    # audio_file.annotate_filtered_peaks()
    # plt.title('%s Major' % chord)
    # audio_file.add_title()