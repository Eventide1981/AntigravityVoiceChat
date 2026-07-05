import threading
import time
import speech_recognition as sr
import pyautogui
import keyboard
import sounddevice as sd
import numpy as np
import wave
import os
import pyttsx3
import pygetwindow as gw
from collections import deque

# ==========================================
# Global State & Configurations
# ==========================================
def is_bot_speaking():
    lock_file = os.path.join(os.environ.get('TEMP', '.'), 'antigravity_speaking.lock')
    return os.path.exists(lock_file)

current_mode = 'ptt'
mode_lock = threading.Lock()

# Audio Configurations
FS = 44100
CHUNK_DURATION = 0.1 # 100ms
CHUNK_SAMPLES = int(FS * CHUNK_DURATION)
ENERGY_THRESHOLD = 100 # RMS amplitude threshold for speech detection
SILENCE_TIMEOUT = 6.0 # seconds of silence before finalizing (increased for rambling)
MAX_RECORDING_TIME = 120.0 # max seconds to listen (increased to 2 minutes)



# ==========================================
# Speech-to-Text (STT) Logic
# ==========================================
def calculate_rms(indata):
    """Calculate Root Mean Square (RMS) energy of an audio chunk."""
    data = indata.astype(np.float32)
    return np.sqrt(np.mean(data**2))

def process_audio(recording):
    """Save audio to WAV, transcribe it, and type it into the UI."""
    if not recording:
        return
        
    audio_data = np.concatenate(recording, axis=0)
    temp_wav = 'temp_audio.wav'
    
    # Save WAV
    with wave.open(temp_wav, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(FS)
        wf.writeframes(audio_data.tobytes())
        
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(temp_wav) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print(f"[STT] Transcribed: {text}")
            
            # --- WINDOW SWITCHING LOGIC ---
            try:
                original_window = gw.getActiveWindow()
                ag_windows = [w for w in gw.getAllWindows() if 'antigravity' in w.title.lower()]
                
                if ag_windows:
                    ag_window = ag_windows[0]
                    if ag_window.isMinimized:
                        ag_window.restore()
                    
                    ag_window.activate()
                    time.sleep(0.1) # Wait for focus
                    
                    pyautogui.typewrite(text)
                    pyautogui.press('enter')
                    
                    time.sleep(0.1) # Wait for enter to register
                    
                    # Switch back to the user's previous window (e.g. Blender)
                    if original_window and original_window._hWnd != ag_window._hWnd:
                        original_window.activate()
                else:
                    print("[STT Warning] Could not find the Antigravity window! Typing in the current window instead.")
                    pyautogui.typewrite(text)
                    pyautogui.press('enter')
                    
            except Exception as e:
                print(f"[STT Window Switching Error] {e}")
                # Fallback to just typing
                pyautogui.typewrite(text)
                pyautogui.press('enter')
            # ------------------------------
            
    except sr.UnknownValueError:
        # Ignore silence or unintelligible audio
        print("[STT] (Unintelligible / Silence ignored)")
    except sr.RequestError as e:
        print(f"[STT Error] Speech Recognition service error: {e}")
    except Exception as e:
        print(f"[STT Error] {e}")
        
    if os.path.exists(temp_wav):
        os.remove(temp_wav)

def stt_worker():
    """Worker thread for the STT loop handling both modes."""
    print("\n" + "=" * 50)
    print("BASIC CONTROLS:")
    print(" [F9]          : Toggle between 'Push-to-Talk' and 'Continuous' modes")
    print(" [Ctrl+Space]  : Hold to speak in Push-to-Talk mode")
    print("=" * 50 + "\n")
    
    while True:
        with mode_lock:
            mode = current_mode
            
        if mode == 'ptt':
            # Wait for PTT hotkey
            try:
                keyboard.wait('ctrl+space')
            except Exception:
                time.sleep(0.1)
                continue
                
            if is_bot_speaking():
                continue # ignore microphone while bot is speaking
                
            print("\n[STT - PTT] Recording... (Release Ctrl+Space to stop)")
            recording = []
            
            def ptt_callback(indata, frames, time_info, status):
                recording.append(indata.copy())
                
            with sd.InputStream(samplerate=FS, channels=1, dtype='int16', blocksize=CHUNK_SAMPLES, callback=ptt_callback):
                while keyboard.is_pressed('ctrl+space'):
                    time.sleep(0.05)
                    
            print("[STT - PTT] Processing...")
            process_audio(recording)
            
        elif mode == 'continuous':
            if is_bot_speaking():
                time.sleep(0.5)
                continue
                
            recording = []
            is_recording = False
            silence_start = None
            lookback = deque(maxlen=10) # 1 second lookback buffer
            
            try:
                with sd.InputStream(samplerate=FS, channels=1, dtype='int16', blocksize=CHUNK_SAMPLES) as stream:
                    while True:
                        with mode_lock:
                            if current_mode != 'continuous':
                                break
                        if is_bot_speaking():
                            break
                            
                        indata, overflowed = stream.read(CHUNK_SAMPLES)
                        rms = calculate_rms(indata)
                        
                        if not is_recording:
                            lookback.append(indata.copy())
                            if rms > ENERGY_THRESHOLD:
                                print("\n[STT - Cont] Listening...")
                                is_recording = True
                                recording.extend(list(lookback))
                                silence_start = None
                        else:
                            recording.append(indata.copy())
                            if rms < ENERGY_THRESHOLD:
                                if silence_start is None:
                                    silence_start = time.time()
                                elif time.time() - silence_start > SILENCE_TIMEOUT:
                                    print(f"[STT - Cont] Silence detected ({SILENCE_TIMEOUT}s). Finalizing...")
                                    break
                            else:
                                silence_start = None
                                
                            if len(recording) * CHUNK_DURATION > MAX_RECORDING_TIME:
                                print(f"[STT - Cont] Reached max limit ({MAX_RECORDING_TIME}s). Finalizing...")
                                break
                                
                if is_recording and len(recording) > 0:
                    process_audio(recording)
                    time.sleep(0.5) # Brief cooldown
                    
            except Exception as e:
                print(f"[STT Worker Error] {e}")

def toggle_mode():
    """Toggle between PTT and Continuous mode."""
    global current_mode
    with mode_lock:
        if current_mode == 'ptt':
            current_mode = 'continuous'
            print("\n>>> MODE CHANGED: CONTINUOUS (Turn-Taking) <<<")
            print(">>> The mic will automatically listen for you to speak, and pause when the bot speaks. <<<")
        else:
            current_mode = 'ptt'
            print("\n>>> MODE CHANGED: PUSH-TO-TALK <<<")

# ==========================================
# Main Execution
# ==========================================
def main():
    print("============================================================")
    print("Starting Unified Antigravity Voice Chat Extension")
    print("============================================================")
    
    # Start STT worker
    t = threading.Thread(target=stt_worker, daemon=True)
    t.start()
    
    # Setup global hotkey for Mode Toggle (F9)
    keyboard.on_press_key('F9', toggle_mode, suppress=True)
    
    print("\n==================================================")
    print("BASIC CONTROLS:")
    print(" [F9]          : Toggle between 'Push-to-Talk' and 'Continuous' modes")
    print(" [Ctrl+Space]  : Hold to speak in Push-to-Talk mode")
    print("==================================================\n")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
