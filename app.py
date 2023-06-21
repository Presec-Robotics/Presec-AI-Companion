import pygame
from math import sin, cos, radians
from win32api import GetSystemMetrics
from random import randint
import main as sm
import asyncio 
from threading import *
import pyaudio
import numpy as np

class Circle():
    def __init__(self, parent, x, y, r, color):
        self.parent = parent
        self.x = x
        self.y = y
        self.radius = r
        self.color = color
    def center(self):
        self.x = self.parent.get_width() / 2
        self.y = self.parent.get_height() / 2
    def set_revolution(self, angle, distance, focus_x, focus_y):
        angle_rad = radians(angle)
        self.x = focus_x + (distance * cos(angle_rad))
        self.y = focus_y + (distance * sin(angle_rad))
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Text():
    def __init__(self, text, x, y, size, color, fontname=None):
        self.x = x
        self.y = y
        self.text = text
        self.size = size
        self.fontname = fontname
        self.color = color
        self.font = pygame.font.SysFont(self.fontname, self.size)
        self.text_surface = self.font.render(self.text, True, self.color)
    def center_x(self, screen):
        self.x = (screen.get_width() - self.text_surface.get_width()) / 2
    def center_y(self, screen):
        self.y = (screen.get_height() - self.text_surface.get_height()) / 2
    def render(self, screen):
        screen.blit(self.text_surface,(self.x, self.y))

import sounddevice as sd
import numpy as np

def get_pitch():
    CHUNK_SIZE = 1024
    SAMPLE_RATE = 44100

    # Create PyAudio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK_SIZE)

    data = stream.read(CHUNK_SIZE)
    samples = np.frombuffer(data, dtype=np.int16)

    audio_level = np.abs(samples).mean()

    return audio_level

is_listening = True
is_processing = False
is_speaking = False

prompt = "hello"
response = ""
error = ""

async def main():
    pygame.init()

    SCREEN_WIDTH = GetSystemMetrics(0)
    SCREEN_HEIGHT = GetSystemMetrics(1)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE, vsync=1)
    clock = pygame.time.Clock()

    running = True
    angular_velocity = 90
    i = 0
    deltaTime = 0.0

    def listen():
        data = sm.listen()

        global prompt, is_listening, is_processing, error

        if data['code'] == 0:
            prompt = data['res']
            is_listening = False
            is_processing = True
        else:
            error = data['error']
        print(data)

    def process(prompt):
        data = sm.respond(prompt)

        global response, is_speaking, is_processing, error

        if data['code'] == 0:
            response = data['res']
            is_processing = False
            is_speaking = True
        else:
            error = data['error']

    def respond(response):
        data = sm.speak(response)

        global prompt, is_speaking, is_listening, error

        if data['code'] == 0:
            is_speaking = False
            is_listening = True
        else:
            error = data['error']

    listen_thread = Thread(target=listen)
    process_thread = Thread(target=process, args=[prompt])
    respond_thread = Thread(target=respond, args=[response])

    if is_listening and not listen_thread.is_alive():
        listen_thread.start()
    elif is_processing and not process_thread.is_alive():
        process_thread.start()
    elif is_speaking and not respond_thread.is_alive():
        respond_thread.start()

    startTime = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("#FFFFFF")

        if is_listening:
            scale = min(100 ,get_pitch() / 200 + 20)
            
            mid = Circle(screen, 10, 10, scale, "#B3AED3")
            mid.center()
            mid.draw(screen)
            
            text = Text("Listening...", 100, 100, 36, "Black")
            text.center_x(screen)
            text.center_y(screen)
            text.y += 200
            text.render(screen)
        elif is_processing:
            mid = Circle(screen, 10, 10, 80, "#95cb95")
            mid.center()
            mid.draw(screen)

            mini = Circle(screen, 10, 10, 20, "#95cb95")

            mini.set_revolution(i, 110, mid.x, mid.y)

            text = Text(prompt, 100, 100, 36, "Black")
            text.center_x(screen)
            text.center_y(screen)
            text.y += 200
            text.render(screen)

            i += angular_velocity * deltaTime
            mini.draw(screen)
        elif is_speaking:
            pitch = get_pitch()
            scale = pitch * 0.6 + 20

            mid = Circle(screen, 10, 10, scale, "#95a0cb")
            mid.center()
            mid.draw(screen)
            
            text = Text(response, 100, 100, 36, "Black")
            text.center_x(screen)
            text.center_y(screen)
            text.y += 200
            text.render(screen)

        deltaTime = ( pygame.time.get_ticks() - startTime ) / 1000.0
        startTime = pygame.time.get_ticks()

        pygame.display.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
	asyncio.run(main())