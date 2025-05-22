import sys, os

if sys.platform == "win32":
    os.add_dll_directory(r"C:\Users\Raylin\Downloads\fluidsynth-2.4.6-win10-x64\bin")

import fluidsynth
fs = fluidsynth.Synth()
fs.start()
sfid = fs.sfload("assets/sounds/Antares_SoundFont.sf2")
fs.program_select(0, sfid, 0, 0)
fs.noteon(0, 60, 100)

import time
time.sleep(1)

fs.noteoff(0, 60)
fs.delete()
