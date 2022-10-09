# `Artery Gear: Fusion`'s Toolkit
![Python: 3.10](https://img.shields.io/badge/python-3.10-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-blue) 
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

This repository contains the code to:
- Dump gear data from the game's info box screenshots taken from your Android device into either JSON format or a comma-separated string.

With these feature(s) to come (in no particular order and without promises):
- Optimise gear for your character(s) in the game.
- Capturing gear data from the game's network traffic

## Installation
You'll need:
- Python 3.10+ (primary runtime)
- [`poetry`](https://python-poetry.org/docs/#installation) (to install dependencies)
- [`adb`](https://developer.android.com/studio/command-line/adb) (to interact with your Android device)

Assuming you have installed the above, install the dependencies by running:
```sh
git clone https://github.com/PythonTryHard/agf-toolkit.git
cd agf-toolkit
poetry install
```
Then, ensure `adb` is running on your machine with:
```sh
adb start-server
```
When `adb` is running, after [configuring](#configuration) you can run the toolkit with:
```sh
poetry run python -m agf_tookit
```
## Configuration
The toolkit is configured via a `.env` file. The (boiled down) example configuration is as follows:
```sh
DEBUG=""

IDENTIFIER=""
PORT=""

SUB_STAT_1="0,0"
SUB_STAT_2="0,0"
SUB_STAT_3="0,0"
SUB_STAT_4="0,0"
```
- `DEBUG` when set to anything other than `""` will enable debug logging.
- `IDENTIFIER` is for the serial number of your Android device. You can find this by running `adb devices` in your terminal. If you're connecting via `IP`, this is the IP address of your Android device.
- `PORT` is the debugging port of your Android device. This is ignored when connecting via `USB`. 
- `SUB_STAT_1` to `4` is the coordinate that the program use to detect gears' sub stat's rarity. For more detail, see [Template preparation/Gear info box](#gear-info-box).

## Template preparation
You will need 6-7 screenshots: 1 of your gear info box and 5-6 of your gear's star grade. The screenshots should be placed in `./agf_tookit/templates` and named as follows:
```sh
info_box.png    # Gear info box 
1.png           # 1-star gear          
2.png           # 2-star gear
3.png           # 3-star gear
4.png           # 4-star gear
5.png           # 5-star gear
6.png           # 6-star gear
```
And no, **DO NOT** use the sample stuffs included.
### Gear info box
I recommend using a screenshot of the info box from Target Elimination mode. Finish a run, and tap on the gear icon on the top right of the screen. This will bring up the info box.

After that, take a screenshot and crop out the info box as tightly as possible without clipping in. Using any software, clean up the box as much as possible. You don't need to be precise with this. For an example, see the [sample info box](https://github.com/PythonTryHard/agf-toolkit/blob/master/templates_sample/info_box.png).

### Gear star
Again, info box screenshot, this time you crop out the stars. Make sure to not use the ones with equipment icon clipping in. For an example, see the [sample 6-star](https://github.com/PythonTryHard/agf-toolkit/blob/master/templates_sample/6.png)

## Note: This repository is...
### Not feature-complete.
I'm working on this solo, while also juggling irl work. This was supposed to be a rewrite of another private project, but I decided at the time of writing that this was enough to be of use to anyone wanting to write code for the game.

### Not stable, nor tested thoroughly.
A lot of things are still in the works, a lot of things are written on a whim. I haven't written any tests, the main loop is not decoupled from `__main__` to test, and I don't have enough screenshots to properly test the screenshot reader.

As the project scales, more and more tests will be needed. I'll try to write them as I go, but I can't promise anything.

### Not written by a professional programmer.
I'm a hobbyist try-hard programmer (as evident by my username) that just write too much code. If anything can be improved, please let me know. I'm always open to suggestions.

### Not meant to be used by the general public.
A lot of things in this repository needs some work to be usable by the general public. I will get around to writing a guide for this soon enough.