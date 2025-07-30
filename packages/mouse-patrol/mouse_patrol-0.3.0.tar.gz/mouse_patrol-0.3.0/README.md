# MousePatrol

**Python utility to automatically & regularly move your mouse. Use it to prevent going idle, trigger screensaver etc.**

## Features

- Moves your mouse in a smooth square pattern at set intervals
- Prevents your computer from going idle or locking
- Simple, lightweight, and easy to use
- Emergency stop: move your mouse to the top-left corner or press Ctrl+C

## Installation

### Install from PyPI (Recommended)

```sh
pip install mouse-patrol
```

### Manual Installation

1. Clone this repository:

   ```sh
   git clone https://github.com/f1nal04/mouse-patrol.git
   cd mouse-patrol
   ```

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

## Usage

### If installed via pip:

```sh
mouse-patrol
```

### If using manual installation:

```sh
python mouse_patrol/main.py
```

To stop the program, press `Ctrl+C` or move your mouse to the top-left corner of the screen.

## Disclaimer

Use responsibly. This tool simulates mouse movement and may interfere with other automation or security policies.
