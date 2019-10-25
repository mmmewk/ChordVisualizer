from constants import * 
import numpy as np

def getNoteFromNote(rootNote, halfsteps):
    startIndex = Notes.index(rootNote)
    endIndex = (startIndex + halfsteps) % 12
    return Notes[endIndex]

def getForwardDistance(noteA, noteB):
    indexA = Notes.index(noteA)
    indexB = Notes.index(noteB)
    if (indexB < indexA):
        indexB = indexB + 12
    
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

def findNote(string, note):
    root = Strings[string]
    return getForwardDistance(root, note)

def findHighNote(string, note):
    return findNote(string, note) + 12

def getInstancesOfNote(note):
    stringPositions = []
    fretPositions = []
    for string in range(0, 6):
        lowPosition = findNote(string, note)
        highPosition = findHighNote(string, note)
        stringPositions.append(string + 1)
        fretPositions.append(lowPosition)
        stringPositions.append(string + 1 )
        fretPositions.append(highPosition)

    return [fretPositions, stringPositions]
