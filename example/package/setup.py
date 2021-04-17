from setuptools import setup

setup(
    name="snake",
    version="1.0",
    description="Snake simulator",
    author="Guilherme Saturnino",
    author_email="GUISA@orsted.dk",
    packages=["snake"],
    entry_points = {
        "console_scripts": ['snake=snake.snake:main']
    }
)