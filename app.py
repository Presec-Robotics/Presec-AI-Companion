import pygame
from math import sin, cos, radians
from win32api import GetSystemMetrics
import main as sm
import asyncio
from threading import Thread
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
        screen.blit(self.text_surface, (self.x, self.y))


def get_pitch():
    CHUNK_SIZE = 1024
    SAMPLE_RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    data = stream.read(CHUNK_SIZE)
    samples = np.frombuffer(data, dtype=np.int16)

    audio_level = np.abs(samples).mean()

    return audio_level


is_listening = True
is_processing = False
is_speaking = False

prompt = ""
response = ""
error = ""


async def main():
    pygame.init()

    SCREEN_WIDTH = GetSystemMetrics(0)
    SCREEN_HEIGHT = GetSystemMetrics(1)

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.RESIZABLE, vsync=1
    )

    clock = pygame.time.Clock()
    startTime = pygame.time.get_ticks()

    running = True
    angular_velocity = 90
    i = 0
    deltaTime = 0.0

    def listen():
        global prompt, is_listening, is_processing, error

        data = sm.listen()

        if data['code'] == 0:
            prompt = data['res']
            is_listening = False
            is_processing = True
        else:
            error = data['error']

    def process():
        global prompt, response, error, is_speaking, is_processing

        # data = sm.respond(prompt)
        data = {
            "code": 0, "res": "Hello Pascall de creator, i am PAC (presec A.I companion), your very own AI assistant, how may i help you? blah blah blah blah blah blah blah blah blah blah"}

        if data['code'] == 0:
            response = data['res']
            is_processing = False
            is_speaking = True
        else:
            print(error)
            error = data['error']

    def respond():
        global prompt, response, error, is_speaking, is_listening

        data = sm.speak(response)

        if data['code'] == 0:
            is_speaking = False
            is_listening = True
        else:
            error = data['error']

    listen_thread = Thread(target=listen)
    process_thread = Thread(target=process)
    respond_thread = Thread(target=respond)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("#FFFFFF")

        if is_listening:
            if not listen_thread.is_alive():
                listen_thread.start()

            pitch = get_pitch()
            scale = pitch * 0.6 + 20

            mid = Circle(screen, 10, 10, scale, "#B3AED3")
            mid.center()
            mid.draw(screen)

            text = Text("Listening...", 100, 100, 36, "Black")
            text.center_x(screen)
            text.center_y(screen)
            text.y += 200
            text.render(screen)
        elif is_processing:
            if not process_thread.is_alive():
                process()

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
            if not respond_thread.is_alive():
                respond_thread.start()

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

        deltaTime = (pygame.time.get_ticks() - startTime) / 1000.0
        startTime = pygame.time.get_ticks()

        pygame.display.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    asyncio.run(main())
