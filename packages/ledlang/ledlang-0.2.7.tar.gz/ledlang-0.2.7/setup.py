from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="ledlang",
    version="0.2.7",
    description="A language for controlling LED animations. Other device must support PLOT and CLEAR calls.",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="ElliNet13",
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=['pyserial'],
    entry_points={
        'console_scripts': [
            'ledlang-test = ledlang.LEDLangTesting:main',
            'ledlang = ledlang.LEDSendCLI:main',
        ],
    },
    extras_require={
        'test': ['pytest'],
    },
    license="MIT",
    url="https://github.com/ElliNet13/ledlang",
    include_package_data=True,
    package_data={
        "ledlang": ["tests/*"],
    },
)
