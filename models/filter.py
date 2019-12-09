from models.note import Note
import numpy as np

# a filter once added to an audio file will give a simple pass fail for a specific data point
# all points that the filter failed will be added to a list
# minimum and maximum values for the filtered property will also be soted
class Filter(object):
  def __init__(self):
    self.clear()

  def name(self):
    return self.__class__.__name__

  def clear(self):
    self.filtered = []
    self.min_value = np.inf
    self.max_value = -np.inf
    self.avg_value = 0
    self.count = 0

  def set_parent(self, parent):
    self.parent = parent
  
  def is_valid(self, index):
    if not hasattr(self, 'parent'):
      raise Exception('No Data', 'No Data has been selected to filter')
    
    value = self.get_value(index)
    if value < self.min_value:
      self.min_value = value

    if value > self.max_value:
      self.max_value = value

    total_value = self.avg_value * self.count + value
    self.count += 1
    self.avg_value = total_value / self.count

    if self.validate(value):
      return True
    else: 
      self.filtered.append(index)
      return False

# only care for frequencies in a certain range
class FrequencyFilter(Filter):
  def __init__(self, min_frequency, max_frequency):
    self.min_frequency = min_frequency
    self.max_frequency = max_frequency
    Filter.__init__(self)
    Filter.__init__(self)

  def get_value(self, index):
    return self.parent.xf[index]

  def validate(self, frequency):
    return frequency > self.min_frequency and frequency < self.max_frequency

# noises below a certain level can be ignored
class IntensityFilter(Filter):
  def __init__(self, min_intensity):
    self.min_intensity = min_intensity
    Filter.__init__(self)

  def get_value(self, index):
    return self.parent.fft_out[index]

  def validate(self, intensity):
    return intensity > self.min_intensity

class AccuracyFilter(Filter):
  def __init__(self, max_accuracy):
    self.max_accuracy = max_accuracy
    Filter.__init__(self)

  def get_value(self, index):
    frequency = self.parent.xf[index]

    # below 10 hz we honestly don't care and the pitch of the note is hard to identify
    if frequency < 10:
      return 0

    return np.abs(Note(frequency).accuracy)

  def validate(self, accuracy):
    return accuracy < self.max_accuracy

class ModeFilter(Filter):
  def __init__(self, mode_width=3):
    self.mode_width = mode_width
    Filter.__init__(self)

  def get_value(self, index):
    start = np.max([0, index - self.mode_width])
    end = np.min([index + self.mode_width, self.parent.fft_count])
    return np.max(self.parent.fft_out[start:end]) == self.parent.fft_out[index]

  def validate(self, is_mode):
    return is_mode

class RelativeHeightFilter(Filter):
  def __init__(self, min_height=1.5):
    self.min_height = min_height
    Filter.__init__(self)

  def get_value(self, index):
    frequency = self.parent.xf[index]
    intensity = self.parent.fft_out[index]
    return intensity / self.parent.average_intensity_for(frequency)

  def validate(self, height):
    return height >= self.min_height

class BestMatchFilter(Filter):
  def __init__(self):
    Filter.__init__(self)

  def get_value(self, index):
    frequency = self.parent.xf[index]
    return np.abs(Note(frequency).accuracy) <= self.parent.best_accuracy_for(frequency)

  def validate(self, is_best):
    return is_best

class OvertoneCountFilter(Filter):
  def __init__(self, min_overtones=3, overtone_match_width=0.03):
    Filter.__init__(self)
    self.min_overtones = min_overtones
    self.overtone_match_width = overtone_match_width

  def get_value(self, index):
    return self.parent.overtone_count(index, self.overtone_match_width)

  def validate(self, count):
    return count >= self.min_overtones

