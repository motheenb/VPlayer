import threading
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
        self.media = vlc.MediaPlayer()
        self.r = sr.Recognizer()
        self.listening = True
        self.functions = {  # str(command) linked to its function
            'play': play_song,
            'pause': pause_song,
            'stop': stop_song,
            'resume': resume_song,
            'volume': volume_control,
            '': idle
        }

    def run(self):
        while self.listening is True:
            speech_input = self.speech_to_text()
            operation = str(speech_input.split(' ')[0])
            context = speech_input.replace(operation + ' ', '')  # grab everything after the first word/operation
            for f in self.functions:
                if operation == f:  # if valid function
                    self.functions[operation](context, self.media)  # execute function with functions[function_name]

    def speech_to_text(self) -> str:
        text = ''
        try:
            with sr.Microphone() as src:
                audio = self.r.record(src, duration=5)  # record for duration of 5 sec.
                voice_to_text = self.r.recognize_google(audio)
                text = voice_to_text.lower()
                return text
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print('No Input Detected!')
        return text


def volume_control(context, media):
    volume_settings = {  # customizable volume settings
        'low': 25,
        'medium': 55,
        'high': 85
    }
    speak_text('Volume control!')
    if context == 'mute':
        speak_text('Muting Music!')
        vlc.MediaPlayer.audio_set_mute(media, True)  # Mute
    elif context == 'play':
        speak_text('Resuming Music!')
        vlc.MediaPlayer.audio_set_mute(media, False)  # UnMute
    elif context == 'low' or context == 'medium' or context == 'high':
        vlc.MediaPlayer.audio_set_volume(media, int(volume_settings[context]))  # set volume to preset value using key
    else:
        volume = int(context)
        vlc.MediaPlayer.audio_set_volume(media, volume)  # set volume to int value


# (context, media) leaves room to improve each function

def idle(context, media):  # handle actions while idle ?
    print('IDLE')


def resume_song(context, media):
    speak_text('Resuming Music!')
    vlc.MediaPlayer.play(media)


def stop_song(context, media):
    speak_text('Stopping Music!')
    vlc.MediaPlayer.release(media)


def pause_song(context, media):
    speak_text('Pausing Music!')
    vlc.MediaPlayer.pause(media)


def play_song(context, media) -> vlc.MediaPlayer:  # returns instance of MediaPlayer
    print(context)
    speak_text('Playing ' + context)
    video = pafy.new(find_song_url(context))
    best = video.getbestaudio()
    vlc.MediaPlayer.release(media)
    media = vlc.MediaPlayer(best.url)
    vlc.MediaPlayer.audio_set_volume(media, 50)
    media.play()  # play YouTube audio
    return media


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
