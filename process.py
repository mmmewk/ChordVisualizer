from audio import *
from time import sleep
import matplotlib.pyplot as plt
from scipy.io import wavfile as wav
from scipy.fftpack import fft
from scipy.signal import find_peaks_cwt
import numpy as np

ChunkSize = 0.1

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
    # plt.clf()
    plt.plot(xf, np.abs(fftOut[0:N//2]))
    plt.show(block=False)

def plotfft(file, threshold=0.2, width=0.7, maxFrequency=700):
    data = parse(file)
    fftOut = fft(data['intensity'])
    N = data['N']
    fftOut = fftOut[0:N//30]
    fftOut = np.abs(fftOut)
    fftOut = fftOut / np.max(fftOut)

    maximaIndexes = find_peaks_cwt(fftOut, np.array([width]))
    xf = np.linspace(0.0, data['rate'] / 30, N // 30)
    plt.clf()
    plt.xlim(0, 1000)
    plt.grid()
    plt.plot(xf, fftOut)
    notesToPlot = {}
    for index in maximaIndexes:
        frequency = xf[index]
        intensity = fftOut[index]
        if (intensity > threshold) and (maxFrequency > frequency):
            halfsteps = getDistanceFromA4(frequency)
            if (halfsteps not in notesToPlot) or (intensity > notesToPlot[halfsteps]['intensity']):
                notesToPlot[halfsteps] = { 'frequency': frequency, 'intensity': intensity }
    
    notesForTitle = []
    for halfsteps, data in notesToPlot.items():
        note = getNoteFromNote('A', halfsteps)
        notesForTitle = np.append(notesForTitle, note)
        plt.text(data['frequency'], data['intensity'], note)

    uniqueNotesForTitle = np.unique(notesForTitle)

    if len(uniqueNotesForTitle) >= 3:
        plt.title(guessChord(uniqueNotesForTitle) + ', ' + ', '.join(uniqueNotesForTitle))
    else: 
        plt.title(mode(notesForTitle.tolist()) + ', ' + ', '.join(uniqueNotesForTitle))

    plt.draw()
    plt.pause(0.0001)

def listen(outputFile, duration=0.1, wait=0.5):
    plt.show(block=False)
    while True:
        record(outputFile, duration)
        plotfft(outputFile)
        sleep(wait)

