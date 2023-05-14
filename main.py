import os
import time
import speech_recognition as sr
import pyttsx3

def speak(text):
	"""
	This function takes in input text, generates an audio file from it and plays the sound
	
	*Text input can only be recognised if it is in english*
	"""
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

speak("Hello!")