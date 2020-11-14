import urllib
import requests
import re
import speech_recognition as sr
import pyttsx3
import vlc
import threading
import pafy

# @Author (Motheen Baig)
# GitHub (https://github.com/motheenb/VPlayer)


class Listen(threading.Thread):  # runs single Thread to listen for voice input
    def __init__(self):
        threading.Thread.__init__(self)
        self.player = AudioPlayer()
        self.r = sr.Recognizer()
        self.listening = True
        self.functions = {  # str(command) linked to its function
            'play': self.player.play_song,
            'pause': self.player.pause_song,
            'stop': self.player.stop_song,
            'resume': self.player.resume_song,
            'volume': self.player.volume_control,
            '': self.player.idle
        }

    def run(self):
        while self.listening is True:
            speech_input = self.speech_to_text()
            operation = str(speech_input.split(' ')[0])
            context = speech_input.replace(operation + ' ', '')  # grab everything after the first word/operation
            for f in self.functions:
                if operation == f:  # if valid function
                    self.functions[operation](context)  # execute function with functions[function_name]

    def speech_to_text(self) -> str:
        text = ''
        try:
            with sr.Microphone() as src:
                self.r.adjust_for_ambient_noise(src, duration=0.7)
                audio = self.r.record(src, duration=10)  # record for duration of 5 sec.
                voice_to_text = self.r.recognize_google(audio)
                text = voice_to_text.lower()
                return text
        except sr.RequestError as e:
            pass
        except sr.UnknownValueError:
            # print('No Input Detected!')
            pass
        return text


class AudioPlayer:
    def __init__(self):
        self.media = None
        self.video = None
        self.best = None
        self.play_intro()

    def play_song(self, context) -> vlc.MediaPlayer:  # returns instance of MediaPlayer
        speak_text('Playing ' + context)
        self.video = pafy.new(find_song_url(context))
        self.best = self.video.getbestaudio()
        if self.media is not None:
            vlc.MediaPlayer.release(self.media)
        self.media = vlc.MediaPlayer(self.best.url)
        vlc.MediaPlayer.audio_set_volume(self.media, 50)
        self.media.play()  # play YouTube audio
        return self.media

    def resume_song(self, context):
        speak_text('Resuming Music!')
        vlc.MediaPlayer.play(self.media)

    def stop_song(self, context):
        speak_text('Stopping Music!')
        vlc.MediaPlayer.stop(self.media)

    def pause_song(self, context):
        speak_text('Pausing Music!')
        vlc.MediaPlayer.pause(self.media)

    def volume_control(self, context):
        volume_settings = {  # customizable volume settings
            'low': 25,
            'medium': 55,
            'high': 85
        }
        speak_text('Volume control!')
        if context == 'mute':
            speak_text('Muting Music!')
            vlc.MediaPlayer.audio_set_mute(self.media, True)  # Mute
        elif context == 'play':
            speak_text('Resuming Music!')
            vlc.MediaPlayer.audio_set_mute(self.media, False)  # UnMute
        elif context == 'low' or context == 'medium' or context == 'high':
            vlc.MediaPlayer.audio_set_volume(self.media, int(volume_settings[context]))  # set volume to preset value
        else:
            volume = int(context)
            vlc.MediaPlayer.audio_set_volume(self.media, volume)  # set volume to int value

    def play_intro(self):
        self.media = vlc.MediaPlayer("welcome.mp3")
        self.media.play()

    def idle(self, context):  # handle actions while idle ?
        # print('IDLE')
        pass


def find_song_url(song_name) -> str:
    query_string = urllib.parse.urlencode({"search_query": song_name})
    format_url = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    search_results = re.findall(r"watch\?v=(\S{11})", format_url.read().decode())
    clip = requests.get("https://www.youtube.com/watch?v=" + "{}".format(search_results[0]))
    format_clip = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])  # refined YouTube video URL
    return format_clip


def speak_text(command):  # speak using the os voice
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


def main():  # create instance of Listen Thread and start()
    listen = Listen()
    listen.start()


if __name__ == '__main__':
    main()
