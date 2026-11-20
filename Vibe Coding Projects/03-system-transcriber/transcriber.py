"""
System Transcriber - core + command line
----------------------------------------
Modes:
  live  - transcribes whatever is playing on your PC (YouTube, calls, videos...)
  url   - downloads the audio of a YouTube (or other) link and transcribes it
  file  - transcribes a local audio/video file

Runs locally with faster-whisper (no internet needed after the model downloads once).
The desktop window (app.pyw) uses the same core functions defined here.
"""

import argparse
import datetime as dt
import os
import queue
import re
import sys
import tempfile
import threading
import time
import warnings
from pathlib import Path
from typing import Callable, Optional

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_IMPLICIT_TOKEN", "1")
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")

import numpy as np

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "transcripts"
WHISPER_RATE = 16000  # Whisper expects 16 kHz mono
MODELS = ["tiny", "base", "small", "medium"]

Log = Callable[[str], None]


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

_model_cache: dict = {}


def load_model(name: str, log: Log = print):
    """Load (or reuse an already loaded) Whisper model."""
    if name in _model_cache:
        return _model_cache[name]
    from faster_whisper import WhisperModel

    log(f"Loading model '{name}' (first time downloads it, this can take a minute)...")
    model = WhisperModel(name, device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
    # Warm-up so the first real chunk isn't extra slow
    list(model.transcribe(np.zeros(WHISPER_RATE, dtype=np.float32), language="en")[0])
    _model_cache.clear()  # keep only one model in memory (this PC has limited RAM)
    _model_cache[name] = model
    log("Model ready.")
    return model


def fmt_srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def fmt_clock(seconds: float) -> str:
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02}:{m:02}:{s:02}"


_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(10)), *(f"LPT{i}" for i in range(10))}


def safe_name(text: str, limit: int = 80) -> str:
    """Turn a video title / file name into a safe Windows file name (no paths, no device names)."""
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", text).strip().strip(".")
    text = text[:limit].strip() or "transcript"
    if text.split(".")[0].upper() in _RESERVED:
        text = f"_{text}"
    return text


def unique_base(base_name: str) -> str:
    """Avoid overwriting an earlier transcript with the same name."""
    candidate, n = base_name, 2
    while (OUT_DIR / f"{candidate}.txt").exists() or (OUT_DIR / f"{candidate}.srt").exists():
        candidate, n = f"{base_name} ({n})", n + 1
    return candidate


def lang_arg(language: Optional[str]):
    return None if language in (None, "", "auto") else language


# ----------------------------------------------------------------------------
# File / URL transcription
# ----------------------------------------------------------------------------

def transcribe_file(
    model,
    path: Path,
    language: str,
    base_name: str,
    on_line: Log = print,
    on_status: Log = print,
    should_stop: Callable[[], bool] = lambda: False,
) -> Path:
    """Transcribe an audio/video file. Writes .txt and .srt, returns the .txt path."""
    OUT_DIR.mkdir(exist_ok=True)
    base_name = unique_base(safe_name(base_name))
    txt_path = OUT_DIR / f"{base_name}.txt"
    srt_path = OUT_DIR / f"{base_name}.srt"

    segments, info = model.transcribe(
        str(path), language=lang_arg(language), vad_filter=True, beam_size=5
    )
    on_status(f"Language: {info.language} ({info.language_probability:.0%}) - "
              f"length {fmt_clock(info.duration)}")

    with open(txt_path, "w", encoding="utf-8") as txt, open(srt_path, "w", encoding="utf-8") as srt:
        n = 0
        for seg in segments:
            if should_stop():
                on_status("Stopped. Partial transcript saved.")
                break
            text = seg.text.strip()
            if not text:
                continue
            n += 1
            line = f"[{fmt_clock(seg.start)}] {text}"
            on_line(line)
            pct = (seg.end / info.duration * 100) if info.duration else 0
            on_status(f"Transcribing... {pct:.0f}%")
            txt.write(line + "\n")
            srt.write(f"{n}\n{fmt_srt_time(seg.start)} --> {fmt_srt_time(seg.end)}\n{text}\n\n")
            txt.flush()
            srt.flush()
        else:
            on_status(f"Done. Saved to {txt_path.name} and {srt_path.name}")
    return txt_path


def download_audio(url: str, folder: str, on_status: Log = print) -> tuple[Path, str]:
    """Download only the audio track of a video link. Returns (file path, title)."""
    import yt_dlp

    if not re.match(r"^https?://", url.strip(), re.IGNORECASE):
        raise ValueError("Only web links (http:// or https://) are allowed.")

    def hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            if total:
                on_status(f"Downloading audio... {d.get('downloaded_bytes', 0) / total:.0%}")

    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(folder, "audio.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "noplaylist": True,
        "max_filesize": 2 * 1024 ** 3,  # refuse absurdly large downloads (2 GB)
        "progress_hooks": [hook],
    }
    on_status("Downloading audio...")
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info))
    return path, info.get("title") or "video"


# ----------------------------------------------------------------------------
# Live capture (WASAPI loopback = "what you hear")
# ----------------------------------------------------------------------------

def list_loopback_devices() -> tuple[list[tuple[int, str]], Optional[int]]:
    """Returns ([(index, name), ...], default_index)."""
    import pyaudiowpatch as pyaudio

    with pyaudio.PyAudio() as p:
        devices = [(d["index"], d["name"]) for d in p.get_loopback_device_info_generator()]
        try:
            default = p.get_default_wasapi_loopback()["index"]
        except Exception:
            default = None
    return devices, default


def to_whisper_audio(chunk: np.ndarray, channels: int, rate: int) -> np.ndarray:
    """int16 interleaved -> float32 mono 16 kHz."""
    audio = chunk.astype(np.float32) / 32768.0
    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    if rate != WHISPER_RATE and len(audio):
        n_out = int(len(audio) * WHISPER_RATE / rate)
        x_old = np.linspace(0, 1, num=len(audio), endpoint=False)
        x_new = np.linspace(0, 1, num=n_out, endpoint=False)
        audio = np.interp(x_new, x_old, audio).astype(np.float32)
    return audio


class LiveSession:
    """Captures system audio and transcribes it in chunks on a background thread."""

    SILENCE_RMS = 0.004  # below this a block counts as silence

    def __init__(
        self,
        model,
        device_index: Optional[int] = None,
        language: str = "auto",
        min_chunk: float = 5.0,
        max_chunk: float = 15.0,
        beam: int = 1,
        on_line: Log = print,
        on_status: Log = print,
        debug: bool = False,
    ):
        self.model = model
        self.device_index = device_index
        self.language = lang_arg(language)
        self.min_chunk, self.max_chunk = min_chunk, max_chunk
        self.beam = beam
        self.on_line, self.on_status = on_line, on_status
        self.debug = debug

        OUT_DIR.mkdir(exist_ok=True)
        self.out_path = OUT_DIR / f"live_{dt.datetime.now():%Y%m%d_%H%M%S}.txt"
        self.device_name = ""
        self._q: "queue.Queue[tuple[float, np.ndarray]]" = queue.Queue()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_warn = 0.0

    # -- lifecycle ---------------------------------------------------------

    def start(self) -> None:
        import pyaudiowpatch as pyaudio

        self._pa = pyaudio.PyAudio()
        try:
            if self.device_index is not None:
                dev = self._pa.get_device_info_by_index(self.device_index)
            else:
                dev = self._pa.get_default_wasapi_loopback()
        except Exception as e:
            self._pa.terminate()
            raise RuntimeError(f"Could not find a loopback audio device: {e}") from e

        self.device_name = dev["name"]
        self.channels = int(dev["maxInputChannels"]) or 2
        self.rate = int(dev["defaultSampleRate"])

        def callback(in_data, frame_count, time_info, status):
            # Store the moment the audio was heard, so timestamps stay right even if we lag
            self._q.put((time.time(), np.frombuffer(in_data, dtype=np.int16).copy()))
            return (in_data, pyaudio.paContinue)

        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=dev["index"],
            frames_per_buffer=int(self.rate * 0.1),
            stream_callback=callback,
        )
        self.start_time = time.time()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self, wait: float = 60) -> None:
        try:
            self._stream.stop_stream()
            self._stream.close()
            self._pa.terminate()
        except Exception:
            pass
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=wait)

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    # -- processing --------------------------------------------------------

    def _transcribe_chunk(self, buf: list, buf_start: float, out) -> None:
        audio = to_whisper_audio(np.concatenate(buf), self.channels, self.rate)
        level = float(np.sqrt(np.mean(audio ** 2))) if len(audio) else 0.0
        if self.debug:
            self.on_status(f"[debug] chunk {len(audio) / WHISPER_RATE:.1f}s, level {level:.4f}")
        if len(audio) < WHISPER_RATE * 0.5 or level < self.SILENCE_RMS:
            return  # too short or pure silence

        t0 = time.time()
        segments, info = self.model.transcribe(
            audio,
            language=self.language,
            vad_filter=True,
            beam_size=self.beam,
            condition_on_previous_text=False,
        )
        text = " ".join(s.text.strip() for s in segments).strip()
        if self.debug:
            self.on_status(f"[debug] transcribed in {time.time() - t0:.1f}s -> {len(text)} chars")

        # Lock the language after the first confident detection (detecting every chunk is slow)
        if text and self.language is None and info.language_probability >= 0.7:
            self.language = info.language
            self.on_status(f"Language detected: {info.language} (locked in)")

        backlog = self._q.qsize() * 0.1
        if backlog > 20 and time.time() - self._last_warn > 60:
            self._last_warn = time.time()
            self.on_status(f"Falling behind by ~{backlog:.0f}s - try the 'tiny' model or close heavy apps")

        if text:
            line = f"[{fmt_clock(buf_start - self.start_time)}] {text}"
            self.on_line(line)
            out.write(line + "\n")
            out.flush()

    def _worker(self) -> None:
        buf: list = []
        buf_samples = 0
        buf_start = time.time()
        quiet_blocks = 0
        frames_per_s = self.rate * self.channels

        with open(self.out_path, "w", encoding="utf-8") as out:
            while not self._stop.is_set() or not self._q.empty():
                try:
                    heard_at, block = self._q.get(timeout=0.5)
                except queue.Empty:
                    if buf:  # nothing arriving -> flush what we have
                        self._transcribe_chunk(buf, buf_start, out)
                        buf, buf_samples, quiet_blocks = [], 0, 0
                    continue

                if not buf:
                    buf_start = heard_at
                buf.append(block)
                buf_samples += len(block)

                rms = float(np.sqrt(np.mean((block.astype(np.float32) / 32768.0) ** 2))) if len(block) else 0
                quiet_blocks = quiet_blocks + 1 if rms < self.SILENCE_RMS else 0

                seconds = buf_samples / frames_per_s
                # Cut at a natural pause once we have enough, or force-cut at max length
                if (seconds >= self.min_chunk and quiet_blocks >= 3) or seconds >= self.max_chunk:
                    self._transcribe_chunk(buf, buf_start, out)
                    buf, buf_samples, quiet_blocks = [], 0, 0

            if buf:
                self._transcribe_chunk(buf, buf_start, out)


# ----------------------------------------------------------------------------
# Command line
# ----------------------------------------------------------------------------

def run_live(args) -> None:
    if args.list_devices:
        devices, default = list_loopback_devices()
        print("Loopback devices (anything playing on these can be transcribed):\n")
        for idx, name in devices:
            print(f"  [{idx}] {name}{'   <- default' if idx == default else ''}")
        return

    model = load_model(args.model)
    session = LiveSession(
        model, args.device, args.language, args.min_chunk, args.max_chunk, args.beam,
        on_line=lambda s: print(s, flush=True),
        on_status=lambda s: print(f"  ({s})", flush=True),
        debug=args.debug,
    )
    try:
        session.start()
    except RuntimeError as e:
        sys.exit(f"{e}\nTry: transcribe live --list-devices")

    print(f"\nListening to: {session.device_name}")
    print(f"Saving to:    {session.out_path}")
    print("Play something (e.g. a YouTube video). Press Ctrl+C to stop.\n")
    print("-" * 60)
    try:
        while session.is_running():
            if args.duration and time.time() - session.start_time >= args.duration:
                print("\nTime limit reached.")
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopping... finishing the last chunk.")
    finally:
        session.stop()
        print(f"\nTranscript saved to: {session.out_path}")


def run_url(args) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        audio_path, title = download_audio(args.url, tmp)
        print(f"Got: {title}\n")
        model = load_model(args.model)
        out = transcribe_file(model, audio_path, args.language, safe_name(title))
        print(f"\nSaved: {out} (+ .srt)")


def run_file(args) -> None:
    path = Path(args.path)
    if not path.exists():
        sys.exit(f"File not found: {path}")
    model = load_model(args.model)
    out = transcribe_file(model, path, args.language, safe_name(path.stem))
    print(f"\nSaved: {out} (+ .srt)")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="transcribe",
        description="Transcribe audio playing on your PC, a YouTube link, or a file.",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--language", default="auto",
                        help="Language code like 'en' or 'es'. Default: auto-detect.")
    common.add_argument("--model", default="base", choices=MODELS,
                        help="Bigger = more accurate but slower. Default: base")

    live = sub.add_parser("live", parents=[common], help="Transcribe what's playing on your PC")
    live.add_argument("--device", type=int, default=None, help="Loopback device index (see --list-devices)")
    live.add_argument("--list-devices", action="store_true", help="Show available audio outputs and exit")
    live.add_argument("--min-chunk", type=float, default=5.0, help="Min seconds before cutting at a pause")
    live.add_argument("--max-chunk", type=float, default=15.0, help="Max seconds per chunk")
    live.add_argument("--duration", type=float, default=0, help="Stop automatically after N seconds")
    live.add_argument("--debug", action="store_true", help="Print chunk diagnostics")
    live.add_argument("--beam", type=int, default=1,
                      help="Beam size. 1 = fastest (default), 5 = a bit more accurate but much slower")
    live.set_defaults(func=run_live)

    url = sub.add_parser("url", parents=[common], help="Transcribe a YouTube (or other) link")
    url.add_argument("url")
    url.set_defaults(func=run_url)

    f = sub.add_parser("file", parents=[common], help="Transcribe a local audio/video file")
    f.add_argument("path")
    f.set_defaults(func=run_file)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
