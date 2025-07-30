from setuptools import setup, find_packages

setup(
    name="evatygram",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["Telethon"],
    author="Извращенец",
    author_email="marwanalknah017@gmail.com",
    description="مكتبة توليد جلسات تيليجرام مثل Telethon و Pyrogram",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/marwan123/evatygram",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)