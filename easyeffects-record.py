#!/usr/bin/python3

import sys
import time
import os.path
import argparse
import subprocess


def launch_easyeffects(preset):
    command = "ps cax | grep easyeffects"
    ps = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    running = ps.communicate()[0]
    if not running:
        if preset and preset != "auto":
            command = f"easyeffects -l {preset}"
            print(f"Launching easyeffects with preset: {preset}")
        else:
            command = "easyeffects"
            print("launching easyeffects")
        easyeffects = subprocess.Popen(command, shell=True)
        time.sleep(3)
        return easyeffects
    else:
        if preset and preset != "auto":
            print("Easy Effects is already running, cannot set preset")
        else:
            print("Easy Effects is already running")
        return None


def disconnect_output():
    """Disconnects Easy Effects from speaker output"""
    command = "pw-link --id --links"
    pw_link = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    links = pw_link.communicate()[0].decode()
    links = links.split("\n")
    for num, link in enumerate(links):
        if "|<-" in link and "ee_soe_output_level" in link:
            if "pw-record" not in links[num-1]:
                link_id = int(link.split("|<-")[0].replace(" ", ""))
                command = f"pw-link --disconnect {link_id}"
                subprocess.Popen(command, shell=True)


def re_record(root, file_path, output_extension, mute):
    """Re-records song by playing it and recording output from Easy Effects"""
    # start recorder
    command = "pw-record --target 0 temp.wav"
    recorder = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE)
    time.sleep(0.1)   # extra time to initialize pipewire node

    # connect Easy Effects node to recorder node
    command = "pw-link ee_soe_output_level pw-record"
    subprocess.Popen(command, shell=True)

    # play song and wait for it to end
    file_name = file_path.split("/")[-1]
    print(f"Playing: {file_name}")
    command = f'ffplay -nodisp -v quiet -stats -autoexit "{file_path}"'
    player = subprocess.Popen(command, shell=True)
    try:
        if mute:
            disconnect_output()
        player.wait()
    except KeyboardInterrupt:
        player.kill()
        print("Player stopped")

    # stop recorder
    recorder.kill()

    # convert to desired format and wait for it to end
    print(f"Encoding to: {output_extension}")
    file_no_ext = file_name[:-len(file_name.split(".")[-1])-1]
    output_path = f"{root}/output/{file_no_ext}.{output_extension}"
    command = f'ffmpeg -v quiet -stats -i temp.wav "{output_path}"'
    ffmpeg = subprocess.Popen(command, shell=True)
    try:
        ffmpeg.wait()
    except KeyboardInterrupt:
        ffmpeg.kill()
        print("Encoding stopped")

    # delete temp file
    command = "rm temp.wav"
    subprocess.Popen(command, shell=True)


def main(args):
    song_path = args.song_path
    input_extensions = args.input_extensions
    output_extension = args.output_extension
    preset = args.preset
    slent = args.slent

    root = os.getcwd()
    if not os.path.exists("output"):
        os.mkdir("output")

    if song_path:
        if not os.path.exists(song_path):
            print("Specified path is invalid")
            sys.exit()
        easyeffects = launch_easyeffects(preset)
        if slent:
            print("Running in silent mode")
        re_record(root, song_path, output_extension, slent)
        if easyeffects:
            easyeffects.kill()
    else:
        # get list of all songs
        input_extensions_str = str(input_extensions).replace("['", "").replace("']", "").replace("', '", ", ")
        print(f"Scanning for songs, extensions: {input_extensions_str}")
        file_list = []
        for path, subdirs, files in os.walk(root):
            for name in files:
                file_path = os.path.join(path, name)
                for input_extension in input_extensions:
                    if "output/" not in file_path and file_path[-len(input_extension):] == input_extension:
                        file_list.append(file_path)
        if len(file_list) != 0:
            print(f"Found {len(file_list)} songs")
        else:
            print("No songs found in current directory")
            sys.exit()

        if slent:
            print("Running in silent mode")

        # run easyeffects and load preset
        easyeffects = launch_easyeffects(preset)

        # loop over all songs
        print("Press Ctrl+C to stop current song")
        for song_path in file_list:
            re_record(root, song_path, output_extension, slent)

        # stop easyeffects
        if easyeffects:
            easyeffects.kill()


def argparser():
    """Sets up argument parser for CLI"""
    parser = argparse.ArgumentParser(
        prog="easyeffects-record",
        description="Automated player and recorder, allowing re-recording one or multiple songs with applied effects from Easy Effects tool"
        )
    parser._positionals.title = "arguments"
    parser.add_argument(
        "song_path",
        nargs="?",
        default=None,
        help='Path to target song file, if not specified, will run recursively in current directory. \
              When recursing, input-extension will be used to filter files, \
              and files from "output" directory will be omitted. If file path is provided, \
              new file will be saved in "output" directory in current directory'
        )
    parser.add_argument(
        "-i",
        "--input-extensions",
        nargs="+",
        type=str,
        metavar="EXT",
        default=["mp3", "m4a"],
        help="list of input extensions to scan for in directories, default: mp3, m4a"
        )
    parser.add_argument(
        "-o",
        "--output-extension",
        type=str,
        metavar="EXT",
        default="mp3",
        help="output file extension, default: mp3"
        )
    parser.add_argument(
        "-p",
        "--preset",
        type=str,
        action=None,
        help="Easy Effects preset, default: auto"
        )
    parser.add_argument(
        "-s",
        "--slent",
        action="store_true",
        help="disconnects Easy Effects from device sound output, but still records sound"
        )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
        )
    return parser.parse_args()


if __name__ == "__main__":
    args = argparser()
    main(args)
