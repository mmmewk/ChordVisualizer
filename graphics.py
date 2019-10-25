from helpers import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm

colors = ['r','g','b','y','k', 'c']
def getPhysicalPosition(fretPosition):
    return 1.0 - ( 1.0 / (np.power(2.0, fretPosition / 12.0)) )

def setAxes():
    fig = plt.figure(figsize=(20, 5))
    ax = fig.add_subplot(111)
    ax.set_yticks(range(1, 7))
    ax.set_yticklabels(Strings)
    ax.set_ylim(0, 7) # strings are 1 - 6

    frets = np.linspace(0, 24, 25)
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

    ax.set_xlim(0, 0.625)
    ax.grid(which = 'minor', alpha = 0)
    ax.grid(which = 'major', alpha = 1, color='k', linestyle='-', linewidth=2)

    gridlines = ax.get_xgridlines()
    firstLine = gridlines[1]
    firstLine.set_color('red')

def drawNote(note, color, label):
    [Fret, String] = getInstancesOfNote(note)
    halfFrets = map(lambda f: f + 0.5, Fret)
    X = map(getPhysicalPosition, halfFrets)
    plt.scatter(X, String, s=100, c=color, label=label)

def getLabel(rootNote, note):
    index = getForwardDistance(rootNote, note)
    return note.ljust(2) + " " + ScaleNotes[index]

def drawChord(rootNote, progression, name):
    setAxes()
    notes = getProgression(rootNote, progression)
    colors = cm.hsv(np.linspace(0, 1, len(notes) + 1))
    for note, color in zip(notes, colors):
        label = getLabel(rootNote, note)
        drawNote(note, color, label)
    
    plt.title(rootNote + " " + name)
    plt.legend()
    plt.show(block=False)