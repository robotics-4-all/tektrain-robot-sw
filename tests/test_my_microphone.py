import sys
import time
from pidevices.actuators.speaker import Speaker
from pidevices.sensors.microphone import Microphone
import base64
import wave



def stringToWav(recorded_sound, path = None):
    source = base64.b64decode(recorded_sound.encode("ascii"))
    n = len(source)
    step = 2 * 256
    data = [source[i:i+step] for i in range(0, n, step)]

    f = wave.open(path, 'wb')

    # Set file attributes
    f.setnchannels(1)
    f.setframerate(44100)
    f.setsampwidth(2)
    f.setnframes(256)

    for sample in data:
        f.writeframes(sample)

    f.close()


def playSoundFromFile(volume, file):
    # Open the wav file
    f = wave.open(file, 'rb')

    channels = f.getnchannels()
    framerate = f.getframerate()
    sample_width = f.getsampwidth()
    print(channels, framerate, sample_width)

    # Read data from file
    data = bytearray()
    sample = f.readframes(256)
    print(type(sample))
    while sample:
        for s in sample:
            data.append(s)
        sample = f.readframes(256)

    # Close file
    f.close()

    source = base64.b64encode(data).decode("ascii")
    
    return source


if __name__ == "__main__":
    mic_dev_name = "Mic"
    mic_framerate = 44100
    mic_channels = 1
    
    speaker_dev_name = "Speaker"
    speaker = Speaker(dev_name=speaker_dev_name)  
    
    file_path = sys.argv[1]
    from_file = sys.argv[2]

    print("Recording.....")
    mic = Microphone(dev_name=mic_dev_name, channels=mic_channels)
    audio = mic.read(secs=5, 
                    framerate=mic_framerate, 
                    volume=50, 
                    file_path=file_path, 
                    file_flag=False)
    
    recorded_sound = base64.b64encode(mic.record).decode("ascii")
    stringToWav(recorded_sound, file_path)

    source = playSoundFromFile(100,  file_path)
    source = base64.b64decode(source.encode("ascii"))

    print("Source length: ",round(len(source) / (2 * mic_framerate)))
    
    speaker.volume = 100

    speaker.async_write(source, file_flag=False)
    duration = round(len(source) / (2 * mic_framerate))
    try:
        _timer = time.time()
        while speaker.playing:
            if (time.time() - _timer) > duration * 1.01 + 0.1:
                raise Exception("Speaker: timeout!")
            time.sleep(0.1)
    except Exception as e:
        print(f"Speaker stuck with msg: {e}! Restarting it..")
    
        # success = False
        # speaker.stop()
        # while (not success):
        #     try:
        #         speaker.start()
        #         success = True
        #     except Exception as e:
        #         print("Exception caught")
        #         success = False
            
        #     time.sleep(5)

    


       
    

    

    



