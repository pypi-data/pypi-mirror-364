from setuptools import setup, find_packages

setup(
    name="single-lang",
    version="1.2.0",
    packages=find_packages(include=['single', 'single.*']),
    entry_points={
        'console_scripts': [
            'single = single.nucleus.main:run_from_command_line',
        ],
    },
)