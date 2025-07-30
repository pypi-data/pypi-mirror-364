"""Symmetric cryptography primitives."""

from .aes import (
    aes_encrypt,
    aes_decrypt,
    encrypt_file,
    decrypt_file,
    encrypt_file_async,
    decrypt_file_async,
    scrypt_encrypt,
    scrypt_decrypt,
    pbkdf2_encrypt,
    pbkdf2_decrypt,
    argon2_encrypt,
    argon2_decrypt,
)
from .chacha import (
    chacha20_encrypt,
    chacha20_decrypt,
    xchacha_encrypt,
    xchacha_decrypt,
)
from .stream import (
    salsa20_encrypt as _salsa20_encrypt,
    salsa20_decrypt as _salsa20_decrypt,
    chacha20_stream_encrypt,
    chacha20_stream_decrypt,
)
from .kdf import (
    derive_key_scrypt,
    verify_derived_key_scrypt,
    derive_key_pbkdf2,
    verify_derived_key_pbkdf2,
    derive_key_argon2,
    derive_hkdf,
    kdf_pbkdf2,
    derive_pbkdf2 as _derive_pbkdf2,
    generate_salt,
)

derive_pbkdf2 = _derive_pbkdf2

# re-export deprecated ciphers
salsa20_encrypt = _salsa20_encrypt
salsa20_decrypt = _salsa20_decrypt

__all__ = [
    "aes_encrypt",
    "aes_decrypt",
    "encrypt_file",
    "decrypt_file",
    "encrypt_file_async",
    "decrypt_file_async",
    "scrypt_encrypt",
    "scrypt_decrypt",
    "pbkdf2_encrypt",
    "pbkdf2_decrypt",
    "argon2_encrypt",
    "argon2_decrypt",
    "chacha20_encrypt",
    "chacha20_decrypt",
    "xchacha_encrypt",
    "xchacha_decrypt",
    "chacha20_stream_encrypt",
    "chacha20_stream_decrypt",
    "derive_key_scrypt",
    "verify_derived_key_scrypt",
    "derive_key_pbkdf2",
    "verify_derived_key_pbkdf2",
    "derive_key_argon2",
    "derive_hkdf",
    "kdf_pbkdf2",
    "generate_salt",
]
