# KeyPractice

KeyPractice is a slim, cross-platform terminal-based typing trainer. It allows you to practice custom exercises defined in YAML files, and tracks your analytics (best times, streaks, session data, etc.).

## Features
- Easily extensible: add your own YAML exercise files
- Tracks your best times, streaks, and session history
- Tracks speed (WPM), error counts, and improvements over time
- View analytics for each exercise (best time, best speed, lowest errors, streak, last 5 sessions)
- Minimal dependencies (just Python and PyYAML)
- Works on Windows, Mac, and Linux

## Installation

1. Ensure you have Python 3.7+ installed.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. (Optional) Install as a module:
   ```sh
   pip install .
   # or
   pipx install .
   ```

## Usage

1. Place your YAML exercise files in the `exercises/` folder.
2. Run KeyPractice:
   ```sh
   python -m keypractice
   # or, if installed:
   keypractice
   ```
3. Select an exercise and start practicing!
4. To view analytics for an exercise, choose the analytics option in the menu.

## Creating Custom YAML Exercises

Each exercise is a YAML file in the `exercises/` folder. Example:

```yaml
name: Home Row
items:
  - a
  - s
  - d
  - f
  - j
  - k
  - l
  - ;
```

- `name`: The name of the exercise (shown in the menu).
- `items`: A list of strings to practice typing. Each item will be shown one at a time.

You can create as many YAML files as you like. Each will appear as a separate exercise in the menu.

## Analytics
- Best time per exercise
- Best speed (WPM)
- Lowest error count
- Streaks (consecutive days practiced)
- Session history (last 5 sessions)
- Session dates
- Improvements over time

## Contributing
Feel free to submit issues or pull requests for new features, bug fixes, or new exercise sets!
