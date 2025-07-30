from setuptools import setup, find_packages


requirements = ['wheel', 'pycryptodome', 'websockets', 'ujson', 'pybase64', 'urllib3', 'mutagen', 'TinyTag']


setup(
    name = 'evatygram',
    version = '2.1.1',
    author='Eva',
    author_email = 'marwanalknah017@gmail.com',
    description = 'This is an unofficial library and fastest library for deploying robots on Rubika accounts.',
    keywords = ['rubika', 'evatygram', 'rubikaio', 'chat', 'bot', 'robot', 'asyncio'],
    long_description = str(open('README.md', 'r').read()),
    python_requires="~=3.8",
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/eeeterii/evatygram/',
    packages = find_packages(),
    install_requires = requirements,
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet',
        'Topic :: Communications',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
)