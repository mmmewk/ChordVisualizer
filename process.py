from audio import *
from graphics import setAxes
from time import sleep
import matplotlib.pyplot as plt
from scipy.io import wavfile as wav
from scipy.fftpack import fft
from scipy.signal import find_peaks_cwt
import numpy as np
import matplotlib.cm as cm

def parse(file):
    rate, data = wav.read(file)
    intensity = data[:]
    N = len(intensity)
    duration = float(N) / rate
    time = np.linspace(0, duration, N)

    data = {
             'rate': rate,
             'intensity': intensity,
             'time': time,
             'duration': duration,
             'N': N,
            }
    return data

def parsefft(file):
    data = parse(file)
    fftOut = getfft(data)
    N = data['N']
    # 30 is a random number to crop down the data to audible range
    xf = np.linspace(0.0, data['rate'] / 30, N // 30)

    notesToPlot = getCleanNotes(fftOut, xf)

    return data, fftOut, xf, notesToPlot

def plot(file):
    data = parse(file)
    plt.clf()
    plt.plot(data['time'], data['intensity'])
    plt.draw()
    plt.pause(0.001)

def createSampleData(frequencies = [440.0], duration = 1, noise = 100):
    rate = 44000.0
    time = np.linspace(0, duration, int(rate * duration))
    N = len(time)
    intensity = np.random.rand(len(time)) * noise
    for frequency in frequencies:
        intensity += np.cos(2 * np.pi * frequency * time)


    return {
             'rate': rate,
             'intensity': intensity,
             'time': time,
             'duration': duration,
             'N': N,
            }

def plotSampleData(frequencies = [440.0], duration=1, noise=100):
    data = createSampleData(frequencies, duration, noise)
    plt.figure(1)
    plt.plot(data['time'], data['intensity'])
    plt.show(block=False)
    plt.figure(2)
    plt.xlim(0, 1000)
    fftOut = fft(data['intensity'])
    N = data['N']
    xf = np.linspace(0.0, data['rate'] / 2, N // 2)
    plt.plot(xf, np.abs(fftOut[0:N//2]))
    plt.show(block=False)

def getfft(data):
    fftOut = fft(data['intensity'])
    fftOut = fftOut[0:data['N']//30]
    fftOut = np.abs(fftOut)
    return fftOut / np.max(fftOut)

def getCleanNotes(data, xf, threshold=0.2, width=0.7, maxFrequency=800, centsThreshold=20):
    maximaIndexes = find_peaks_cwt(data, np.array([width]))
    
    cleanNotes = {}
    for index in maximaIndexes:
        frequency = xf[index]
        intensity = data[index]
        if (intensity > threshold) and (maxFrequency > frequency):
            halfstepsAbsolute = getDistanceFromA4(frequency)
            halfsteps = int(np.round(halfstepsAbsolute))
            centsOff = (halfstepsAbsolute - halfsteps) * 100

            if np.abs(centsOff) < centsThreshold and (halfsteps not in cleanNotes or intensity > cleanNotes[halfsteps]['intensity']):
                cleanNotes[halfsteps] = {
                    'frequency': frequency,
                    'intensity': intensity,
                    'note': getNoteFromNote('A', halfsteps),
                    'accuracy': centsOff,
                }
    
    return cleanNotes

def addTitle(notesToPlot):
    notesForTitle = np.array([])
    for halfsteps, noteData in notesToPlot.items():
        notesForTitle = np.append(notesForTitle, noteData['note'])
        plt.text(noteData['frequency'], noteData['intensity'], noteData['note'] + " " + str(np.round(noteData['accuracy'])))

    uniqueNotesForTitle = np.unique(notesForTitle)

    if len(uniqueNotesForTitle) >= 3:
        plt.title(guessChord(uniqueNotesForTitle) + ', ' + ', '.join(uniqueNotesForTitle))
    else: 
        plt.title(', '.join(uniqueNotesForTitle))

def plotfft(data, fftOut, xf, notesToPlot):
    plt.xlim(0, 1000)
    plt.grid()
    plt.plot(xf, fftOut)

def drawNotes(data, fftOut, xf, notesToPlot):
    colors = cm.hsv(np.linspace(0,1,12))
    for halfsteps, noteData in notesToPlot.items():
        X = []
        Y = []
        cleanFrequency = str(np.round(frequencyMultiplier(halfsteps) * A4))
        accuracy = str(np.round(noteData['accuracy']))
        legendLabel = noteData['note'] + cleanFrequency  + ' + ' + accuracy
        color = colors[halfsteps % 12]
        for string in range(0, len(Strings)):
            baseFrequency = getFrequencyOfString(string)
            multiplier = noteData['frequency'] / baseFrequency
            fretPosition = np.round(np.log2(multiplier) * 12)
            if fretPosition >= 0 and fretPosition < 18:
                xpos = getPhysicalPosition(fretPosition + 0.5)
                X.append(xpos)
                Y.append(string + 1)
                plt.text(xpos, string + 1, noteData['note'], horizontalalignment='center', verticalalignment='center', fontsize=12)

        plt.scatter(X, Y, s=300, linewidth=2, label=legendLabel, facecolors='white', edgecolors=color)
    
    plt.legend(loc='upper right')


def listenfft(duration=3, wait=3):
    plt.show(block=False)
    while True:
        record('test.wav', duration)
        data, fftOut, xf, notesToPlot = parsefft('test.wav')
        plt.clf()
        plotfft(data, fftOut, xf, notesToPlot)
        addTitle(notesToPlot)
        plt.draw()
        sleep(wait)

def listenDisplay(duration=3, wait=3):
    setAxes()
    plt.show(block=False)
    while True:
        record('test.wav', duration)
        data, fftOut, xf, notesToPlot = parsefft('test.wav')
        plt.clf()
        setAxes(False)
        drawNotes(data, fftOut, xf, notesToPlot)
        addTitle(notesToPlot)
        plt.draw()
        sleep(wait)

def listen(duration=3, wait=3):
    fig = plt.figure(figsize=(20, 6))
    plt.show(block=False)
    while True:
        record('test.wav', duration)
        data, fftOut, xf, notesToPlot = parsefft('test.wav')
        plt.clf()
        plt.subplot(211)
        addTitle(notesToPlot)
        plotfft(data, fftOut, xf, notesToPlot)
        plt.draw()
        plt.subplot(212)
        setAxes(False)
        drawNotes(data, fftOut, xf, notesToPlot)
        plt.draw()
        plt.pause(0.1)
        sleep(wait)

