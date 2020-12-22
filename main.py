import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

import threading
import time

import ffmpeg
from wand.image import Image
from os import makedirs, listdir
from os.path import abspath, dirname
import shutil

scriptFolder = dirname(abspath(__file__))

if len(sys.argv) != 2:
    print("Wrong arguments")
    exit()
currentVideo = sys.argv[1]
currentVideoPath = abspath(currentVideo)
if '/' in currentVideo: currentVideo = currentVideo[currentVideo.rfind('/')+1:]
outVideoPath = currentVideoPath[:currentVideoPath.rfind('.')]+"_distorted.mp4"
distortionPercentage = 80
progressValue = 0
distortAudio = False

probe = ffmpeg.probe(currentVideoPath)
videoInfo = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
videoW = videoInfo[0]['width']
videoH = videoInfo[0]['height']
videoFPS = videoInfo[0]['r_frame_rate'].split('/')
videoFPS = int(int(videoFPS[0]) / int(videoFPS[1]))
fpsValue = videoFPS

builder = Gtk.Builder()
builder.add_from_file(f"{scriptFolder}/main.glade")

progress = builder.get_object("progress")
distortionWidget = builder.get_object("distortionWidget")
framerateWidget = builder.get_object("framerateWidget")
activateButton = builder.get_object("activateButton")
audioCheck = builder.get_object("audioCheck")

framerateWidget.set_value(fpsValue)

def toggleInterface(toggle):
    distortionWidget.set_sensitive(toggle)
    framerateWidget.set_sensitive(toggle)
    activateButton.set_sensitive(toggle)
    audioCheck.set_sensitive(toggle)

def closeApp():
    Gtk.main_quit()

def distortify():
    GLib.idle_add(toggleInterface, False)
    # Reset progress
    progressValue = 0
    progress.set_fraction(progressValue)
    print(f"Video: {currentVideo} ({videoW}x{videoH}@{videoFPS})")
    print(f"Distortion: {distortionPercentage}%")
    print(f"FPS: {fpsValue}")
    # Extract Frames
    shutil.rmtree(f'{scriptFolder}/frames', ignore_errors=True)
    makedirs(f'{scriptFolder}/frames', exist_ok=True)
    (
        ffmpeg
        .input(currentVideoPath)
        .output(f"{scriptFolder}/frames/frame%04d.png", r=fpsValue)
        .run(quiet=True)
    )
    frames = listdir(f"{scriptFolder}/frames")
    frames.sort()
    framesN = len(frames)
    deltaFramesN = 1 / framesN
    print(f"Total Frames: {framesN}")
    # Distort Frames
    dSize = (distortionPercentage / framesN) / 100
    iSize = 1
    for frame in frames:
        if not frame.endswith('png'): continue
        with Image(filename=f"{scriptFolder}/frames/{frame}") as i:
            i.liquid_rescale(width=int(videoW*iSize), height=int(videoH*iSize))
            i.resize(width=videoW, height=videoH)
            i.save(filename=f"{scriptFolder}/frames/{frame}")
            progressValue += deltaFramesN
            progress.set_fraction(progressValue)
        iSize -= dSize
    print("Done")
    # Prepare video stream
    videoStream = ffmpeg.input(f'{scriptFolder}/frames/*.png', pattern_type='glob', framerate=fpsValue)
    # Prepare audio stream
    if distortAudio:
        audioStream = (
            ffmpeg
            .input(currentVideoPath)
            .audio
            .filter('vibrato', f=10.0, d=0.5)
            .filter('aformat', 's16p')
        )
        finalOutput = ffmpeg.concat(videoStream.video, audioStream, v=1, a=1)
    else:
        finalOutput = videoStream
    finalOutput = finalOutput.output(outVideoPath,
        vcodec="libx264",
        bf=2,
        flags="+cgop",
        pix_fmt="yuv420p",
        movflags="faststart"
    )
    finalOutput.run(overwrite_output=True)
    shutil.rmtree(f'{scriptFolder}/frames', ignore_errors=True)
    GLib.idle_add(toggleInterface, True)
    GLib.idle_add(closeApp)

class Handler:
    def onDestroy(self, *args):
        Gtk.main_quit()

    def onDistortButton(self, button):
        x = threading.Thread(target=distortify)
        x.start()

    def distortionChanged(self, scale):
        global distortionPercentage
        distortionPercentage = int(scale.get_value())

    def fpsChanged(self, spinner):
        global fpsValue
        fpsValue = int(spinner.get_value())

    def audioToggled(self, check):
        global distortAudio
        distortAudio = check.get_mode()

builder.connect_signals(Handler())
window = builder.get_object("mainWindow")
window.set_title(f"distortify: {currentVideo}")
window.show_all()

Gtk.main()
