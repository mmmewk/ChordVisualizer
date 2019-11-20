from models.string import String
from models.note import Note
from audio import play_multiple
import os
import matplotlib.pyplot as plt
import numpy as np

class Instrument(object):
  tunings = {}
  def __init__(self, tuning='standard', max_fret=18):
    self.name = 'instrument'
    self.tuning = tuning
    self.max_fret = max_fret
    self.strings = list(map(lambda s: String(s[1], max_fret=max_fret, index=s[0]), enumerate(self.tunings[self.tuning])))

  def tune(self, tuning):
    self.__init__(self, tuning)

  def get_frets(self, fret_positions):
    frets = []
    for index, fret in enumerate(fret_positions):
      string = self.strings[index]
      frets.append(string.get_fret(fret))
    
    return frets

  def find_note(self, note, octaves=True):
    instances = []
    for string in self.strings:
      instances += string.find_note(note, octaves=octaves)

    return instances

  def play(self, pos, time=1):
    frets = self.get_frets(pos)
    play_multiple(frets, time=time)

  def strum(self, pos, time=1, dir='down', delay=0.05):
    frets = self.get_frets(pos)
    if dir == 'up':
      frets.reverse()

    play_multiple(frets, delay=delay, time=time)

  def draw(self):
    fig = plt.gcf()
    ax = plt.gca()

    ax.set_yticks(range(1, len(self.strings) + 1))
    ax.set_yticklabels(self.strings)
    ax.set_ylim(0, len(self.strings) + 1)

    frets = np.linspace(0, self.max_fret, self.max_fret + 1)
    halfFrets = list(map(lambda f: f + 0.5, frets))

    majorPositions = list(map(self.strings[0].get_fret_position, frets))
    minorPositions = list(map(self.strings[0].get_fret_position, halfFrets))
    minLabels = list(map(lambda f: int(f), frets))
    majLabels = list(map(lambda f: '', frets))

    ax.set_xticklabels(minLabels, minor = True)
    ax.set_xticklabels(majLabels, minor = False)
    ax.tick_params(axis = 'x', which = 'minor', labelsize=20)

    ax.set_xticks(majorPositions)
    ax.set_xticks(minorPositions, minor = True)

    ax.set_xlim(0, self.strings[0].get_fret_position(self.max_fret + 4))
    ax.grid(which = 'minor', alpha = 0)
    ax.grid(axis = 'x', which = 'major', alpha = 1, color='k', linestyle='-', linewidth=2)
    ax.grid(axis = 'y', which = 'both', alpha = 0.7, color='brown', linestyle='-', linewidth=1)
    ax.set_axisbelow(True)
    gridlines = ax.get_xgridlines()
    firstLine = gridlines[1]
    firstLine.set_color('red')

  def draw_note(self, note, labelfunc=str, octaves=True, color='k'):
    note = Note(note)
    frets = self.find_note(note, octaves=octaves)
    if octaves:
      accuracy = int(np.round(note.accuracy))
      if accuracy > 0:
        label = "%s + %.0f" % (note.note, accuracy)
      elif accuracy < 0:
        label = "%s %.0f" % (note.note, accuracy)
      else:
        label = note.note

    else:
      label = str(note)

    X = []
    Y = []
    for fret in frets:
      plt.text(fret.xpos, fret.ypos, labelfunc(fret), horizontalalignment='center', verticalalignment='center', fontsize=12)
      X.append(fret.xpos)
      Y.append(fret.ypos)

    plt.scatter(X, Y, s=300, linewidth=2, label=label, facecolors='white', edgecolors=color)

  def draw_progression(self, progression, colorfunc=None):
    if colorfunc is None:
      colorfunc = lambda note: 'r' if note.note == progression.root.note else 'k'

    for note in progression.notes:
      labelfunc = lambda n: progression.get_scale_number(note)
      self.draw_note(note, labelfunc=labelfunc, color=colorfunc(note))

  def draw_chord(self, chord):
    colorfunc = lambda n: n.unique_color()
    self.draw_progression(chord, colorfunc=colorfunc)

  def __str__(self):
    return self.name.title() + ' tuning:' + self.tuning.title() + ' strings:' +','.join(map(str, self.strings))

class Guitar(Instrument):
  tunings = {
    'standard'        : ['E2', 'A2', 'D3', 'G3', 'B3', 'E4'],
    'drop-d'          : ['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],
    'double-drop-d'   : ['D2', 'A2', 'D3', 'G3', 'B3', 'D4'],
    'open-g'          : ['D2', 'G2', 'D3', 'G3', 'B3', 'D4'],
    'open-d'          : ['D2', 'A2', 'D3', 'F#3', 'A3', 'D4'],
    'open-e'          : ['E2', 'B2', 'E3', 'G3', 'B3', 'E4'],
    'open-a'          : ['E2', 'A2', 'E3', 'A3', 'C#4', 'E4'],
  }

  def __init__(self, name='guitar'):
    Instrument.__init__(self)
    self.name = name

class Ukulele(Instrument):
  tunings = {
    'standard' : ['G4', 'C4', 'E4', 'A4'],
  }

  def __init__(self, name='ukulele'):
    Instrument.__init__(self)
    self.name = name

class Bass(Instrument):
  tunings = {
    'standard'        : ['E1', 'A1', 'D2', 'G2'],
  }

  def __init__(self, name='bass'):
    Instrument.__init__(self)
    self.name = name
