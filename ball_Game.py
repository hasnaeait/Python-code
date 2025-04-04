import pygame
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json

# Initialize Pygame
pygame.init()

# Window configuration
WINDOW_SIZE = (500, 500)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Ball Movement with Vosk")

# Ball configuration
BALL_COLOR = "blue"
BALL_RADIUS = 20
ball_position = [WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2]
BALL_SPEED = 10

# Load the Vosk model
model = Model(model_name="vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

# Function to recognize speech using Vosk
def recognize_speech():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=lambda indata, frames, time, status: None):
        print("Listening...")
        while True:
            data = sd.rec(frames=8000, samplerate=16000, channels=1, dtype='int16')
            sd.wait()
            if recognizer.AcceptWaveform(data.tobytes()):
                result = json.loads(recognizer.Result())
                transcription = result.get("text", "").lower()
                print(f"Recognized: {transcription}")
                return transcription

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the background and ball
    screen.fill("white")
    pygame.draw.circle(screen, BALL_COLOR, ball_position, BALL_RADIUS)

    # Get voice command
    transcription = recognize_speech()
    if "right" in transcription:
        ball_position[0] += BALL_SPEED
    elif "left" in transcription:
        ball_position[0] -= BALL_SPEED
    elif "up" in transcription:
        ball_position[1] -= BALL_SPEED
    elif "down" in transcription:
        ball_position[1] += BALL_SPEED

    # Keep the ball within window bounds
    ball_position[0] = max(BALL_RADIUS, min(WINDOW_SIZE[0] - BALL_RADIUS, ball_position[0]))
    ball_position[1] = max(BALL_RADIUS, min(WINDOW_SIZE[1] - BALL_RADIUS, ball_position[1]))

    # Update the display
    pygame.display.flip()

pygame.quit()
