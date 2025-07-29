# LEDLang
[![Publish to PyPI](https://github.com/ElliNet13/ledlang/actions/workflows/deploy.yml/badge.svg)](https://github.com/ElliNet13/ledlang/actions/workflows/deploy.yml)
![PyPI - Version](https://img.shields.io/pypi/v/ledlang)
![GitHub License](https://img.shields.io/github/license/ElliNet13/ledlang)

<br>
LED Programming Language, mostly for controlling a Micro:bit but others can be used.
[to-the-serial Micro:bit Makecode Helper](https://ellinet13.github.io/to-the-serial/)

| Command  | What they do                    |
|----------|---------------------------------|
| PLOT     | Turn on a pixel on the screen   |
| CLEAR    | Clear the screen                |

# Problems
| Item     | Problem                                                                                        |
|----------|------------------------------------------------------------------------------------------------|
| TEXT     | Only works if the height of your display is 5, you can get around this bug by using REALSIZE   |

# Notes
| Item         | Problem                                     |
|--------------|---------------------------------------------|
| REALSIZE     | Can lag since division is used every PLOT   |

Commits between builds: - [8709459](https://github.com/ElliNet13/ledlang/commit/87094599da88fc93e37c7f7104f29d8986fc1e71): Reorder fillers<br>
Test Status: success<br>
[Github repo](https://github.com/ElliNet13/ledlang)