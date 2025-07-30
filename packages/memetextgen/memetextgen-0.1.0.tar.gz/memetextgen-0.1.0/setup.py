# setup.py

from setuptools import setup, find_packages

setup(
    name='memetextgen',
    version='0.1.0',
    description='A silly meme-case text converter.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Joe Blow',
    author_email='your@email.com',
    url='https://github.com/yourusername/memetextgen',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'memetextgen = memetextgen.__main__:main'
        ]
    },
)
