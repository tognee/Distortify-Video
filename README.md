# Distortify Video

A GTK app that lets you distort videos using a Content Aware Scale like filter.  
Made it to work with nautilus-python addons as a right click option for videos.

# Installing

`sudo apt install python3 python3-pip ffmpeg`

`git clone https://github.com/tognee/Distortify-Video`

`cd Distortify-Video`

` pip3 install -r requirements.txt`

# Usage

(Put your video in the repository folder, in example i'll use video.mp4)
`python3 main.py video.mp4`

You can also pass a absolute path, the app can handle it
`python3 /path/to/main.py path/to/video.mp4`

Choose distortion level, fps number, if you want distorted audio or not and tap "Distort" button

Examples of work are presented below.

## Original:

[![Original](https://img.youtube.com/vi/O5tDNWA31vg/0.jpg)](https://www.youtube.com/watch?v=O5tDNWA31vg)  
Youtube Link

## Distorted:

[![Distorted](https://img.youtube.com/vi/-i2lPdw6UXU/0.jpg)](https://www.youtube.com/watch?v=-i2lPdw6UXU)  
Youtube Link
