from constants import * 
from config import *
import numpy as np

def getFrequencyOfNote(note, octave=4):
    halfsteps = getForwardDistance('A', note)
    octaveShift = Octave * (octave - 4)
    return A4 * frequencyMultiplier(halfsteps + octaveShift)

def getPhysicalPosition(fretPosition):
    return 1.0 - ( 1.0 / frequencyMultiplier(fretPosition) )

def frequencyMultiplier(halfsteps):
    return np.power(2.0, (halfsteps / float(Octave)))

def getFrequencyOfString(string):
    frequency = BaseFrequency
    note = Strings[0]
    for s in range(1, (string + 1)):
        halfsteps = getForwardDistance(note, Strings[s])
        frequency = frequency * frequencyMultiplier(halfsteps)
        note = Strings[s]
    
    return frequency

def getFrequencyOfFret(string, fret):
    stringFrequency = getFrequencyOfString(string)
    return stringFrequency * frequencyMultiplier(fret)

def getNoteFromNote(rootNote, halfsteps):
    startIndex = Notes.index(rootNote)
    endIndex = (startIndex + halfsteps) % Octave
    return Notes[endIndex]

def getForwardDistance(noteA, noteB):
    indexA = Notes.index(noteA)
    indexB = Notes.index(noteB)
    if (indexB < indexA):
        indexB = indexB + Octave
    
    return indexB - indexA

def getNoteFromString(string, fret):
    root = Strings[string]
    return getNoteFromNote(root, fret)

def getProgression(rootNote, notePositions):
    notes = []
    startIndex = Notes.index(rootNote)
    for note in notePositions:
        distanceFromRoot = ScaleNotes.index(note)
        notes.append(getNoteFromNote(rootNote, distanceFromRoot))
    
    return notes

def getChord(rootNote, chordType='Major'):
    return getProgression(rootNote, Chords[chordType])

def getScale(rootNote, scaleType='Major'):
    return getProgression(rootNote, Scales[scaleType])

def getArpeggio(rootNote, arpType='Major'):
    return getProgression(rootNote, Arpeggios[arpType])

def findNote(string, note):
    root = Strings[string]
    return getForwardDistance(root, note)

def getNoteNumber(rootNote, note):
    index = getForwardDistance(rootNote, note)
    return ScaleNotes[index]

def findHighNote(string, note):
    return findNote(string, note) + Octave

def getInstancesOfNote(note):
    stringPositions = []
    fretPositions = []
    for string in range(0, len(Strings)):
        lowPosition = findNote(string, note)
        highPosition = findHighNote(string, note)
        stringPositions.append(string + 1)
        fretPositions.append(lowPosition)
        if (highPosition < HighestFret):
            stringPositions.append(string + 1 )
            fretPositions.append(highPosition)

    return [fretPositions, stringPositions]

def getFrequencies(rootFrequency, progression):
    halfsteps = map(lambda note: ScaleNotes.index(note), progression)
    return map(lambda halfstep: rootFrequency * frequencyMultiplier(halfstep), halfsteps)

def getDistanceFromA4(frequency):
    multiplier = np.log2(frequency / A4)
    return int(np.round(multiplier * 12))

def getClosestNote(frequency):
    return getNoteFromNote('A', getDistanceFromA4(frequency))

def guessChord(notes):
    # try out each note as the root
    for root in notes:
        halfsteps = map(lambda note: getForwardDistance(root, note), notes)
        halfsteps.sort()
        progression = map(lambda halfstep: ScaleNotes[halfstep], halfsteps)
        for chordType, chordProgression in Chords.items():
            if chordProgression == progression:
                return root + ' ' + chordType
        
    return 'Unkown Chord'

def mode(list):
    return max(set(list), key = list.count)