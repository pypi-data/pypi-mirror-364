from setuptools import setup, find_packages

setup(
    name="single-lang",
    version="1.2.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'single = single_lang.nucleus.main:run_from_command_line',
        ],
    },
)