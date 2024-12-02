from setuptools import setup, find_packages

setup(
    name="douyin-crawler",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'selenium',
        'PySide6',
        'webdriver_manager'
    ],
) 