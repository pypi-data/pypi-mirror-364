from setuptools import setup, find_packages

setup(
    name="robo-checker",
    version="0.1.0",
    description="A tool to filter out data from robots.txt restricted URL domains.",
    author="Dongyang Fan",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
)