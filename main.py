import os
import time
import speech_recognition as sr
import pyttsx3

def speak(text : str) -> None:
	"""
	This function takes in input text, generates an audio file from it and plays the sound
	
	*Text input can only be recognised if it is in english*
	"""
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

def listen() -> str:
	"""
	This function takes audio input by the user through the microphone

	And turns it into words

	( Returs a string in lower case )
	"""
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""
		try:
			said = r.recognize_google(audio)
		except Exception as e:
			print("Exception:", str(e))

	return said.lower()