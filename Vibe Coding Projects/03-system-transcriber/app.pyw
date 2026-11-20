"""
System Transcriber - desktop window.
Double-click the desktop shortcut (or this file) to open it; no terminal needed.
"""

import json
import os
import queue
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent

# pythonw has no console: send any stray output to a log file instead of crashing
if sys.stdout is None or sys.stderr is None:
    _log = open(HERE / "app.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = _log

import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:  # crisp text on high-DPI screens + own taskbar icon
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SystemTranscriber.App")
except Exception:
    pass

import transcriber as core

SETTINGS_FILE = HERE / "settings.json"

MODEL_CHOICES = [
    ("tiny  - fastest, least accurate", "tiny"),
    ("base  - recommended", "base"),
    ("small - more accurate, slower", "small"),
    ("medium - very slow on this PC", "medium"),
]
LANGUAGE_CHOICES = [
    ("Auto-detect", "auto"), ("English", "en"), ("Spanish", "es"), ("Catalan", "ca"),
    ("French", "fr"), ("German", "de"), ("Italian", "it"), ("Portuguese", "pt"),
    ("Dutch", "nl"), ("Russian", "ru"), ("Chinese", "zh"), ("Japanese", "ja"),
    ("Korean", "ko"), ("Arabic", "ar"),
]
DEFAULT_DEVICE_LABEL = "Default output (follows Windows)"

# Colors
BG = "#f6f7fb"
CARD = "#ffffff"
ACCENT = "#4f46e5"
ACCENT_DARK = "#4338ca"
DANGER = "#dc2626"
DANGER_DARK = "#b91c1c"
MUTED = "#6b7280"
TEXT = "#111827"
BORDER = "#e5e7eb"


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.events: "queue.Queue[tuple[str, object]]" = queue.Queue()
        self.job: str | None = None  # None | "live" | "url" | "file"
        self.session: core.LiveSession | None = None
        self.stop_flag = threading.Event()     # stops url/file jobs
        self.live_cancel = threading.Event()   # cancels a live start that is still loading
        self.live_lock = threading.Lock()
        self.no_sound_hint_shown = False
        self._live_error_shown = False
        self.last_saved: Path | None = None
        self.live_started_at: float | None = None
        self.settings = self._load_settings()

        root.title("System Transcriber")
        root.geometry("900x680")
        root.minsize(640, 480)
        root.configure(bg=BG)
        icon = HERE / "icon.ico"
        if icon.exists():
            try:
                root.iconbitmap(default=str(icon))
            except Exception:
                pass

        self._style()
        self._build()
        self._refresh_devices()
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.after(100, self._poll)

    # ------------------------------------------------------------------ UI

    def _style(self):
        s = ttk.Style()
        s.theme_use("clam")
        base_font = ("Segoe UI", 10)
        s.configure(".", background=BG, foreground=TEXT, font=base_font)
        s.configure("Card.TFrame", background=CARD)
        s.configure("Card.TLabel", background=CARD, foreground=TEXT)
        s.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        s.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 16))
        s.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
        s.configure("Status.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        s.configure("Live.TLabel", background=BG, foreground=DANGER, font=("Segoe UI Semibold", 9))

        s.configure("TNotebook", background=CARD, borderwidth=0, tabmargins=(12, 10, 12, 0))
        s.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 10),
                    background="#eef0f6", foreground=MUTED, borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", CARD)],
              foreground=[("selected", ACCENT)])

        s.configure("Accent.TButton", background=ACCENT, foreground="white",
                    font=("Segoe UI Semibold", 10), padding=(18, 8), borderwidth=0)
        s.map("Accent.TButton",
              background=[("disabled", "#c7c9f5"), ("active", ACCENT_DARK)],
              foreground=[("disabled", "white")])
        s.configure("Danger.TButton", background=DANGER, foreground="white",
                    font=("Segoe UI Semibold", 10), padding=(18, 8), borderwidth=0)
        s.map("Danger.TButton", background=[("active", DANGER_DARK)])
        s.configure("Ghost.TButton", background=CARD, foreground=TEXT, padding=(12, 6),
                    bordercolor=BORDER, borderwidth=1)
        s.map("Ghost.TButton", background=[("active", "#f3f4f6"), ("disabled", CARD)],
              foreground=[("disabled", "#9ca3af")])
        s.configure("TEntry", padding=6, fieldbackground="white", bordercolor=BORDER)
        s.configure("TCombobox", padding=5, fieldbackground="white", bordercolor=BORDER)

    def _build(self):
        pad = {"padx": 20}

        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", pady=(16, 8), **pad)
        ttk.Label(header, text="System Transcriber", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Turn anything you hear on your PC, a YouTube link or a file into text.",
                  style="Sub.TLabel").pack(anchor="w")

        # Source tabs
        card = ttk.Frame(self.root, style="Card.TFrame")
        card.pack(fill="x", **pad)
        self.tabs = ttk.Notebook(card)
        self.tabs.pack(fill="x")

        # Live tab
        live = ttk.Frame(self.tabs, style="Card.TFrame", padding=16)
        self.tabs.add(live, text="  Live: PC audio  ")
        ttk.Label(live, text="Listen to:", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.device_var = tk.StringVar()
        self.device_box = ttk.Combobox(live, textvariable=self.device_var, state="readonly", width=48)
        self.device_box.grid(row=0, column=1, sticky="ew", padx=8)
        self.refresh_btn = ttk.Button(live, text="Refresh", style="Ghost.TButton", command=self._refresh_devices)
        self.refresh_btn.grid(row=0, column=2)
        self.live_btn = ttk.Button(live, text="Start listening", style="Accent.TButton", command=self._toggle_live)
        self.live_btn.grid(row=0, column=3, padx=(12, 0))
        ttk.Label(live, text="Play a video, call or anything with speech. Text appears every few seconds.",
                  style="Muted.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))
        live.columnconfigure(1, weight=1)

        # URL tab
        url = ttk.Frame(self.tabs, style="Card.TFrame", padding=16)
        self.tabs.add(url, text="  YouTube link  ")
        ttk.Label(url, text="Link:", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url, textvariable=self.url_var)
        url_entry.grid(row=0, column=1, sticky="ew", padx=8)
        url_entry.bind("<Return>", lambda e: self._toggle_url())
        self.paste_btn = ttk.Button(url, text="Paste", style="Ghost.TButton", command=self._paste_url)
        self.paste_btn.grid(row=0, column=2)
        self.url_btn = ttk.Button(url, text="Transcribe", style="Accent.TButton", command=self._toggle_url)
        self.url_btn.grid(row=0, column=3, padx=(12, 0))
        ttk.Label(url, text="Downloads only the audio. No need to play the video. Also saves .srt subtitles.",
                  style="Muted.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))
        url.columnconfigure(1, weight=1)

        # File tab
        f = ttk.Frame(self.tabs, style="Card.TFrame", padding=16)
        self.tabs.add(f, text="  Audio / video file  ")
        ttk.Label(f, text="File:", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        self.file_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.file_var).grid(row=0, column=1, sticky="ew", padx=8)
        self.browse_btn = ttk.Button(f, text="Browse...", style="Ghost.TButton", command=self._browse)
        self.browse_btn.grid(row=0, column=2)
        self.file_btn = ttk.Button(f, text="Transcribe", style="Accent.TButton", command=self._toggle_file)
        self.file_btn.grid(row=0, column=3, padx=(12, 0))
        ttk.Label(f, text="mp3, mp4, wav, m4a, mkv, webm... Also saves .srt subtitles.",
                  style="Muted.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))
        f.columnconfigure(1, weight=1)

        # Settings row
        opts = ttk.Frame(self.root)
        opts.pack(fill="x", pady=(12, 8), **pad)
        ttk.Label(opts, text="Quality:").pack(side="left")
        self.model_var = tk.StringVar()
        self.model_box = ttk.Combobox(opts, textvariable=self.model_var, state="readonly", width=30,
                                      values=[label for label, _ in MODEL_CHOICES])
        self.model_box.pack(side="left", padx=(6, 18))
        ttk.Label(opts, text="Language:").pack(side="left")
        self.lang_var = tk.StringVar()
        self.lang_box = ttk.Combobox(opts, textvariable=self.lang_var, state="readonly", width=14,
                                     values=[label for label, _ in LANGUAGE_CHOICES])
        self.lang_box.pack(side="left", padx=6)

        model = self.settings.get("model", "base")
        self.model_var.set(next((l for l, v in MODEL_CHOICES if v == model), MODEL_CHOICES[1][0]))
        lang = self.settings.get("language", "auto")
        self.lang_var.set(next((l for l, v in LANGUAGE_CHOICES if v == lang), "Auto-detect"))
        self.model_box.bind("<<ComboboxSelected>>", lambda e: self._save_settings())
        self.lang_box.bind("<<ComboboxSelected>>", lambda e: self._save_settings())

        # Transcript area
        text_card = tk.Frame(self.root, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        text_card.pack(fill="both", expand=True, **pad)
        self.text = tk.Text(text_card, wrap="word", height=6, font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                            relief="flat", padx=16, pady=12, spacing1=2, spacing3=6,
                            insertbackground=TEXT, undo=False)
        scroll = ttk.Scrollbar(text_card, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.tag_configure("stamp", foreground="#9ca3af", font=("Consolas", 9))
        self.text.tag_configure("hint", foreground=MUTED, font=("Segoe UI", 10, "italic"))
        self._show_hint()

        # Action buttons
        actions = ttk.Frame(self.root)
        actions.pack(fill="x", pady=(8, 4), **pad)
        ttk.Button(actions, text="Copy all", style="Ghost.TButton", command=self._copy).pack(side="left")
        ttk.Button(actions, text="Clear", style="Ghost.TButton", command=self._clear).pack(side="left", padx=6)
        self.open_file_btn = ttk.Button(actions, text="Open saved transcript", style="Ghost.TButton",
                                        command=self._open_saved, state="disabled")
        self.open_file_btn.pack(side="right")
        ttk.Button(actions, text="Open transcripts folder", style="Ghost.TButton",
                   command=self._open_folder).pack(side="right", padx=6)

        # Status bar
        bar = ttk.Frame(self.root)
        bar.pack(fill="x", pady=(2, 10), **pad)
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(bar, textvariable=self.status_var, style="Status.TLabel").pack(side="left")
        self.live_var = tk.StringVar()
        ttk.Label(bar, textvariable=self.live_var, style="Live.TLabel").pack(side="right")

    # ------------------------------------------------------------ helpers

    def _load_settings(self) -> dict:
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_settings(self):
        self.settings.update(model=self._model(), language=self._language(),
                             device=self.device_var.get())
        try:
            SETTINGS_FILE.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _model(self) -> str:
        return dict(MODEL_CHOICES).get(self.model_var.get(), "base")

    def _language(self) -> str:
        return dict(LANGUAGE_CHOICES).get(self.lang_var.get(), "auto")

    def _post(self, kind: str, payload=None):
        self.events.put((kind, payload))

    def _show_hint(self):
        self.text.delete("1.0", "end")
        self.text.insert("end", "Your transcript will appear here.", "hint")
        self._has_hint = True

    def _append(self, line: str):
        if self._has_hint:
            self.text.delete("1.0", "end")
            self._has_hint = False
        at_bottom = self.text.yview()[1] > 0.98
        if line.startswith("[") and "] " in line:
            stamp, rest = line.split("] ", 1)
            self.text.insert("end", stamp + "]  ", "stamp")
            self.text.insert("end", rest + "\n")
        else:
            self.text.insert("end", line + "\n")
        if at_bottom:
            self.text.see("end")

    def _refresh_devices(self):
        try:
            devices, default = core.list_loopback_devices()
        except Exception as e:
            devices, default = [], None
            self.status_var.set(f"Could not list audio devices: {e}")
        self.devices = {DEFAULT_DEVICE_LABEL: None}
        for idx, name in devices:
            label = name.replace(" [Loopback]", "")
            self.devices[label] = idx
        self.device_box["values"] = list(self.devices)
        saved = self.settings.get("device")
        self.device_var.set(saved if saved in self.devices else DEFAULT_DEVICE_LABEL)

    def _set_busy(self, job: str | None):
        self.job = job
        busy = job is not None
        for w in (self.model_box, self.lang_box, self.device_box):
            w.configure(state="disabled" if busy else "readonly")
        self.refresh_btn.configure(state="disabled" if busy else "normal")
        for btn, name, idle_text, stop_text in (
            (self.live_btn, "live", "Start listening", "Stop listening"),
            (self.url_btn, "url", "Transcribe", "Stop"),
            (self.file_btn, "file", "Transcribe", "Stop"),
        ):
            if job == name:
                btn.configure(text=stop_text, style="Danger.TButton", state="normal")
            else:
                btn.configure(text=idle_text, style="Accent.TButton",
                              state="disabled" if busy else "normal")

    def _run_thread(self, target):
        def wrapper():
            try:
                target()
            except core.Cancelled:
                self._post("status", "Stopped.")
            except Exception as e:
                traceback.print_exc()
                self._post("error", str(e) or e.__class__.__name__)
            finally:
                self._post("finished")
        threading.Thread(target=wrapper, daemon=True).start()

    # --------------------------------------------------------------- live

    def _toggle_live(self):
        if self.job == "live":
            with self.live_lock:
                session = self.session
                if session is None:  # still loading the model: cancel the start
                    self.live_cancel.set()
            if session is None:
                self.live_btn.configure(state="disabled", text="Cancelling...")
                self.status_var.set("Cancelling... (waiting for the speech model to finish loading)")
                return
            self._stop_live(session)
            return

        self._save_settings()
        self.live_cancel.clear()
        self.no_sound_hint_shown = False
        self._set_busy("live")
        self.live_btn.configure(text="Cancel")
        self.status_var.set("Starting... loading the speech model.")
        model_name, language = self._model(), self._language()
        device_index = self.devices.get(self.device_var.get())

        def job():
            model = core.load_model(model_name, log=lambda s: self._post("status", s))
            if self.live_cancel.is_set():
                self._post("live_cancelled")
                return
            session = core.LiveSession(
                model, device_index, language,
                on_line=lambda s: self._post("line", s),
                on_status=lambda s: self._post("status", s),
            )
            session.start()
            with self.live_lock:  # Stop may have been pressed while the device was opening
                cancelled = self.live_cancel.is_set()
                if not cancelled:
                    self.session = session
            if cancelled:
                session.stop(wait=5)
                self._remove_if_empty(session)
                self._post("live_cancelled")
                return
            self._post("live_started", session)

        def wrapper():
            try:
                job()
            except Exception as e:
                traceback.print_exc()
                self._post("error", str(e))
                self._post("live_cancelled")
        threading.Thread(target=wrapper, daemon=True).start()

    def _stop_live(self, session):
        self.live_btn.configure(state="disabled", text="Stopping...")
        self.status_var.set("Stopping... finishing the current few seconds.")

        def stop():
            session.stop(wait=30)
            self._post("live_stopped", session)
        threading.Thread(target=stop, daemon=True).start()

    @staticmethod
    def _remove_if_empty(session) -> bool:
        try:
            if session.lines_written == 0 and session.out_path.stat().st_size == 0:
                session.out_path.unlink()
                return True
        except OSError:
            pass
        return False

    def _live_state(self, s) -> str:
        """Short description of what the live session is doing right now."""
        now = time.time()
        if s.last_block_at is None or now - s.last_block_at > 3:
            state = "no sound from this device"
        elif s.last_sound_at is None or now - s.last_sound_at > 5:
            state = "silence"
        elif s.transcribing:
            state = "hearing audio · transcribing"
        else:
            state = "hearing audio"
        behind = s.backlog_seconds()
        if behind >= 5:
            state += f" · {behind:.0f}s behind"
        return state

    # ---------------------------------------------------------- url / file

    def _paste_url(self):
        try:
            self.url_var.set(self.root.clipboard_get().strip())
        except tk.TclError:
            pass

    def _toggle_url(self):
        if self.job == "url":
            self.stop_flag.set()
            self.status_var.set("Stopping...")
            return
        if self.job:
            return
        url = self.url_var.get().strip()
        if not url.startswith(("http://", "https://")):
            messagebox.showinfo("System Transcriber", "Paste a link that starts with https://")
            return
        self._start_offline_job("url", url)

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Choose an audio or video file",
            filetypes=[("Audio / video", "*.mp3 *.mp4 *.wav *.m4a *.mkv *.webm *.ogg *.flac *.mov *.aac *.wma"),
                       ("All files", "*.*")],
        )
        if path:
            self.file_var.set(path)

    def _toggle_file(self):
        if self.job == "file":
            self.stop_flag.set()
            self.status_var.set("Stopping...")
            return
        if self.job:
            return
        path = Path(self.file_var.get().strip().strip('"'))
        if not path.is_file():
            messagebox.showinfo("System Transcriber", "Choose a file first (Browse...).")
            return
        self._start_offline_job("file", path)

    def _start_offline_job(self, kind: str, source):
        self._save_settings()
        self.stop_flag.clear()
        self._set_busy(kind)
        model_name, language = self._model(), self._language()
        status = lambda s: self._post("status", s)

        def job():
            if kind == "url":
                with tempfile.TemporaryDirectory() as tmp:
                    audio, title = core.download_audio(source, tmp, on_status=status,
                                                       should_stop=self.stop_flag.is_set)
                    if self.stop_flag.is_set():
                        raise core.Cancelled()
                    self._post("line", f"--- {title} ---")
                    model = core.load_model(model_name, log=status)
                    if self.stop_flag.is_set():
                        raise core.Cancelled()
                    status("Transcribing... (the first lines can take a moment)")
                    out = core.transcribe_file(model, audio, language, core.safe_name(title),
                                               on_line=lambda s: self._post("line", s),
                                               on_status=status, should_stop=self.stop_flag.is_set)
            else:
                self._post("line", f"--- {source.name} ---")
                model = core.load_model(model_name, log=status)
                if self.stop_flag.is_set():
                    raise core.Cancelled()
                status("Transcribing... (the first lines can take a moment)")
                out = core.transcribe_file(model, source, language, core.safe_name(source.stem),
                                           on_line=lambda s: self._post("line", s),
                                           on_status=status, should_stop=self.stop_flag.is_set)
            self._post("saved", out)

        self._run_thread(job)

    # ------------------------------------------------------------ actions

    def _copy(self):
        if self._has_hint:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text.get("1.0", "end").strip())
        self.status_var.set("Transcript copied to clipboard.")

    def _clear(self):
        self._show_hint()

    def _open_folder(self):
        core.OUT_DIR.mkdir(exist_ok=True)
        os.startfile(core.OUT_DIR)

    def _open_saved(self):
        if self.last_saved and self.last_saved.exists():
            os.startfile(self.last_saved)

    # ------------------------------------------------------- event loop

    def _poll(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "line":
                    self._append(payload)
                elif kind == "status":
                    self.status_var.set(payload)
                elif kind == "error":
                    self.status_var.set(f"Error: {payload}")
                    messagebox.showerror("System Transcriber", str(payload))
                elif kind == "saved":
                    self.last_saved = payload
                    self.open_file_btn.configure(state="normal")
                elif kind == "live_started":
                    self.live_started_at = time.time()
                    self._set_busy("live")  # turns the button into "Stop listening"
                    self.status_var.set(f"Listening to {payload.device_name.replace(' [Loopback]', '')}. "
                                        f"Saving to {payload.out_path.name}")
                elif kind == "live_stopped":
                    session = payload
                    if self._remove_if_empty(session):
                        self.status_var.set("Stopped. Nothing was transcribed (no speech was heard).")
                    else:
                        self.last_saved = session.out_path
                        self.open_file_btn.configure(state="normal")
                        self.status_var.set(f"Stopped. Saved to {session.out_path.name}")
                    self._reset_live()
                elif kind == "live_cancelled":
                    if not self.status_var.get().startswith("Error"):
                        self.status_var.set("Cancelled.")
                    self._reset_live()
                elif kind == "finished":
                    self._set_busy(None)
        except queue.Empty:
            pass

        s = self.session
        if self.live_started_at and s is not None:
            if s.error and not s.is_running() and not self._live_error_shown:
                self._live_error_shown = True
                messagebox.showerror("System Transcriber", f"Live transcription stopped:\n{s.error}")
                self._stop_live(s)
            dot = "●" if int(time.time() * 2) % 2 else "○"
            self.live_var.set(f"{dot} LIVE  {core.fmt_clock(time.time() - self.live_started_at)}"
                              f"  ·  {self._live_state(s)}")
            # Explain the most common reason for an empty transcript
            silent_for = time.time() - (s.last_sound_at or self.live_started_at)
            if silent_for > 10 and s.lines_written == 0 and not self.no_sound_hint_shown:
                self.no_sound_hint_shown = True
                self.status_var.set(
                    f"No sound heard from {s.device_name.replace(' [Loopback]', '')} yet. "
                    f"Is the video playing (not muted), and on this device? Check 'Listen to'.")

        self.root.after(100, self._poll)

    def _reset_live(self):
        with self.live_lock:
            self.session = None
        self.live_started_at = None
        self._live_error_shown = False
        self.live_var.set("")
        self._set_busy(None)

    def _on_close(self):
        if self.job:
            if not messagebox.askyesno("System Transcriber",
                                       "A transcription is running. Stop it and close?\n"
                                       "(What has been transcribed so far is already saved.)"):
                return
            self.stop_flag.set()
            self.live_cancel.set()
            with self.live_lock:
                session = self.session
            if session:
                session.stop(wait=5)
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
