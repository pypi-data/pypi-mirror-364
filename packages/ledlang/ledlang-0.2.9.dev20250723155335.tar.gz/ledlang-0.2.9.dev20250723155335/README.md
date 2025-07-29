# LEDLang
[![Publish to PyPI](https://github.com/ElliNet13/ledlang/actions/workflows/deploy.yml/badge.svg)](https://github.com/ElliNet13/ledlang/actions/workflows/deploy.yml)
![PyPI - Version](https://img.shields.io/pypi/v/ledlang)
![GitHub License](https://img.shields.io/github/license/ElliNet13/ledlang)
[![Run Pytest](https://github.com/ElliNet13/ledlang/actions/workflows/pytest.yml/badge.svg)](https://github.com/ElliNet13/ledlang/actions/workflows/pytest.yml)

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

[Github repo](https://github.com/ElliNet13/ledlang)<br>
Test Status for this: [![Test Status Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Frepos%2FElliNet13%2Fledlang%2Factions%2Fjobs%2F46576116271&query=status&logo=github&label=Test%20Status)](https://github.com/ElliNet13/ledlang/actions/runs/16475564628/job/46576116271)<br>
[View this deploy]((https://github.com/ElliNet13/ledlang/actions/runs/16475564619/job/46576115924))