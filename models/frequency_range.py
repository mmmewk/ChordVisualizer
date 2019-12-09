class FrequencyRange(object):
  def __init__(self, start, end):
    self.start = start
    self.end = end

  def contains(self, frequency):
    return frequency >= self.start and frequency <= self.end

  def overlaps(self, other):
    return self.contains(other.start) or self.contains(other.end)

  def merge(self, other):
    if not self.overlaps(other):
      raise Exception('Invalid Merge', 'Frequency Ranges do not overlap')

    if self.contains(other.start) and not self.contains(other.end):
      self.end = other.end

    if self.contains(other.end) and not self.contains(other.start):
      self.start = other.start

  @staticmethod
  def simplify(in_ranges):
    # duplicate in ranges just in case
    in_ranges = list(map(lambda r: FrequencyRange(r.start, r.end), in_ranges))
    out_ranges = []
    for in_range in in_ranges:
      overlap_found = False
      for out_range in out_ranges:
        if out_range.overlaps(in_range):
          out_range.merge(in_range)
          overlap_found = True
          break

      if not overlap_found:
        out_ranges.append(in_range)

    return sorted(out_ranges, key=lambda r: r.start)

  @staticmethod
  def inverse(in_ranges):
    inverse_ranges = []
    cursor = 0
    for in_range in in_ranges:
      inverse_ranges.append(FrequencyRange(cursor, in_range.start))
      cursor = in_range.end

    return inverse_ranges
    

