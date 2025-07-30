# Keyslide

## Description

**Keyslide** is a Python package offering a playful approach to text encryption and decryption—think Caesar cipher, but mapped to the physical QWERTY keyboard! Shift letters left or right across keyboard rows, either programmatically or via command line. Useful for simple obfuscation, puzzles, or just for fun.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation

Install from PyPI:

```bash
pip install keyslide
```

## Usage

### Python API

```python
from keyslide import encrypt, decrypt

text = "Hello, World!"
key = 2  # Shift right by 2 keys

cipher = encrypt(text, key)
print(cipher)  # Encrypted text

plain = decrypt(cipher, key)
print(plain)   # Should print: Hello, World!
```

### Command Line

Encrypt:

```bash
keyslide.encrypt "Hello, World!" 2
```
_Output:_  
`Jrnno, Ynrce!`

Decrypt:

```bash
keyslide.decrypt "Jrnno, Ynrce!" 2
```
_Output:_  
`Hello, World!`

**Notes:**
- Negative keys shift left: `keyslide.encrypt "Hello, World!" -1`
- Unknown characters (not on QWERTY) are unchanged.

## Features

- 🔤 **Keyboard-based encryption**: Shift letters based on their QWERTY row positions.
- 🛠️ **Easy API**: Use `encrypt()` and `decrypt()` in your Python code.
- 💻 **CLI ready**: Quick command-line access with `keyslide.encrypt` and `keyslide.decrypt`.
- ➡️ **Customizable key**: Shift any number of steps, positive (right) or negative (left).

## Contributing

Contributions are welcome!  
- Open issues for bugs or feature requests.
- Submit pull requests for improvements.

## License

This project is licensed under the MIT License.