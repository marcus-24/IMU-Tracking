import os
from setuptools import setup


def read(fname: str) -> str:
    """Reads README file
    Args:
        fname (str): path to readme file
    Returns:
        str: contents in readme
    """
    full_fname = os.path.join(os.path.dirname(__file__), fname)
    with open(full_fname, encoding="utf-8") as file:
        return file.read()


setup(
      name="IMU-Tracking",
      version="0.0.1",
      author="Marcus Allen",
      author_email="marcusCallen24@gmail.com",
      py_modules=[],
      long_description=read('README.md')
)
