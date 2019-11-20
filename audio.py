import os

def play(note, delay=0, time=1):
    play_multiple([note], time=time, delay=delay)

def play_multiple(note, time=1, delay=0):
    note = Note(note)
    command = ' pluck '.join(map(lambda n: str(n.frequency), notes))
    if delay:
        delays = map(lambda i: str(i * delay), range(0, len(notes)))
        command += ' delay ' + ' '.join(delays)
    os.system('play -n synth %f pluck %s' % (time, command))

def record(out_file, time):
    os.system('rec -c 1 ' + str(out_file) + ' trim 0 ' + str(time))

def play_file(input_file, time=None):
    command = 'play ' + str(input_file)
    if bool(time):
        command = command + ' trim 0 ' + str(time)
    os.system(command)