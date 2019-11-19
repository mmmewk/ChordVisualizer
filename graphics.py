from helpers import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import r

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