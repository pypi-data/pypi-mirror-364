from setuptools import setup, find_packages

setup(
    name="dxkstt",  # ✅ Must be unique on PyPI
    version='0.1.3',
    author='Kaushik',
    author_email='pubgkaushik@gmail.com',
    description='Speech-to-Text package with Hindi to English translation',
    packages=find_packages(),
    install_requires=[
        'speechrecognition',
        'pyaudio',
        'mtranslate',
        'colorama',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
