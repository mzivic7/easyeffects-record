# easyeffects-record
Automated player and recorder, allowing re-recording one or multiple songs with applied effects from [Easy Effects](https://github.com/wwmm/easyeffects)

## Features
- Play and record specified file
- Or be recursive in current directory
- Filter files by extension
- Specify output file extension
- Select Easy Effects preset
- Record without playing sound on speakers
- Automatically launch Easy Effects

## Usage
```
usage: easyeffects-record [-h] [-i EXT [EXT ...]] [-o EXT] [-p PRESET] [-s] [-v] [song_path]

Automated player and recorder, allowing re-recording one or multiple songs with applied effects
from Easy Effects tool

arguments:
  song_path             Path to target song file, if not specified, will run recursively in
                        current directory. When recursing, input-extension will be used to filter
                        files, and files from "output" directory will be omitted. If file path is
                        provided, new file will be saved in "output" directory in current
                        directory

options:
  -h, --help            show this help message and exit
  -i EXT [EXT ...], --input-extensions EXT [EXT ...]
                        list of input extensions to scan for in directories, default: mp3, m4a
  -o EXT, --output-extension EXT
                        output file extension, default: mp3
  -p PRESET, --preset PRESET
                        Easy Effects preset, default: auto
  -s, --slent           disconnects Easy Effects from device sound output, but still records sound
  -v, --version         show program's version number and exit
```

## Dependencies
[Easy Effects](https://github.com/wwmm/easyeffects) - Obviously  
[ffmpeg](https://www.ffmpeg.org/) - For playing and re-encoding audio file  
[pipewire](https://pipewire.org/) - Easy Effects dependency, also used for recording audio  

## Installing
- From AUR: `yay -S easyeffects-record`
- Manual:
    - Install all dependencies with your package manager
    - Clone this repository: `git clone https://github.com/mzivic7/easyeffects-record`
    - `cd easyeffects-record`
    - Copy script to system: `sudo cp easyeffects-record.py /usr/local/sbin/easyeffects-record`
    - Make it executable: `sudo chmod +x /usr/local/sbin/easyeffects-record`
