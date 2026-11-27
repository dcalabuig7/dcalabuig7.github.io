# Vibe Coding Projects

Small projects built with AI-assisted "vibe coding". Each one has its own README with full details.

| # | Project | What it is | Open it |
|---|---------|------------|---------|
| 01 | [Click Counter](01-click-counter/) | A counter you can increase, decrease and reset | [▶ Open in browser](https://dcalabuig7.github.io/Vibe%20Coding%20Projects/01-click-counter/) |
| 02 | [Echoes Game](02-echoes-game/) | Sci-fi RPG where you progress by improving your English | [▶ Play in browser](https://dcalabuig7.github.io/Vibe%20Coding%20Projects/02-echoes-game/) |
| 03 | [System Transcriber](03-system-transcriber/) | Windows app that transcribes PC audio, YouTube links and files | Desktop app, [install below](#03--system-transcriber) |
| 04 | [Unit Converter](04-unit-converter/) | Converts length, weight and temperature units | [▶ Open in browser](https://dcalabuig7.github.io/Vibe%20Coding%20Projects/04-unit-converter/) |
| 05 | [Brave New World News Feed](05-brave-new-world-news-feed/) | Daily verified news in Spanish, English, Portuguese and Chinese, with an iPhone widget | [▶ Open in browser](https://dcalabuig7.github.io/Vibe%20Coding%20Projects/05-brave-new-world-news-feed/) |

---

## 01 · Click Counter

**▶ Open:** https://dcalabuig7.github.io/Vibe%20Coding%20Projects/01-click-counter/

- **Install:** nothing. It runs in any browser.
- **Use:** click **+** / **−** or press the ↑ / ↓ arrow keys, and click **Reset** to go back to 0. The count is remembered in your browser.
- **Offline:** download the repository (see below) and double-click `01-click-counter/index.html`.

More: [01-click-counter/README.md](01-click-counter/README.md)

## 02 · Echoes Game

**▶ Play:** https://dcalabuig7.github.io/Vibe%20Coding%20Projects/02-echoes-game/

- **Install:** nothing. It runs in any modern browser on computer, tablet or phone.
- **Use:** click **Wake up ›**, then read each scene and write or choose your response. Missions train grammar, vocabulary and reading. Progress saves automatically in your browser. Use **Export backup** / **Import backup…** to keep it safe or move it to another device.
- **Offline:** in the `02-echoes-game` folder run `python -m http.server 8000`, then open http://localhost:8000. (Double-clicking `index.html` doesn't work for this kind of web app.)

More: [02-echoes-game/README.md](02-echoes-game/README.md)

## 03 · System Transcriber

A Windows desktop program, so it can't run in a browser.
**Source:** [view on GitHub](https://github.com/dcalabuig7/dcalabuig7.github.io/tree/main/Vibe%20Coding%20Projects/03-system-transcriber)

- **Requirements:** Windows 10/11 and [Python 3.10+](https://www.python.org/downloads/) (tick "Add python.exe to PATH" when installing it).
- **Install:**
  1. [Download the repository ZIP](https://github.com/dcalabuig7/dcalabuig7.github.io/archive/refs/heads/main.zip) and extract it.
  2. Open `Vibe Coding Projects\03-system-transcriber` and double-click **`setup.bat`**.
  3. A **System Transcriber** shortcut appears on your desktop.
- **Use:** open the shortcut and pick a tab:
  - **Live: PC audio:** click **Start listening**, then play a video or join a call.
  - **YouTube link:** paste a link and click **Transcribe**.
  - **Audio / video file:** click **Browse...**, then **Transcribe**.

  Transcripts are saved as `.txt` (and `.srt` subtitles) in the `transcripts` folder. Everything runs offline on your PC.

More: [03-system-transcriber/README.md](03-system-transcriber/README.md)

## 04 · Unit Converter

**▶ Open:** https://dcalabuig7.github.io/Vibe%20Coding%20Projects/04-unit-converter/

- **Install:** nothing. It runs in any browser.
- **Use:** pick a category (length, weight or temperature), type a number, and choose the "From" and "To" units. The answer updates as you type. Click **⇄** to swap the units.
- **Offline:** download the repository (see below) and double-click `04-unit-converter/index.html`.

More: [04-unit-converter/README.md](04-unit-converter/README.md)

## 05 · Brave New World News Feed

**▶ Open:** https://dcalabuig7.github.io/Vibe%20Coding%20Projects/05-brave-new-world-news-feed/

- **Install:** nothing. It runs in any browser.
- **Use:** pick a language at the top right (Español, English, Português, 中文), pick a section, read the short summary, and click **Ver gráfico y detalles** to open the full story with its chart, sources and verification stamp. Use the search bar to find a topic.
- **iPhone widget:** paste `widget/BraveNewWorld-widget.js` into the Scriptable app and add a large Scriptable widget.
- **Offline:** download the repository (see below) and double-click `05-brave-new-world-news-feed/index.html`.

More: [05-brave-new-world-news-feed/README.md](05-brave-new-world-news-feed/README.md)

---

## Getting all the projects

- **ZIP:** https://github.com/dcalabuig7/dcalabuig7.github.io/archive/refs/heads/main.zip
- **Git:** `git clone https://github.com/dcalabuig7/dcalabuig7.github.io.git`
