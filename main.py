import os
import time
import asyncio
import pyttsx3
import requests
import speech_recognition as sr

async def speak(text : str) -> dict:
	"""
	This function takes in input text, generates an audio file from it and plays the sound

	*Text input can only be recognised if it is in english*

	Returns Dictionary { error-code, error }

	Error Code (code): int ( 1 for error and 0 for success )

	Error (error): a python Exception
	"""
	try:
		engine = pyttsx3.init()
		engine.say(text)
		engine.runAndWait()

		return { 'code' : 0, 'error': None }
	except Exception as e:
		return { 'code' : 1, 'error': e }
	

async def listen() -> dict:
	"""
	This function takes audio input by the user through the microphone

	And turns it into words

	It returs a dictionary containing the response, error and error code 

	Response (res): is a string in lower case 

	Error code (code): number ie. 1 or 0

	Error (error): a python Exception
	"""
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""
		try:
			said = r.recognize_google(audio)
		except Exception as e:
			return { 'res': said.lower(), 'code': 1, 'error': e }

	return { 'res': said.lower(), 'code': 0, 'error': None }

async def respond(prompt : str) -> dict:
	"""
	This function takes in an input prompt as a string and interacts with

	the OpenAssistant text-based AI (https://huggingface.co/OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5)

	through an API space (https://huggingface.co/spaces/onuri/asst) to generate response object / dictionary

	the function returns a dictionary containing { response, code, error }

	Response (res): is a string for the response

	Error code (code): number ie. 1 or 0

	Error (error): a python Exception
	"""
	data = ""
	
	try:
		response = requests.post("https://onuri-asst.hf.space/run/predict", json={
			"data": [
				prompt,
			]
		}).json()

		data = response["data"][0]
	except Exception as e:
		return { 'res': data, 'code': 1, 'error': e }
	
	return { 'res': data, 'code': 0, 'error': None }
