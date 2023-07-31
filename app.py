# Import required libraries and modules
import pygame
from math import sin, cos, radians
from win32api import GetSystemMetrics
import main as sm
import asyncio
from threading import Thread
import pyaudio
import numpy as np


class Circle():
    """
    Interface for creating circle on screen
    """
    def __init__(self, parent, x, y, r, color):
        # Initialize circle properties
        self.parent = parent
        self.x = x
        self.y = y
        self.radius = r
        self.color = color

    def center(self):
        # Center the circle on the screen
        self.x = self.parent.get_width() / 2
        self.y = self.parent.get_height() / 2

    def set_revolution(self, angle, distance, focus_x, focus_y):
        # Set circle position in a circular path
        angle_rad = radians(angle)
        self.x = focus_x + (distance * cos(angle_rad))
        self.y = focus_y + (distance * sin(angle_rad))

    def draw(self, screen):
        # Draw the circle on the screen
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class Text():
    """
    Interface for creating text elements
    """
    def __init__(self, text, x, y, size, color, fontname=None):
        # Initialize text properties
        self.x = x
        self.y = y
        self.text = text
        self.size = size
        self.fontname = fontname
        self.color = color
        self.font = pygame.font.SysFont(self.fontname, self.size)
        self.text_surface = self.font.render(self.text, True, self.color)

    def center_x(self, screen):
        # Center the text horizontally on the screen
        self.x = (screen.get_width() - self.text_surface.get_width()) / 2

    def center_y(self, screen):
        # Center the text vertically on the screen
        self.y = (screen.get_height() - self.text_surface.get_height()) / 2

    def render(self, screen):
        # Render the text on the screen
        screen.blit(self.text_surface, (self.x, self.y))


def get_pitch():
    """
    Read audio stream from device and determine it's pitch
    """

    # determine recording frequency and speed
    CHUNK_SIZE = 1024
    SAMPLE_RATE = 44100

    # listen to audio stream
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    # read and sample audio data
    data = stream.read(CHUNK_SIZE)
    samples = np.frombuffer(data, dtype=np.int16)

    # get estimated pitch
    audio_level = np.abs(samples).mean()

    return audio_level


# Global variables for controlling the flow of the application
is_listening = False
is_processing = True
is_speaking = False

prompt = "hello, what is your name"
response = ""
error = ""


async def main():
    # Initialize pygame and screen properties
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
        """
        Handle listening
        """
        global prompt, is_listening, is_processing, error

        data = sm.listen()

        # handle errors ( just in case )
        if data['code'] == 0:
            prompt = data['res']
            is_listening = False
            is_processing = True
        else:
            error = data['error']

        print("listen thread reached end")

    def process():
        """
        Handle processing
        """
        global prompt, response, error, is_speaking, is_processing

        data = sm.respond(prompt)

        # handle errors ( just in case )
        if data['code'] == 0:
            response = data['res']
            is_processing = False
            is_speaking = True
        else:
            print(error)
            error = data['error']
        
        print("process thread reached end")

    def respond():
        """
        Handle response
        """
        global prompt, response, error, is_speaking, is_listening

        data = sm.speak(response)

        # handle errors ( just in case )
        if data['code'] == 0:
            is_speaking = False
            is_listening = True
        else:
            error = data['error']

        print("respond thread reached end")

    # create Threads to handle tasks in backgroud ( For increasing performance )
    listen_thread = Thread(target=listen)
    process_thread = Thread(target=process)
    respond_thread = Thread(target=respond)

    # Run Application interface
    while running:
        for event in pygame.event.get():
            # Quit if any "Quit" event is triggered
            if event.type == pygame.QUIT:
                running = False

        screen.fill("#FFFFFF")

        # Render Listening Scene
        if is_listening:
            # start listening thread if it is'nt already running
            if not listen_thread.is_alive():
                print("listen thread started")
                listen_thread.start()

            # determing the scale of the audio visualizer
            pitch = get_pitch()
            scale = pitch * 0.6 + 20

            # render audio visualizer
            mid = Circle(screen, 10, 10, scale, "#B3AED3")
            mid.center()
            mid.draw(screen)

            # render "Listening..." text
            text = Text("Listening...", 100, 100, 36, "Black")
            text.center_x(screen)
            text.center_y(screen)
            text.y += 200
            text.render(screen)
        
        # render processing scene
        elif is_processing:
            print("process thread started")
            # start processing thread if it is'nt already running
            if not process_thread.is_alive():
                process()

            # create central circle
            mid = Circle(screen, 10, 10, 80, "#95cb95")
            mid.center()
            mid.draw(screen)

            # create mini satelite circle
            mini = Circle(screen, 10, 10, 20, "#95cb95")

            # revole mini circle around central circle
            mini.set_revolution(i, 110, mid.x, mid.y)

            # render prompt text
            text = Text(prompt, 100, 100, 36, "Black")
            text.center_x(screen)
            text.center_y(screen)
            text.y += 200
            text.render(screen)

            # increase mini circle revolution and update the element
            i += angular_velocity * deltaTime
            mini.draw(screen)

        # render speaking scene
        elif is_speaking:
            print("respond thread started")
            # start respond thread if it is'nt already running
            if not respond_thread.is_alive():
                respond_thread.start()

            # determine visualizer scale
            pitch = get_pitch()
            scale = pitch * 0.6 + 20

            # render audio visualizer
            mid = Circle(screen, 10, 10, scale, "#95a0cb")
            mid.center()
            mid.draw(screen)

            # render response text
            text = Text(response, 100, 100, 36, "Black")
            text.center_x(screen)
            text.center_y(screen)
            text.y += 200
            text.render(screen)

        deltaTime = (pygame.time.get_ticks() - startTime) / 1000.0
        startTime = pygame.time.get_ticks()

        # render application scene
        pygame.display.update()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    asyncio.run(main())
