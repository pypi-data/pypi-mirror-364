#!/usr/bin/env python3

import pyautogui
import time

__version__ = "0.2.0"
__author__ = "Leon Bojanowski"
__email__ = "leongaborbojanowski04@gmail.com"

# Configuration
SQUARE_SIZE = 100
MOVE_DURATION = 0.25
INTERVAL = 60

# Enable safety feature (for emergency stop: move mouse to corner)
pyautogui.FAILSAFE = True


def move_in_square():
    # Save current position
    start_x, start_y = pyautogui.position()

    print(f"Starting square movement from position ({start_x}, {start_y})")

    # Move right
    pyautogui.moveTo(start_x + SQUARE_SIZE, start_y,
                     duration=MOVE_DURATION, tween=pyautogui.easeInOutQuad)

    # Move down
    pyautogui.moveTo(start_x + SQUARE_SIZE, start_y + SQUARE_SIZE,
                     duration=MOVE_DURATION, tween=pyautogui.easeInOutQuad)

    # Move left
    pyautogui.moveTo(start_x, start_y + SQUARE_SIZE,
                     duration=MOVE_DURATION, tween=pyautogui.easeInOutQuad)

    # Move up (back to start)
    pyautogui.moveTo(start_x, start_y,
                     duration=MOVE_DURATION, tween=pyautogui.easeInOutQuad)

    print("Square movement completed")


def start_patrol():
    print("MousePatrol started!")
    print("To exit: Press Ctrl+C or move the mouse to the upper left corner")
    print("-" * 50)

    try:
        while True:
            move_in_square()
            print(f"Waiting {INTERVAL} seconds until the next movement...")
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\nProgram terminated.")
    except pyautogui.FailSafeException:
        print("\nEmergency stop: Mouse moved to corner.")


def main():
    start_patrol()


if __name__ == "__main__":
    main()
