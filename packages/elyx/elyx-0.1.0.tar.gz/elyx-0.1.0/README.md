# Elyx - Secure Terminal Encryption Tool

A secure, user-friendly terminal-based encryption/decryption tool that uses industry-standard AES encryption to protect your sensitive text data.

## Features

- **Strong Encryption**: Uses AES encryption with PBKDF2 key derivation (100,000 iterations)
- **Password Generation**: Built-in secure password generator (10 characters with mixed case, numbers, and symbols)
- **Beautiful Terminal UI**: Rich formatting with colors and panels for excellent user experience
- **Easy to Use**: Simple menu-driven interface
- **Secure**: Passwords are never stored, all operations happen locally
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### From PyPI (Coming Soon)
```bash
pip install elyx
```

### From Source
```bash
git clone https://github.com/yourusername/elyx.git
cd elyx
pip install -r requirements.txt
pip install -e .
```

## Usage

Run the application:
```bash
elyx
```

Or if installed from source:
```bash
python -m elyx.main
```

### Main Menu Options

1. **Encrypt Text**: Encrypt any text with a password
2. **Decrypt Text**: Decrypt previously encrypted text
3. **Generate Secure Password**: Create a random 10-character password
4. **Help**: View usage instructions
5. **Exit**: Close the application

### Encrypting Text

1. Select option 1 from the main menu
2. Enter or paste the text you want to encrypt
3. Choose to either:
   - Generate a secure password (recommended)
   - Enter your own password (minimum 8 characters)
4. Copy the encrypted output

### Decrypting Text

1. Select option 2 from the main menu
2. Paste the encrypted text
3. Enter the password used for encryption
4. Your original text will be displayed

## Security Notes

- Uses `cryptography` library's Fernet implementation (AES 128-bit encryption)
- Passwords are derived using PBKDF2-HMAC-SHA256 with 100,000 iterations
- Each encryption uses a unique random salt
- Encrypted output is Base64 encoded for easy sharing
- All operations happen locally - no data is sent over the network

## Requirements

- Python 3.8 or higher
- Dependencies:
  - cryptography >= 41.0.0
  - rich >= 13.7.0
  - click >= 8.1.0

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Building for Distribution
```bash
python setup.py sdist bdist_wheel
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Your Name - your.email@example.com