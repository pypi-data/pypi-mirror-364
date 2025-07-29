"""Module gcrypto."""

import os
import hmac
import hashlib
import uuid

from Crypto.Cipher import AES  # pylint: disable=import-error


class AES_BASE: # pylint: disable=C0103
    """Class AES_BASE"""

    @staticmethod
    def pad(data: bytes) -> bytes:
        """ pad """
        # Add padding to make the data length a multiple of AES block size (16 bytes)
        padding_length = AES.block_size - (len(data) % AES.block_size)
        return data + bytes([padding_length] * padding_length)

    @staticmethod
    def unpad(data: bytes) -> bytes:
        """ unpad """
        # Remove padding added during encryption
        padding_length = data[-1]
        if padding_length == 0 or padding_length > 16:
            raise ValueError(f'{padding_length=}. must be >0 or <=16')
        return data[:-padding_length]

    @staticmethod
    def generate_key(key_size: int) -> bytes:
        """ generate_key """    
        return os.urandom(key_size)

    @staticmethod
    def generate_iv_bs(block_size: int) -> bytes:
        """ generate_iv """        
        return os.urandom(block_size)

    @staticmethod
    def generate_key_id() -> str:
        """ generate_key_id """        
        return uuid.uuid4().hex


class AES_GCM(AES_BASE): # pylint: disable=C0103
    """Class AES_GCM"""

    @staticmethod
    def generate_iv() -> bytes:
        """ generate_iv """            
        return AES_BASE.generate_iv_bs(12)

    @staticmethod
    def encrypt(data: bytes,  header: bytes, key: bytes, iv: bytes, pad: bool = True) -> tuple[bytes, bytes]:
        """ encrypt """                
        cipher = AES.new(key, AES.MODE_GCM, iv)
        if header:
            cipher.update(header)
        if pad:
            return cipher.encrypt_and_digest(AES_GCM.pad(data))
        return cipher.encrypt_and_digest(data)

    @staticmethod
    def decrypt(ciphertext: bytes, header: bytes, key: bytes, iv: bytes, tag: bytes, pad: bool = True) -> bytes:  # pylint: disable=too-many-positional-arguments,too-many-arguments
        """ decrypt """                    
        cipher = AES.new(key, AES.MODE_GCM, iv)
        if header:
            cipher.update(header)
        if pad:
            return AES_GCM.unpad(cipher.decrypt_and_verify(ciphertext, tag))
        return cipher.decrypt_and_verify(ciphertext, tag)


class AES_CBC(AES_BASE): # pylint: disable=C0103
    """Class AES_CBC"""

    @staticmethod
    def generate_iv() -> bytes:
        """ generate_iv """                        
        return AES_BASE.generate_iv_bs(AES.block_size)

    @staticmethod
    def encrypt(data: bytes, key: bytes, iv: bytes, pad: bool = True) -> bytes:
        """ encrypt """                        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        if pad:
            return cipher.encrypt(AES_CBC.pad(data))
        return cipher.encrypt(data)

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, iv: bytes, pad: bool = True) -> bytes:
        """ decrypt """                            
        cipher = AES.new(key, AES.MODE_CBC, iv)
        if pad:
            return AES_CBC.unpad(cipher.decrypt(ciphertext))
        return cipher.decrypt(ciphertext)


class HMAC(): # pylint: disable=C0103
    """Class HMAC"""

    @staticmethod
    def sign(data: bytes, key: bytes, digestmod=hashlib.sha256, hexdigest=True) -> str:
        """ sign """                                
        if hexdigest:
            return hmac.new(key, data, digestmod).hexdigest()
        return hmac.new(key, data, digestmod).digest()

    @staticmethod
    def verify(data: bytes, key: bytes, digest: bytes, digestmod=hashlib.sha256,
               hexdigest=True) -> bool:
        """ verify """
        signed_digest = HMAC.sign(data, key, digestmod, hexdigest)
        return signed_digest == digest
