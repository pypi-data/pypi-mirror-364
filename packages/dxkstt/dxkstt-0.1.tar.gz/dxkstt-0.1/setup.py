from setuptools import setup,find_packages

setup(
    name="dxkstt",
    version='0.1',
    author='kaushik',
    author_email='pubgkaushik@gmail.com',
    description='this is speech to text package created by Kaushik')
packages=find_packages(),
install_requirment=[
    'selenium',
    'webdriver_manager'
]