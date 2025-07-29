from setuptools import setup, find_packages

setup(
    name='keypractice',
    version='0.1.0',
    description='A slim, cross-platform terminal-based typing trainer with YAML-based exercises and analytics.',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'PyYAML>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'keypractice=keypractice.__main__:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['exercises/special_characters.yaml'],
    },
    python_requires='>=3.7',
) 