from helpers import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import re

def setAxes():
    fig = plt.figure(figsize=(20, 5))
    ax = fig.add_subplot(111)
    ax.set_yticks(range(1, len(Strings) + 1))
    ax.set_yticklabels(Strings)
    ax.set_ylim(0, len(Strings) + 1)

    frets = np.linspace(0, HighestFret,HighestFret + 1)
    halfFrets = map(lambda f: f + 0.5, frets)
    majorPositions = map(getPhysicalPosition, frets)
    minorPositions = map(getPhysicalPosition, halfFrets)
    minLabels = map(lambda f: int(f), frets)
    majLabels = map(lambda f: '', frets)

    ax.set_xticklabels(minLabels, minor = True)
    ax.set_xticklabels(majLabels, minor = False)
    ax.tick_params(axis = 'x', which = 'minor', labelsize=20)

    ax.set_xticks(majorPositions)
    ax.set_xticks(minorPositions, minor = True)

    ax.set_xlim(0, getPhysicalPosition(HighestFret))
    ax.grid(which = 'minor', alpha = 0)
    ax.grid(axis = 'x', which = 'major', alpha = 1, color='k', linestyle='-', linewidth=2)
    ax.grid(axis = 'y', which = 'both', alpha = 0.7, color='brown', linestyle='-', linewidth=1)
    ax.set_axisbelow(True)
    gridlines = ax.get_xgridlines()
    firstLine = gridlines[1]
    firstLine.set_color('red')

    return ax

def drawNote(note, color='k', label=''):
    [Fret, String] = getInstancesOfNote(note)
    halfFrets = map(lambda f: f + 0.5, Fret)
    X = map(getPhysicalPosition, halfFrets)
    legendLabel = note + " " + label
    plt.scatter(X, String, s=300, linewidth=2, label=legendLabel, facecolors='white', edgecolors=color)
    for xpos, string in zip(X, String):
        plt.text(xpos, string, str(label), horizontalalignment='center', verticalalignment='center', fontsize=12)

def titleize(str):
    return re.sub(r'(.)([A-Z])', '\\1 \\2', str)

def drawProgression(rootNote, progression, progressionType, colors=None):
    setAxes()
    notes = getProgression(rootNote, progression)
    if colors is None:
        colors = rainbow(progression)
    
    for note, color in zip(notes, colors):
        label = getNoteNumber(rootNote, note)
        drawNote(note, color=color, label=str(label))

    plt.title(rootNote + " " + titleize(progressionType))
    plt.legend(loc='upper right')
    plt.show(block=False)


def colorRoot(progression):
    rootNote = progression[0]
    return map(lambda note: 'r' if rootNote == note else 'k', progression)

def rainbow(progression):
    return cm.hsv(np.linspace(0, 1, len(progression) + 1))

def drawChord(rootNote, name):
    progression = Chords[name]
    drawProgression(rootNote, progression, name + ' Chord', rainbow(progression))

def drawScale(rootNote, name):
    progression = Scales[name]
    drawProgression(rootNote, progression, name + ' Scale', colorRoot(progression))

def drawArpeggio(rootNote, name):
    progression = Arpeggios[name]
    drawProgression(rootNote, progression, name + ' Arpeggio', colorRoot(progression))