import io
import json
import os
import re
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
from urllib.parse import quote
import wave

import numpy as np
import pygame
import pygetwindow as gw
from pynput import keyboard as pynput_kb
import pystray
from PIL import Image, ImageDraw
import requests
import sounddevice as sd
import websocket

try:
    import av
    HAS_PYAV = True
except ImportError:
    HAS_PYAV = False

CONFIG_FILE = "parrot_config.json"

DEFAULT_CONFIG = {
    "server_url": "http://127.0.0.1:8765",
    "username": "YourDiscordNick",
    "record_hotkey": "pause",      # Клавіша старт/стоп за замовчуванням (pause, f9, f10 тощо)
    "cancel_hotkey": "esc",        # Скасування/перезапис під час активного запису
    "auto_play_chat": True,
    "ignore_own_messages": True,
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "author_name" in data and "username" not in data:
                data["username"] = data["author_name"]
            return {**DEFAULT_CONFIG, **data}
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def encode_compressed_audio(audio_np: np.ndarray, sample_rate: int) -> tuple[bytes, str, str]:
    """Стискає запис в OGG (Opus/Vorbis) ~18-25 КБ за 5 сек; якщо PyAV немає — у легкий WAV."""
    if HAS_PYAV:
        for codec_name, rate in (("libopus", 16000), ("libvorbis", sample_rate)):
            try:
                out_buf = io.BytesIO()
                container = av.open(out_buf, mode="w", format="ogg")
                stream = container.add_stream(codec_name, rate=rate)
                stream.layout = "mono"
                stream.bit_rate = 24000

                mono_samples = audio_np.reshape(1, -1)
                frame = av.AudioFrame.from_ndarray(mono_samples, format="s16", layout="mono")
                frame.sample_rate = sample_rate

                for packet in stream.encode(frame):
                    container.mux(packet)
                for packet in stream.encode(None):
                    container.mux(packet)
                container.close()

                compressed = out_buf.getvalue()
                if compressed:
                    return compressed, "parrot_voice.ogg", "audio/ogg"
            except Exception:
                continue

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_np.tobytes())
    return wav_buffer.getvalue(), "parrot_voice.wav", "audio/wav"


def play_beep(freq_hz: int, duration_ms: int = 120, volume: float = 0.25):
    """Генерує чистий звуковий сигнал у навушники без зовнішніх аудіофайлів."""
    sample_rate = 44100
    t = np.linspace(0, duration_ms / 1000.0, int(sample_rate * duration_ms / 1000.0), False)
    wave_data = np.sin(freq_hz * 2 * np.pi * t) * volume
    fade = np.linspace(1.0, 0.0, len(wave_data))
    audio = np.int16(wave_data * fade * 32767)
    stereo = np.column_stack((audio, audio))
    sound = pygame.sndarray.make_sound(stereo)
    sound.play()


def get_active_discord_location() -> tuple[Optional[str], Optional[str]]:
    """
    Зчитує назву відкритого сервера та каналу із заголовка вікна Discord:
    '#channel | Server Name - Discord' -> (guild_name, channel_name)
    """
    for title in gw.getAllTitles():
        if "Discord" in title and "#" in title and "|" in title:
            cleaned = re.sub(r"\s*[-—–]\s*Discord\s*$", "", title, flags=re.IGNORECASE).strip()
            match = re.search(r"#([^\s|]+)\s*\|\s*(.+)$", cleaned)
            if match:
                channel_name = match.group(1).strip()
                guild_name = match.group(2).strip()
                return guild_name, channel_name
    return None, None


def normalize_key_name(key) -> str:
    """Перетворює натиснуту клавішу pynput на простий рядок ('pause', 'esc', 'f9', 'a' тощо)."""
    if hasattr(key, "name") and key.name:
        return key.name.lower()
    if hasattr(key, "char") and key.char:
        return key.char.lower()
    return str(key).replace("Key.", "").lower()


class ParrotClientApp:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        self.config = load_config()

        self.is_recording = False
        self.recorded_frames: list[np.ndarray] = []
        self.sample_rate = 16000
        self.stream: Optional[sd.InputStream] = None

        self.playback_queue: list[dict] = []
        self.playback_lock = threading.Lock()
        self.target_guild: Optional[str] = None
        self.target_channel: Optional[str] = None
        self.last_spoken_author: Optional[str] = None
        self.last_spoken_time: float = 0.0
        self.kb_listener: Optional[pynput_kb.Listener] = None
        self.active_ws = None

        self.start_hotkey_listener()
        threading.Thread(target=self.playback_worker, daemon=True).start()
        threading.Thread(target=self.ws_listener_worker, daemon=True).start()

    def start_hotkey_listener(self):
        if self.kb_listener:
            self.kb_listener.stop()

        def on_press(key):
            pressed = normalize_key_name(key)
            rec_key = self.config.get("record_hotkey", "pause").lower()
            cancel_key = self.config.get("cancel_hotkey", "esc").lower()

            if pressed == rec_key:
                self.toggle_recording()
            elif pressed == cancel_key:
                self.cancel_recording()

        self.kb_listener = pynput_kb.Listener(on_press=on_press)
        self.kb_listener.daemon = True
        self.kb_listener.start()

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_and_send_recording()

    def start_recording(self):
        guild_name, channel_name = get_active_discord_location()

        # Сувора перевірка: якщо відкритий не текстовий канал сервера — не пишемо і видаємо сигнал помилки
        if not guild_name or not channel_name:
            play_beep(220, 200)
            return

        self.target_guild = guild_name
        self.target_channel = channel_name
        self.recorded_frames = []
        self.is_recording = True

        play_beep(880, 90)
        threading.Timer(0.11, lambda: play_beep(1174, 110)).start()

        def audio_callback(indata, frames, time_info, status):
            if self.is_recording:
                self.recorded_frames.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            callback=audio_callback,
        )
        self.stream.start()

    def cancel_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.recorded_frames = []

        play_beep(440, 100)
        threading.Timer(0.11, lambda: play_beep(260, 180)).start()

    def stop_and_send_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        play_beep(784, 130)

        if not self.recorded_frames or not self.target_guild or not self.target_channel:
            return

        audio_np = np.concatenate(self.recorded_frames, axis=0)
        self.recorded_frames = []

        audio_bytes, filename, mime_type = encode_compressed_audio(audio_np, self.sample_rate)

        threading.Thread(
            target=self.upload_audio,
            args=(audio_bytes, filename, mime_type, self.target_guild, self.target_channel),
            daemon=True,
        ).start()

    def upload_audio(
        self,
        audio_bytes: bytes,
        filename: str,
        mime_type: str,
        guild_name: str,
        channel_name: str,
    ):
        url = f"{self.config['server_url'].rstrip('/')}/upload_voice"
        try:
            files = {"audio": (filename, audio_bytes, mime_type)}
            data = {
                "guild_name": guild_name,
                "channel_name": channel_name,
                "username": self.config["username"].strip().lstrip("@"),
            }
            resp = requests.post(url, data=data, files=files, timeout=45)
            if resp.status_code != 200:
                print(f"[Upload Error] {resp.status_code}: {resp.text}")
                play_beep(220, 250)
        except Exception as e:
            print(f"[Upload Exception] {e}")
            play_beep(220, 250)

    def ws_listener_worker(self):
        while True:
            ws_base = (
                self.config["server_url"]
                .rstrip("/")
                .replace("https://", "wss://")
                .replace("http://", "ws://")
            )
            user_q = quote(self.config.get("username", "").strip().lstrip("@"))
            ws_url = f"{ws_base}/ws?username={user_q}"
            try:
                ws = websocket.WebSocket()
                ws.connect(ws_url, timeout=20)
                self.active_ws = ws
                while True:
                    raw = ws.recv()
                    if not raw:
                        break
                    event = json.loads(raw)
                    ev_type = event.get("type")
                    if ev_type == "new_audio":
                        self.handle_incoming_audio(event)
                    elif ev_type == "manual_play":
                        with self.playback_lock:
                            self.playback_queue.insert(0, {
                                "audio_url": event["audio_url"],
                                "manual": True,
                            })
            except Exception:
                self.active_ws = None
                time.sleep(4)

    def handle_incoming_audio(self, event: dict):
        if not self.config.get("auto_play_chat", True):
            return

        active_guild, active_ch = get_active_discord_location()
        if not active_guild or not active_ch:
            return

        if (
            event.get("guild_name", "").strip().lower() != active_guild.lower()
            or event.get("channel_name", "").strip().lower() != active_ch.lower()
        ):
            return

        author_clean = event.get("clean_author") or event.get("author", "")
        ev_username = event.get("author_username", "").strip().lower()
        my_user = self.config.get("username", "").strip().lstrip("@").lower()
        if (
            self.config.get("ignore_own_messages", True)
            and (
                ev_username == my_user
                or event.get("author", "").lower() == my_user
                or author_clean.lower() == my_user
            )
        ):
            return

        with self.playback_lock:
            self.playback_queue.append(event)

    def _play_url_blocking(self, url: str, allow_interrupt_on_mute: bool = True):
        resp = requests.get(url, timeout=25)
        if resp.status_code == 200:
            audio_stream = io.BytesIO(resp.content)
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if allow_interrupt_on_mute and not self.config.get("auto_play_chat", True):
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.08)

    def playback_worker(self):
        while True:
            item = None
            with self.playback_lock:
                if self.playback_queue:
                    item = self.playback_queue.pop(0)

            if not item:
                time.sleep(0.15)
                continue

            while self.is_recording:
                time.sleep(0.15)

            try:
                if item.get("manual"):
                    self._play_url_blocking(item["audio_url"], allow_interrupt_on_mute=False)
                    continue

                author_id = item.get("clean_author") or item.get("author", "")
                author_tts_url = item.get("author_tts_url")
                is_already_named = item.get("is_voice_original", False)
                now = time.monotonic()

                need_announce_author = (
                    not is_already_named
                    and author_tts_url
                    and (
                        author_id != self.last_spoken_author
                        or (now - self.last_spoken_time) > 45.0
                    )
                )

                if need_announce_author:
                    self._play_url_blocking(author_tts_url, allow_interrupt_on_mute=True)

                self._play_url_blocking(item["audio_url"], allow_interrupt_on_mute=True)
                self.last_spoken_author = author_id
                self.last_spoken_time = time.monotonic()

            except Exception as e:
                print(f"[Playback Error] {e}")

    def open_settings_window(self):
        win = tk.Tk()
        win.title("Parrot Voice Client — Settings")
        win.geometry("420x315")
        win.resizable(False, False)

        pad = {"padx": 12, "pady": 6}

        ttk.Label(win, text="Parrot Server URL:").pack(anchor="w", **pad)
        server_var = tk.StringVar(value=self.config["server_url"])
        ttk.Entry(win, textvariable=server_var, width=50).pack(**pad)

        ttk.Label(win, text="Your Discord Username:").pack(anchor="w", **pad)
        user_var = tk.StringVar(value=self.config["username"])
        ttk.Entry(win, textvariable=user_var, width=50).pack(**pad)

        keys_frame = ttk.Frame(win)
        keys_frame.pack(fill="x", **pad)

        ttk.Label(keys_frame, text="Record Start/Stop Key:").grid(row=0, column=0, sticky="w")
        rec_var = tk.StringVar(value=self.config["record_hotkey"])
        ttk.Entry(keys_frame, textvariable=rec_var, width=16).grid(row=0, column=1, padx=8)

        ttk.Label(keys_frame, text="Cancel / Re-record Key:").grid(row=1, column=0, sticky="w", pady=4)
        cancel_var = tk.StringVar(value=self.config["cancel_hotkey"])
        ttk.Entry(keys_frame, textvariable=cancel_var, width=16).grid(row=1, column=1, padx=8, pady=4)

        autoplay_var = tk.BooleanVar(value=self.config["auto_play_chat"])
        ttk.Checkbutton(
            win, text="Auto-Play Chat (listen to open channel in background)", variable=autoplay_var
        ).pack(anchor="w", **pad)

        def on_save():
            self.config["server_url"] = server_var.get().strip()
            self.config["username"] = user_var.get().strip().lstrip("@")
            self.config["record_hotkey"] = rec_var.get().strip().lower()
            self.config["cancel_hotkey"] = cancel_var.get().strip().lower()
            self.config["auto_play_chat"] = autoplay_var.get()
            save_config(self.config)
            if self.active_ws:
                try:
                    self.active_ws.send(json.dumps({"username": self.config["username"]}))
                except Exception:
                    pass
            messagebox.showinfo("Parrot", "Settings saved!")
            win.destroy()

        ttk.Button(win, text="Save & Apply", command=on_save).pack(pady=10)
        win.mainloop()

    def run_tray(self):
        img = Image.new("RGB", (64, 64), color=(34, 139, 34))
        draw = ImageDraw.Draw(img)
        draw.ellipse((12, 12, 52, 52), fill=(255, 215, 0))

        def toggle_autoplay(icon, item):
            self.config["auto_play_chat"] = not self.config["auto_play_chat"]
            save_config(self.config)

        menu = pystray.Menu(
            pystray.MenuItem(
                "Auto-Play Chat",
                toggle_autoplay,
                checked=lambda item: self.config["auto_play_chat"],
            ),
            pystray.MenuItem(
                "Settings",
                lambda icon, item: threading.Thread(target=self.open_settings_window, daemon=True).start(),
            ),
            pystray.MenuItem("Exit", lambda icon, item: icon.stop()),
        )

        icon = pystray.Icon("Parrot", img, "Parrot Voice Client", menu)
        mode_info = "OGG Opus стиснення" if HAS_PYAV else "WAV 16kHz"
        print(f"[Parrot Client] Клієнт запущено в системному треї ({mode_info})!")
        if self.config["username"] == "YourDiscordNick":
            threading.Thread(target=self.open_settings_window, daemon=True).start()
        icon.run()


if __name__ == "__main__":
    app = ParrotClientApp()
    app.run_tray()