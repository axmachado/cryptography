# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

import abc
import typing

from cryptography import utils

# This exists to break an import cycle. These classes are normally accessible
# from the serialization module.


class Encoding(utils.Enum):
    PEM = "PEM"
    DER = "DER"
    OpenSSH = "OpenSSH"
    Raw = "Raw"
    X962 = "ANSI X9.62"
    SMIME = "S/MIME"


class PrivateFormat(utils.Enum):
    PKCS8 = "PKCS8"
    TraditionalOpenSSL = "TraditionalOpenSSL"
    Raw = "Raw"
    OpenSSH = "OpenSSH"

    def encryption_builder(self) -> "KeySerializationEncryptionBuilder":
        if self is not PrivateFormat.OpenSSH:
            raise ValueError(
                "encryption_builder only supported with PrivateFormat.OpenSSH"
            )
        return KeySerializationEncryptionBuilder(self)


class PublicFormat(utils.Enum):
    SubjectPublicKeyInfo = "X.509 subjectPublicKeyInfo with PKCS#1"
    PKCS1 = "Raw PKCS#1"
    OpenSSH = "OpenSSH"
    Raw = "Raw"
    CompressedPoint = "X9.62 Compressed Point"
    UncompressedPoint = "X9.62 Uncompressed Point"


class ParameterFormat(utils.Enum):
    PKCS3 = "PKCS3"


class KeySerializationEncryption(metaclass=abc.ABCMeta):
    pass


class BestAvailableEncryption(KeySerializationEncryption):
    def __init__(self, password: bytes):
        if not isinstance(password, bytes) or len(password) == 0:
            raise ValueError("Password must be 1 or more bytes.")

        self.password = password


class NoEncryption(KeySerializationEncryption):
    pass


class KeySerializationEncryptionBuilder(object):
    def __init__(
        self,
        format: PrivateFormat,
        *,
        _kdf_rounds: typing.Optional[int] = None,
    ) -> None:
        self._format = format

        self._kdf_rounds = _kdf_rounds

    def kdf_rounds(self, rounds: int) -> "KeySerializationEncryptionBuilder":
        if self._kdf_rounds is not None:
            raise ValueError("kdf_rounds already set")
        return KeySerializationEncryptionBuilder(
            self._format, _kdf_rounds=rounds
        )

    def build(self, password: bytes) -> KeySerializationEncryption:
        if not isinstance(password, bytes) or len(password) == 0:
            raise ValueError("Password must be 1 or more bytes.")

        return _KeySerializationEncryption(
            self._format, password, kdf_rounds=self._kdf_rounds
        )


class _KeySerializationEncryption(KeySerializationEncryption):
    def __init__(
        self,
        format: PrivateFormat,
        password: bytes,
        *,
        kdf_rounds: typing.Optional[int],
    ):
        self._format = format
        self.password = password

        self._kdf_rounds = kdf_rounds
