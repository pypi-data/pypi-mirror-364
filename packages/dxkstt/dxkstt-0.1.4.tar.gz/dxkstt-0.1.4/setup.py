from setuptools import setup, find_packages

setup(
    name="dxkstt",
    version="0.1.4",  # ⬅️ Make sure to bump the version!
    author="kaushik",
    author_email="pubgkaushik@gmail.com",
    description="This is a speech-to-text package created by Kaushik",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "webdriver-manager",
        "speechrecognition",
        "colorama",
        "pyaudio",
        "mtranslate"
    ],
    python_requires=">=3.6",
)
