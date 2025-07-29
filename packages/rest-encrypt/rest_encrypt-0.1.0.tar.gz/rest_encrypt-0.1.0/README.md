# Rest-Encrypt

Rest-Encrypt provides lightweight encryption-at-rest for application secrets on
both Windows and Linux.  Secrets are stored on disk encrypted and are decrypted
only at runtime when your application needs them.  The project ships a small
Python API and a command line interface.

---

## Features

- Secrets stored as encrypted files (`secrets.enc`) using Fernet (AES-GCM + HMAC).
- Data keys wrapped using platform specific mechanisms:
  - **Windows**: DPAPI in user or machine scope.
  - **Linux**: scrypt + AES-GCM with a local passphrase file.
- Supports JSON, TOML, INI, `.env` and Python ``dict`` formats.
- Rotate secrets or the wrapping key with a single command.

## Installation

```bash
pip install rest-encrypt
```

---

## Quick Start

```bash
# initialise encrypted secrets from a JSON file
rest-encrypt init --secrets-path secrets.enc \
  --wrapped-key-path wrapped.key \
  --from-file secrets.json

# decrypt and print the stored secrets
rest-encrypt load --secrets-path secrets.enc \
  --wrapped-key-path wrapped.key --print
```

### CLI Usage

```bash
# inject secrets into the environment and run a command
rest-encrypt env-run --secrets-path secrets.enc \
  --wrapped-key-path wrapped.key -- \
  python my_script.py

# rotate the wrapped data key
rest-encrypt rotate-key --secrets-path secrets.enc \
  --wrapped-key-path wrapped.key
```

### Python API

```python
from rest_encrypt import SecretStore

store = SecretStore(
    secrets_path="secrets.enc",
    wrapped_key_path="wrapped.key",
    scope="user",          # DPAPI scope on Windows, ignored on Linux
    serializer="json",
    passphrase_path="/etc/rest-encrypt/passphrase",  # Linux only
)

# one-time initialisation
store.init_from_plain({"API_KEY": "123"})

# later, load and use the secrets
secrets = store.load()
store.inject_env(secrets, scope="process")
```

---

## File Layout

Two files are created next to each other:

```
secrets.enc   # encrypted secrets
wrapped.key   # wrapped data key
```

The ``wrapped.key`` is bound to your operating system.  On Linux it is encrypted
with a passphrase file, while on Windows DPAPI protects it.

## Security Notes

See [SECURITY.md](SECURITY.md) for the detailed threat model.  In short, the goal
is to protect secrets if the encrypted files are copied elsewhere.  Local admin
or root access on the original machine can always recover the data.

---

## License

This project is licensed under the Apache 2.0 License.
