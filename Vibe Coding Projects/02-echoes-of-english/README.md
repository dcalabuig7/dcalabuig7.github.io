# Echoes of English

A narrative science-fiction RPG in which you progress by improving your English (playable build v0.3.0).

**▶ Play in your browser:** https://dcalabuig7.github.io/Vibe%20Coding%20Projects/02-echoes-of-english/

## How to play

1. Open the link above. It works in any modern browser on a computer, tablet or phone, with nothing to install.
2. Click **Wake up ›** to start. Read each scene and choose or write **your response**.
3. Missions take you through briefings, evidence and writing tasks. Your answers are checked for grammar, vocabulary, sentence construction, reading comprehension and use of context.
4. Use **Mission Control** to resume a mission, and the **ECHO Archive** to review vocabulary and phrasal verbs.
5. **Settings** has text size, reduced motion and adaptive difficulty.

## Saving your progress

- Progress is saved automatically **in this browser only**. Clearing browser data, or switching browser or device, starts from zero.
- Use **Export backup** regularly to download a backup file, and **Import backup…** to restore it, including on another device.

## Run it on your computer (optional)

The game is a pre-built web app. Browsers don't run it straight from a double-clicked file, so serve the folder locally:

1. Install [Python](https://www.python.org/downloads/), or use any static web server.
2. Open a terminal in this folder and run:
   ```bat
   python -m http.server 8000
   ```
3. Open http://localhost:8000 in your browser. Press Ctrl+C in the terminal to stop the server.

## Privacy

The game runs entirely in your browser. It doesn't ask for personal data, has no accounts, and sends nothing to any server. Saves stay in your browser's local storage.

## Files

This folder holds the **compiled build** (`index.html` + `assets/`). The minified JavaScript is generated, so edit the original source project and rebuild rather than changing these files by hand.
