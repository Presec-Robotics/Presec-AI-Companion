import os
import time
import playsound as ps
import speech_recognition as sr
from gtts import gTTS

def speak(text):
	tts = gTTS(text=text, lang="en")
	filename = "voice.mp3"
	tts.save(filename)
	ps.playsound(filename)

speak("Hello World")