from getpass import getpass
import os
import json
from base64 import b64encode, urlsafe_b64encode

from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_file(file_path, password, out_path):
    # Read file contents and extract filename
    with open(file_path, 'rb') as f:
        data = f.read()
    filename = os.path.basename(file_path).encode()

    # Generate salt and IVs
    salt = os.urandom(16)
    iv_data = os.urandom(12)
    iv_name = os.urandom(12)

    # Derive key from password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    key = kdf.derive(password.encode())
    aesgcm = AESGCM(key)

    # Encrypt file contents and filename
    encrypted_data = aesgcm.encrypt(iv_data, data, None)
    encrypted_name = aesgcm.encrypt(iv_name, filename, None)

    # Build payload
    payload = {
        "salt": b64encode(salt).decode(),
        "iv_data": b64encode(iv_data).decode(),
        "iv_name": b64encode(iv_name).decode(),
        "ciphertext": b64encode(encrypted_data).decode(),
        "filename_enc": b64encode(encrypted_name).decode()
    }

    with open(out_path, 'w') as f:
        json.dump(payload, f)

    print(f"Encrypted to {out_path}")


def encrypt(file_path, password, out_path):
    if not os.path.isdir(file_path):
        encrypt_file(file_path, password, out_path)
        return

    if os.path.exists(out_path) and not os.path.isdir(out_path):
        raise Exception(
            "Output path must be a directory if input is a directory.")

    for root, _, files in os.walk(file_path):
        for file in files:
            full_path = os.path.join(root, file)
            out_file_path = os.path.join(
                out_path, os.path.relpath(full_path, file_path))
            out_file_path = os.path.join(
                os.path.dirname(out_file_path), hash_file_name(file, password))
            os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
            encrypt_file(full_path, password, out_file_path)


def hash_file_name(file_name, password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"static_salt_for_filename",
        iterations=100_000,
    )
    key = kdf.derive(password.encode())

    hmac = HMAC(key, hashes.SHA256())
    hmac.update(file_name.encode())
    hashed_name = hmac.finalize()

    return urlsafe_b64encode(hashed_name).decode().rstrip('=')[:16] + ".enc"


def add_arguments(parser):
    parser.add_argument('input', help='Input file/directory path')
    parser.add_argument('output', help='Output file/directory path')


def main(args):
    file_path = os.path.abspath(args.input)
    out_path = os.path.abspath(args.output)
    password = getpass("Enter the password: ")
    encrypt(file_path, password, out_path)


def _direct():
    file_path = os.path.abspath(input("Enter the file path to encrypt: "))
    password = getpass("Enter the password: ")
    out_path = os.path.abspath(input("Enter the output file path: "))
    encrypt(file_path, password, out_path)


if __name__ == "__main__":
    _direct()
