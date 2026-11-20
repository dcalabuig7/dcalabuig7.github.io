# System Transcriber

A Windows desktop app that turns speech into text, locally and offline, using [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

| Tab | What it does |
|-----|--------------|
| **Live: PC audio** | Transcribes whatever is playing on your PC (YouTube, calls, videos...) as it plays |
| **YouTube link** | Downloads the audio of a link and transcribes it, without playing the video |
| **Audio / video file** | Transcribes an mp3, mp4, wav, m4a, mkv... file |

> This is a **desktop program**, not a web page, so it can't run in the browser.
> Source code: [github.com/dcalabuig7/dcalabuig7.github.io/.../03-system-transcriber](https://github.com/dcalabuig7/dcalabuig7.github.io/tree/main/Vibe%20Coding%20Projects/03-system-transcriber)

## Requirements

- Windows 10 or 11
- [Python](https://www.python.org/downloads/) 3.10 or newer (tested with 3.14). During installation, tick **"Add python.exe to PATH"**.
- About 1 GB of free disk space (components plus the speech model)

## Install

1. Download the repository: [**Download ZIP**](https://github.com/dcalabuig7/dcalabuig7.github.io/archive/refs/heads/main.zip). Extract it, then open `Vibe Coding Projects\03-system-transcriber`.
   (Or use Git: `git clone https://github.com/dcalabuig7/dcalabuig7.github.io.git`)
2. Double-click **`setup.bat`**. It creates a private Python environment, installs the components and puts a **System Transcriber** shortcut on your desktop.

## Use

Double-click **System Transcriber** on the desktop.

- **Live:** leave "Listen to" on *Default output* and click **Start listening**. Then play a video or join a call. Text appears every few seconds. Click **Stop listening** when you're done.
- **YouTube link:** paste the link, click **Transcribe**, and wait. Progress is shown at the bottom.
- **File:** click **Browse...**, choose the file, and click **Transcribe**.

Every transcript is saved automatically in the `transcripts\` folder (**Open transcripts folder** button): a `.txt` file with timestamps, plus a `.srt` subtitle file for links and files.

**Quality**: `base` is the recommended default. `tiny` is faster, and `small` is more accurate but slower. **Language** defaults to auto-detect; choose a language if detection gets it wrong.

## Command line (optional)

```bat
transcribe live                                   :: Ctrl+C to stop
transcribe live --list-devices
transcribe url https://www.youtube.com/watch?v=...
transcribe file "C:\path\to\video.mp4" --model small --language es
```

## Tips and limits

- Live mode records the device you choose (default: your current speakers or headphones). Every sound gets transcribed, including notifications.
- **If nothing appears in live mode**, check the status bar. It shows `hearing audio`, `silence` or `no sound from this device`.
  - **Windows output muted:** most drivers then capture only silence. Lower the volume instead of muting.
  - **Wrong device:** the video plays on a different device than the one in "Listen to" (for example, Bluetooth headphones that just disconnected). Click **Refresh** and pick the right one.
- Live text appears a few seconds after the speech, in chunks of up to 10 seconds.
- The app runs at *above normal* Windows priority while working. On a busy PC (browser, Steam, chat apps), normal priority made speech recognition 15–30× slower.
- If the PC still can't keep up, live mode **skips ahead** to stay current and marks the gap as `[... N s skipped ...]` instead of falling minutes behind. Choose Quality `tiny` or close heavy apps to avoid gaps.
- **Stop** ends capture immediately and finishes only the last few seconds.
- If YouTube links stop working, update the downloader:
  `.venv\Scripts\python.exe -m pip install -U yt-dlp`
- Only transcribe calls or meetings when everyone involved agrees to it.

## Privacy and security

- Everything runs on your PC. Audio and transcripts are never uploaded. The internet is used only to download the speech model once and to fetch audio from links you paste.
- `transcripts/`, `settings.json` and `app.log` are excluded from Git, so they are never published.
- Only `http(s)` links are accepted, downloads are capped at 2 GB, and file names from video titles are sanitized.
- Dependencies are pinned to tested versions in `requirements.txt` (checked with `pip-audit`: no known vulnerabilities on 2026-11-20).

## Files

| File | Purpose |
|------|---------|
| `app.pyw` | The desktop window |
| `transcriber.py` | Capture and transcription engine, plus the command line |
| `setup.bat`, `create-shortcut.ps1` | One-time install and desktop shortcut |
| `transcribe.bat` | Command-line launcher |
| `requirements.txt` | Pinned Python dependencies |
| `icon.ico` | App icon |
