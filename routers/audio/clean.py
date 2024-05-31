# We will crop the first 5 seconds of the audio file and adjust the audio

import os

from pydub import AudioSegment


# Load the audio file

audio = AudioSegment.from_file("routers/audio/env_sounds/rain.mp3")

# Crop the first 5 seconds of the audio file
cropped_audio = audio[5000:]

# Adjust the volume of the audio file
adjusted_audio = cropped_audio + 10

# Export the adjusted audio file
adjusted_audio.export("routes/audio/env_sounds/adjusted_rain.mp3", format="mp3")

audio = AudioSegment.from_file("routers/audio/env_sounds/birds.mp3")

cropped_audio = audio[5000:]

adjusted_audio = cropped_audio + 10

adjusted_audio.export("routes/audio/env_sounds/adjusted_birds.mp3", format="mp3")

audio = AudioSegment.from_file("routers/audio/env_sounds/wind.mp3")

cropped_audio = audio[5000:]

adjusted_audio = cropped_audio - 5

adjusted_audio.export("routes/audio/env_sounds/adjusted_wind.mp3", format="mp3")

