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
    fftOut = fftOut[0:data['N']//2]
    fftOut = np.abs(fftOut)
    return fftOut / np.max(fftOut)


def parsefft(file):
    maxFrequency = 2000
    data = parse(file)
    fftOut = getfft(data)
    N = data['N'] // (data['rate'] / maxFrequency)
    fftOut = fftOut[0:N]
    
    xf = np.linspace(0.0, maxFrequency, N)

    overtoneSets = getOvertoneSets(fftOut, xf)

    return data, fftOut, xf, overtoneSets


def createOvertoneSet(frequency, intensity):
    return {
                'baseFrequency': frequency,
                'maxIntensity': intensity,
                'frequencyCount': 1,
                'rootNote': getClosestNote(frequency),
                'accuracy': getAccuracy(frequency),
                'frequencies': [frequency],
                'intensities': [intensity],
                'notes': [getClosestNote(frequency)],
            }

def addFrequencyToOvertoneSet(overtoneData, frequency, intensity):
    frequencyFound = False
    # check if note is already part of the set
    for index, overtoneFrequency in enumerate(overtoneData['frequencies']):
        frequencyRatio = frequency / overtoneFrequency
        if np.max([frequencyRatio, 1/frequencyRatio]) < frequencyMultiplier(1):
            frequencyFound = True
            if intensity > overtoneData['intensities'][index]:
                overtoneData['frequencies'][index] = frequency
                overtoneData['intensities'][index] = intensity

    # otherwise add it
    if frequencyFound == False:
        overtoneData['frequencies'].append(frequency)
        overtoneData['intensities'].append(intensity)
        overtoneData['notes'].append(getClosestNote(frequency))
        overtoneData['frequencyCount'] += 1

    # update set aggregate data
    if frequency < overtoneData['baseFrequency']:
        overtoneData['baseFrequency'] = frequency
        overtoneData['rootNote'] = getClosestNote(frequency)
        overtoneData['accuracy'] = getAccuracy(frequency)

    overtoneData['maxIntensity'] = np.max([intensity, overtoneData['maxIntensity']])

def getOvertoneSets(data, xf, setThreshold=0.07):
    prominenceRange = int(np.round(5 / xf[1])) # to check if a peak is truely prominent scan over range of 10hz
    overtoneSets = []
    
    for index, frequency in enumerate(xf):
        intensity = data[index]

        rangeStart = index - prominenceRange
        rangeEnd = index + prominenceRange
        averageInRange = np.mean(data[rangeStart:rangeEnd])
        prominence = intensity / averageInRange

        if prominence > 1.5 and intensity > 0.03:
            bestDistance = 1
            bestSet = None

            for overtoneData in overtoneSets:
                frequencyRatio = frequency / overtoneData['baseFrequency']
                frequencyRatio = np.max([frequencyRatio, 1/frequencyRatio])
                distanceFromSet = frequencyRatio % 1

                if distanceFromSet < setThreshold and bestDistance > distanceFromSet:
                    bestDistance = distanceFromSet
                    bestSet = overtoneData
            
            if bestSet is None:
                overtoneSets.append(createOvertoneSet(frequency, intensity))
            else:
                addFrequencyToOvertoneSet(bestSet, frequency, intensity)
    
    return filter(overtoneSetValid, overtoneSets)

def overtoneSetValid(overtoneData):
    return (overtoneData['maxIntensity'] > 0.1 and overtoneData['baseFrequency'] < 700 and overtoneData['accuracy'] < 50 and overtoneData['frequencyCount'] > 1)

def addTitle(overtoneSets):
    notesForTitle = np.array([])
    for overtoneData in overtoneSets:
        notesForTitle = np.append(notesForTitle, overtoneData['rootNote'])

    uniqueNotesForTitle = np.unique(notesForTitle)

    if len(uniqueNotesForTitle) >= 3:
        plt.title(guessChord(uniqueNotesForTitle) + ', ' + ', '.join(uniqueNotesForTitle))
    else: 
        plt.title(', '.join(uniqueNotesForTitle))

def plotfft(data, fftOut, xf, overtoneSets):
    plt.xlim(0, 1000)
    plt.grid()
    plt.plot(xf, fftOut)
    for overtoneData in overtoneSets:
        for frequency, intensity, note in zip(overtoneData['frequencies'], overtoneData['intensities'], overtoneData['notes']):
            multipleFactor = str(int(np.round(frequency/overtoneData['baseFrequency'])))
            helpString = (' (' + note +')') if note != overtoneData['rootNote'] else ''
            plt.text(frequency, intensity, overtoneData['rootNote'] + multipleFactor + helpString)

def drawNotes(data, fftOut, xf, overtoneSets):
    colors = cm.hsv(np.linspace(0,1,12))
    for overtoneData in overtoneSets:
        X = []
        Y = []
        cleanFrequency = str(int(np.round(getCleanFrequency(overtoneData['baseFrequency']))))
        accuracy = str(int(np.round(overtoneData['accuracy'])))
        legendLabel = overtoneData['rootNote'] + cleanFrequency  + ' + ' + accuracy
        halfsteps = int(np.round(getDistanceFromA4(overtoneData['baseFrequency'])))
        color = colors[halfsteps % 12]
        for string in range(0, len(Strings)):
            baseFrequency = getFrequencyOfString(string)
            multiplier = overtoneData['baseFrequency'] / baseFrequency
            fretPosition = np.round(np.log2(multiplier) * 12)
            if fretPosition >= 0 and fretPosition < 18:
                xpos = getPhysicalPosition(fretPosition + 0.5)
                X.append(xpos)
                Y.append(string + 1)
                plt.text(xpos, string + 1, overtoneData['rootNote'], horizontalalignment='center', verticalalignment='center', fontsize=12)

        plt.scatter(X, Y, s=300, linewidth=2, label=legendLabel, facecolors='white', edgecolors=color)
    
    plt.legend(loc='upper right')


def listenfft(duration=3, wait=3):
    plt.show(block=False)
    while True:
        record('test.wav', duration)
        data, fftOut, xf, overtoneSets = parsefft('test.wav')
        plt.clf()
        plotfft(data, fftOut, xf, overtoneSets)
        addTitle(overtoneSets)
        plt.draw()
        sleep(wait)

def listenDisplay(duration=3, wait=3):
    setAxes()
    plt.show(block=False)
    while True:
        record('test.wav', duration)
        data, fftOut, xf, overtoneSets = parsefft('test.wav')
        plt.clf()
        setAxes(False)
        drawNotes(data, fftOut, xf, overtoneSets)
        addTitle(overtoneSets)
        plt.draw()
        sleep(wait)

def listen(duration=3, wait=3):
    fig = plt.figure(figsize=(20, 6))
    plt.show(block=False)
    while True:
        record('test.wav', duration)
        data, fftOut, xf, overtoneSets = parsefft('test.wav')
        plt.clf()
        plt.subplot(211)
        addTitle(overtoneSets)
        plotfft(data, fftOut, xf, overtoneSets)
        plt.draw()
        plt.subplot(212)
        setAxes(False)
        drawNotes(data, fftOut, xf, overtoneSets)
        plt.draw()
        plt.pause(0.1)
        sleep(wait)

def processFFT(file):
    data, fftOut, xf, overtoneSets = parsefft(file)
    addTitle(overtoneSets)
    plotfft(data, fftOut, xf, overtoneSets)
    plt.show(block=False)