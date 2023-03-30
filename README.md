# NOTE
Project is on hiatus due to in-real-life issues, overall loss of motivation and I have essentially stopped playing the game. If you wish to take over, please open an issue first for discussion.

Currently, off-GitHub progress for the repository has been documenting the code. Development will hopefully resume early June 2023.

# `Artery Gear: Fusion`'s Toolkit
![Python: 3.10](https://img.shields.io/badge/python-3.10-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-blue) 
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

This repository contains the code to:
- Dump gear data from the game's info box screenshots taken from your Android device into either JSON format or a 
  comma-separated string.

With these feature(s) to come (in no particular order and without promises):
- Optimise gear for your character(s) in the game.
- Capturing gear data from the game's network traffic

[Before reading any further, please note that this project is...](https://github.com/PythonTryHard/agf-toolkit#note-this-repository-is)

## Installation
### From release (recommended)
By default, this will the CPU version of the underlying OCR module. Pre-built wheels with GPU support will be supplied at a later date. 
```sh
pip install https://github.com/PythonTryHard/agf-toolkit/releases/download/v0.1.0/agf-toolkit-0.1.0-py3-none-any.whl
```

### From source
You'll need:
- Python 3.10 (primary runtime)
	- Python 3.11 support is currently blocked by `paddleocr`'s underlying `paddlepaddle` package. When will that 
  	  package add pre-built wheels, who knows.
- [`poetry`](https://python-poetry.org/docs/#installation) (to install dependencies)

You can 
```sh
git clone https://github.com/PythonTryHard/agf-toolkit.git
cd agf-toolkit
poetry install
```

Afterward you can run the toolkit with:
```sh
poetry run python -m agf_tookit
```
This should output:
```
$ python -m agf_toolkit

 Usage: python -m agf_toolkit [OPTIONS] COMMAND [ARGS]...

╭─ Options ───────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                     │
│ --show-completion             Show completion for the current shell, to copy it or          │
│                               customize the installation.                                   │
│ --help                        Show this message and exit.                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────╮
│ calibrate      Calibrate the toolkit before parsing (default: using Android Debug Bridge).  │
│ parse-files    Parse screenshots. Multiple files can be provided to parse at once.          │
│ parse-screen   Start a live parsing session using Android Debug Bridge.                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────╯
```
## Configuration
The toolkit is configured via a `.env` file. The (boiled down) example configuration is as follows:
```sh
LOGGING_LEVEL=""

IDENTIFIER=""
PORT=""
```
- `LOGGING_LEVEL` is the logging level to use. Valid values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. If not
  set, defaults to `INFO`.
- `IDENTIFIER` is for the serial number of your Android device. You can find this by running `adb devices` in your
- terminal. If you're connecting via `IP`, this is the IP address of your Android device.
- `PORT` is the debugging port of your Android device. This is ignored when connecting via `USB`.

## Contributing
Set up the development environment with:
```sh
poetry install --with dev
poetry run pre-commit install
```
If your contribution involves `agf_toolkit.processor`, please run `poetry run pytest` at repository root to ensure that
your changes don't break compatibility.

## Note: This repository is...
### Not feature-complete.
This was supposed to be a rewrite of another private project, but along the way features and ideas came up, so I decided
to expand the scope and implement them. This takes time, so be patient. Or better yet, hop in!

### Not stable, nor tested thoroughly.
A lot of things are still in the works, a lot of things are written on a whim. Some tests are written, but I'm not sure
if everything is properly tested. `coverage`, yes, but I'll look at that later.


### Not written by a professional programmer.
I'm a hobbyist try-hard programmer (as evident by my username) that just write too much code. My code can be very
opaque, hard to parse, and not follow best practices. If anything can be improved, please let me know. I'm always open
to suggestions.

### Not meant to be used by the general public.
A lot of things in this repository needs some work to be usable by the public. I will get around to writing a guide for
this soon enough. But until the first `v1.x` release, don't hope for much.
