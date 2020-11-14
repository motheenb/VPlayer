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
        self.listening = True
        self.r = sr.Recognizer()
        self.media = None
        self.song_history = []
        self.song_queue = []

    def run(self):
        while self.listening is True:
            command = self.speech_to_text()
            self.handle_commands(command)

    def handle_commands(self, command):
        operations = command.split(' ')
        op = str(operations[0])
        context = command.replace(op + ' ', '')
        if op == 'queue':
            self.song_queue.append(context)
        elif op == 'play':
            speak_text('Playing ' + context)
            self.song_history.append(context)
            self.play_song(context)
        elif op == 'stop':
            speak_text('Stopping Music!')
            vlc.MediaPlayer.release(self.media)
        elif op == 'back':
            back = int(context)
            speak_text('Playing ' + context)
            self.back(back)
        elif op == 'pause':
            speak_text('Pausing Music!')
            vlc.MediaPlayer.pause(self.media)
        elif op == 'resume':
            speak_text('Resuming Music!')
            vlc.MediaPlayer.play(self.media)
        elif op == 'volume':
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

    def back(self, num):
        size = len(self.song_history)
        if size > 0:
            self.play_song(self.song_history.__getitem__(size-num))

    def play_song(self, song_name):
        video = pafy.new(find_song_url(song_name))
        best = video.getbestaudio()
        if self.media is not None:
            vlc.MediaPlayer.release(self.media)
        self.media = vlc.MediaPlayer(best.url)
        vlc.MediaPlayer.audio_set_volume(self.media, 50)
        self.media.play()


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
