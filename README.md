# `Artery Gear: Fusion`'s Toolkit
![Python: 3.10](https://img.shields.io/badge/python-3.10-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-blue) 
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

This repository contains the code to:
- Dump gear data from the game's info box screenshots taken from your Android device into either JSON format or a comma-separated string.

With these feature(s) to come (in no particular order and without promises):
- Optimise gear for your character(s) in the game.
- Capturing gear data from the game's network traffic

[Before reading any further, please note that this project is...](README.md:46)

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
```
- `DEBUG` when set to anything other than `""` will enable debug logging.
- `IDENTIFIER` is for the serial number of your Android device. You can find this by running `adb devices` in your terminal. If you're connecting via `IP`, this is the IP address of your Android device.
- `PORT` is the debugging port of your Android device. This is ignored when connecting via `USB`.


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