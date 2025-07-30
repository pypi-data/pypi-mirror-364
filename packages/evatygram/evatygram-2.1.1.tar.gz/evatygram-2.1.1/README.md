<p align="center">
    <a href="https://github.com/snipe4kill/evatygram">
        <img src="https://upcdn.io/W142hJk/thumbnail/demo/4mrDXtYPJA.png.crop" alt="evatygram" width="128">
    </a>
    <br>
    <b>Rubika API Framework for Python</b>
    <br>
    <a href="https://pypi.org/project/evatygram/">Homepage</a>
    •
    <a href="https://t.me/evatygram_doc">Documentation</a>
    •
    <a href="https://pypi.org/project/evatygram/#history">Releases</a>
    •
    <a href="https://t.me/rubika_library">News</a>
</p>

---

# evatygram

> Elegant, modern and asynchronous Rubika API framework in Python for users and bots

[![PyPI version](https://badge.fury.io/py/evatygram.svg)](https://pypi.org/project/evatygram/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

---

## Example

```python
from evatygram import Client

app = Client("my_account")

@app.Handler
async def hello(message):
    await app.sendMessage(message.get('object-guid'), 'Hello from **evatygram**!')