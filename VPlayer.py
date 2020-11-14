import urllib
import requests
import re
import speech_recognition as sr
import pyttsx3
import vlc
import threading
import pafy


class GrooV(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.functions = {
            'play': self.play_song,
            'stop': self.stop,
            'pause': self.pause,
            'resume': self.resume,
            'volume': self.handle_volume
        }
        self.listening = True
        self.r = sr.Recognizer()
        self.media = None
        self.context = ''
        self.song_history = []
        self.song_queue = []

    def run(self):
        while self.listening is True:
            command = self.speech_to_text()
            self.handle_commands(command)

    volume_settings = {
        'low': 25,
        'medium': 55,
        'high': 85
    }

    def set_volume(self, volume):
        if self.media is not None:
            speak_text('Adjusting Volume!')
            vlc.MediaPlayer.audio_set_volume(self.media, volume)

    def speech_to_text(self) -> str:
        text = ''
        try:
            with sr.Microphone() as src:
                # self.r.adjust_for_ambient_noise(src, duration=0.2)
                audio = self.r.record(src, duration=5)
                voice_to_text = self.r.recognize_google(audio)
                text = voice_to_text.lower()
                return text
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print('No Input Detected!')
        return text

    def pause(self):
        speak_text('Pausing Music!')
        vlc.MediaPlayer.pause(self.media)

    def stop(self):
        speak_text('Stopping Music!')
        if self.media is not None:
            vlc.MediaPlayer.release(self.media)

    def back(self, num):
        size = len(self.song_history)
        if size > 0:
            self.play_song(self.song_history.__getitem__(size-num))

    def resume(self):
        speak_text('Resuming Music!')
        if self.media is not None:
            vlc.MediaPlayer.play(self.media)

    def handle_volume(self):
        context = self.context
        if context == 'mute':
            speak_text('Muting Music!')
            vlc.MediaPlayer.audio_set_mute(self.media, True)
        elif context == 'play':
            speak_text('Resuming Music!')
            vlc.MediaPlayer.audio_set_mute(self.media, False)
        elif context == 'low' or context == 'medium' or context == 'high':
            self.set_volume(self.volume_settings[context])
        else:
            volume = int(context)
            self.set_volume(volume)

    def play_song(self):
        speak_text('Playing ' + self.context)
        video = pafy.new(find_song_url(self.context))
        best = video.getbestaudio()
        if self.media is not None:
            vlc.MediaPlayer.release(self.media)
        self.media = vlc.MediaPlayer(best.url)
        vlc.MediaPlayer.audio_set_volume(self.media, 50)
        self.media.play()

    def do_function(self, op):
        if not op:
            self.functions[op]

    def handle_commands(self, command):
        operations = command.split(' ')
        op = str(operations[0])
        self.context = command.replace(op + ' ', '')
        print(op + " = " + self.context)
        # self.do_function(op)


# scrape YouTube to find appropriate URL for requested song
def find_song_url(song_name) -> str:
    query_string = urllib.parse.urlencode({"search_query": song_name})
    format_url = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    search_results = re.findall(r"watch\?v=(\S{11})", format_url.read().decode())
    clip = requests.get("https://www.youtube.com/watch?v=" + "{}".format(search_results[0]))
    format_clip = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])
    return format_clip


def speak_text(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


g = GrooV()
g.start()
