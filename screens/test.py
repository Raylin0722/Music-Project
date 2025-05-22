import time
import os
import sys
import fluidsynth
from pynput import keyboard

# 初始化 FluidSynth
if sys.platform == "win32":
    os.add_dll_directory(r"C:\Users\Raylin\Downloads\fluidsynth-2.4.6-win10-x64\bin")

fs = fluidsynth.Synth()
fs.start()

sfid = fs.sfload("assets/sounds/Antares_SoundFont.sf2")
fs.program_select(0, sfid, 0, 0)

# 音域限制
MIN_MIDI = 21  # A0
MAX_MIDI = 108  # C8

# 鍵盤對應結構
white_keys = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']
black_keys = ['w', 'e', 't', 'y', 'u']  # 和白鍵排列對應

# 對應的半音位移（從 C 開始）
white_offsets = [0, 2, 4, 5, 7, 9, 11, 12]
black_offsets = [1, 3, 6, 8, 10]

# 可變音域起點（八度計算用）
base_note = 60  # C4 開始

pressed_notes = {}

def play_note(key_char):
    global base_note
    key_char = key_char.lower()
    note = None

    if key_char in white_keys:
        idx = white_keys.index(key_char)
        note = base_note + white_offsets[idx]
    elif key_char in black_keys:
        idx = black_keys.index(key_char)
        note = base_note + black_offsets[idx]

    if note is not None and MIN_MIDI <= note <= MAX_MIDI:
        fs.noteon(0, note, 100)
        pressed_notes[key_char] = (note, time.time())

def stop_note(key_char):
    key_char = key_char.lower()
    if key_char in pressed_notes:
        note, start_time = pressed_notes.pop(key_char)
        fs.noteoff(0, note)
        duration = time.time() - start_time
        print(f"🎵 {note} ({key_char}) played for {duration:.2f} sec")

def shift_octave(direction):
    global base_note
    shift = 12 * direction
    new_base = base_note + shift
    if MIN_MIDI <= new_base <= MAX_MIDI - 12:
        base_note = new_base
        print(f"🎹 音域切換至: {midi_note_to_name(base_note)} ~ {midi_note_to_name(base_note + 12)}")
    else:
        print("❗ 已達到音域邊界，無法再移動")

def midi_note_to_name(n):
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return f"{names[n % 12]}{(n // 12) - 1}"

def on_press(key):
    try:
        k = key.char.lower()

        # 音域切換
        if k == 'z':
            shift_octave(-1)
        elif k == 'x':
            shift_octave(1)
        else:
            if k not in pressed_notes:
                play_note(k)

    except AttributeError:
        pass

def on_release(key):
    try:
        k = key.char.lower()
        stop_note(k)
    except AttributeError:
        pass

    if key == keyboard.Key.esc:
        fs.delete()
        print("🎵 結束")
        return False

print("🎹 可彈奏！使用 A~K / WERTY 彈 8+5 鍵，Z/X 切八度，ESC 離開")
print(f"當前音域：{midi_note_to_name(base_note)} ~ {midi_note_to_name(base_note + 12)}")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
