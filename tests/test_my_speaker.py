from pidevices import Speaker
import alsaaudio
import wave

periodsize = 256
channels = 2
framerate = 44100
dev_name ="hw:CARD=Speaker,DEV=0"
device = alsaaudio.PCM(device=dev_name)

card_name = dev_name.split(":")[-1].split(",")[0].split("=")[-1]
card_index = alsaaudio.cards().index(card_name)
mixers = alsaaudio.mixers(cardindex=card_index)
if "PCM" in mixers:
    mixer = alsaaudio.Mixer(control='PCM', cardindex=card_index)
    mixer.setvolume(30)

source = '/home/pi/tektrain-robot-sw/wav_sounds/file_example_WAV_1MG.wav'
#source = '/home/pi/start.wav'
f = wave.open(source, 'rb')

channels = f.getnchannels()
framerate = f.getframerate()
sample_width = f.getsampwidth()
print(channels, framerate, sample_width)

# Read data from file
data = []
sample = f.readframes(periodsize)
while sample:
    data.append(sample)
    sample = f.readframes(periodsize)

# Close file
f.close()


device.setchannels(channels)
device.setrate(framerate)
device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
device.setperiodsize(periodsize)


for d in data:
    device.write(d)


# speaker = Speaker()
# speaker.volume = 10
# source = '/home/pi/tektrain-robot-sw/wav_sounds/file_example_WAV_1MG.wav'
# speaker.write(source, times=1, file_flag=True)
