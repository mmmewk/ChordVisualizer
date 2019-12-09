- Optimization:
  - For each filter write a method that returns a range of viable values
  - Record a set of audio files with exactly which notes were played
  - Create a grid mesh of combinations of filter values and find the best accuracy

- Real Time:
  - Find a way to record audio into an input stream that can be processed as audio comes in
  - Figure out how accuracy in note recognition depends on audio duration

- Chord Validation:
  - Probably Easier than Chord Guessing
  - For a given chord find all root notes and first few overtones
  - Integrate over a certain accuracy range around each note
  - Integrate outside of the range too
  - If a majority of the intensity is inside of correct range return true
  