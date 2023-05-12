import os
import time
import playsound as ps
import speech_recognition as sr
from gtts import gTTS

def speak(text):
	"""
	This function takes in input text, generates an audio file from it and plays the sound
	*Text input can only be recognised if it is in english*
	"""
	tts = gTTS(text=text, lang="en")
	filename = "voice.mp3"
	tts.save(filename)
	ps.playsound(filename)

speak("Hello World")