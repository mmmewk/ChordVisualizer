import os
from multiprocessing import Process
from helpers import *

def play(frequency, time):
    os.system('play -n synth ' + str(time) + ' sin ' + str(frequency))

def playMultiple(frequencies, time):
    command = 'play -n synth ' + str(time)
    for frequency in frequencies:
        command += ' sin ' + str(frequency)
    
    os.system(command)

def playRawChord(rootNote='A', chordType='Major', time=1):
    progression = Chords[chordType]
    notes = getProgression(rootNote, progression)
    frequencies = map(lambda note: getFrequencyOfNote(note, 4), notes)
    playMultiple(frequencies, time)

def record(outputFile, time):
    os.system('rec -c 1 ' + str(outputFile) + ' trim 0 ' + str(time))

def playFile(inputFile, time=None):
    command = 'play ' + str(inputFile)
    if bool(time):
        command = command + ' trim 0 ' + str(time)
    os.system(command)