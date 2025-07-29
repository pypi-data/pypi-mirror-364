"""
bmdope.py
This file is main module of py-bmdope.
py-bmdope is a Python package for Block Metadata-Driven Order-Preserving Encryption (BMDOPE).
It provides functionalities for encrypting and decrypting data using the BMDOPE algorithm.
"""

from pybmdope.key import split_key, reshuffle
from pybmdope.metadata import encrypt_metadata, decrypt_metadata
from pybmdope.util import binary_to_bytes, bytes_to_binary

import os

MAX_32_BIT = 2**32 - 1  # Maximum value for a 32-bit unsigned integer
MAX_128_BIT = 2**128 - 1  # Maximum value for a 128-bit unsigned integer

class DecryptionError(Exception):
    """
    Custom exception raised when decryption fails.
    
    This exception is used to indicate that the decryption process has encountered
    an error, which may be due to an incorrect key or tampered data.
    """
    pass

class BMDOPE:
    def __init__(self, key: bytes):
        """
        Initialize the BMD-OPE cipher with a 16-byte key.
        Args:
            key (bytes): A 16-byte encryption key used for the BMD-OPE cipher.
        Raises:
            ValueError: If the key is not bytes type or not exactly 16 bytes long.
        Attributes:
            key (bytes): The original encryption key.
            __current_key (bytes): The current key being used (copy of original key).
            __BLOCK_SIZE (int): Size of each block in bytes (set to 4).
            __SHIFT_MASK (int): Bit mask for shifts, using 5 bits (0b11111).
        """
        if not isinstance(key, bytes) and len(key) != 16:
            raise ValueError("Key must be 16 bytes long if provided.")
        
        self.key = key
        self.__current_key = key
        
        self.__BLOCK_SIZE = 4  # Size of each block in bytes
        self.__SHIFT_MASK = 0b11111  # Mask for shifts (5 bits)
        
    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypts the given data using the BMDOPE algorithm.
        """
        self.__current_key = self.key
        remainder = len(data) % self.__BLOCK_SIZE
        if remainder == 0:
            blocks = [data[i:i+self.__BLOCK_SIZE] for i in range(0, len(data), self.__BLOCK_SIZE)]
        else:
            blocks = [data[:remainder]] + [data[i:i+self.__BLOCK_SIZE] for i in range(remainder, len(data), self.__BLOCK_SIZE)]

        encrypted_blocks = b''
        metadata = []
        
        for block in blocks:
            encrypted_block, length = self.encrypt_block(block, self.__current_key)
            encrypted_blocks += encrypted_block
            metadata.append(length)
            self.__current_key = reshuffle(self.__current_key)

        iv = self.generate_key()
        encrypted_metadata = encrypt_metadata(metadata, self.key, iv)
        
        return encrypted_blocks + encrypted_metadata + iv
        
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypts the given encrypted data using the BMDOPE algorithm.
        """
        try:
            self.__current_key = self.key
            decrypted_data = b''
            iv = encrypted_data[-16:]
            metadata = decrypt_metadata(encrypted_data[:-16], self.key, iv)
            
            for length, i in zip(metadata, range(len(metadata))):
                block = bytes_to_binary(encrypted_data[i * 16:(i + 1) * 16])
                slice_bits = block[-length:]
                decrypted_data += self.decrypt_block(slice_bits, self.__current_key)
                self.__current_key = reshuffle(self.__current_key)
            
            return decrypted_data
        except Exception as e:
            raise DecryptionError("Decryption failed. Possibly due to incorrect key or tampered data.") from e
        
    def encrypt_bound(self, data: bytes, lower_bound: bool = True, upper_bound: bool = True) -> tuple[bytes, bytes]:
        """
        Encrypts the given data with metadata ignored for bounds to provide a range query.
        Args:
            data (bytes): The data to be encrypted.
            lower_bound (bool): If True, includes the lower bound in the encryption.
            upper_bound (bool): If True, includes the upper bound in the encryption.
        Returns:
            tuple[bytes, bytes]: A tuple containing upper and lower bounds of the encrypted data.
        Raises:
            ValueError: If the data is not bytes type or if the bounds are not boolean.
        """
        
        self.__current_key = self.key
        remainder = len(data) % self.__BLOCK_SIZE
        if remainder == 0:
            blocks = [data[i:i+self.__BLOCK_SIZE] for i in range(0, len(data), self.__BLOCK_SIZE)]
        else:
            blocks = [data[:remainder]] + [data[i:i+self.__BLOCK_SIZE] for i in range(remainder, len(data), self.__BLOCK_SIZE)]

        encrypted_blocks = b''
        metadata = []
        
        for block in blocks:
            encrypted_block, length = self.encrypt_block(block, self.__current_key)
            encrypted_blocks += encrypted_block
            metadata.append(length)
            self.__current_key = reshuffle(self.__current_key)

        iv = self.generate_key()
        footer = encrypt_metadata(metadata, self.key, iv) + iv
        footer_length = len(footer)
        
        lower_bound = encrypted_blocks + (b'\x00' * footer_length if lower_bound else footer)
        upper_bound = encrypted_blocks + (b'\xff' * footer_length if upper_bound else footer)
        
        return lower_bound, upper_bound
    
    def encrypt_block(self, block: bytes, key: bytes) -> bytes:
        """
        Encrypts a 4-byte block using a 16-character key.
        
        The function processes the block through a series of additions and bitwise
        left shifts. The operations are determined by splitting the key into
        different parts. The final integer value is converted to its binary
        string representation and then encoded into bytes.
        
        Args:
            block (bytes): The data block to be encrypted, with a maximum size of 4 bytes.
            key (str): The encryption key, which must be exactly 16 characters long.
        
        Returns:
            bytes: The encrypted data as a binary string encoded in UTF-8.
        
        Raises:
            ValueError: If the provided key is not in bytes format, 
                        is not 16 characters long, or if the block size exceeds 4 bytes.
        """
        if not isinstance(key, bytes):
            raise ValueError("Key must be a bytes object.")
        if len(key) != 16:
            raise ValueError("Invalid key size.")
        if len(block) > 4:
            raise ValueError("Block size must not exceed 4 bytes.")
        
        parts, shifts = split_key(key)
        value = int.from_bytes(block, 'big')
        
        padding = int(MAX_128_BIT * value / MAX_32_BIT)
        binary_padding = bin(padding)[2:].zfill(128)
        
        for i in range(4):
            value += int.from_bytes(parts[i], 'big')
            if i != 3:
                shift_value = shifts[i] & self.__SHIFT_MASK
                value <<= shift_value

        binary_encrypted = bin(value)[2:]
        encrypted_block = (binary_padding[0:128 - len(binary_encrypted)] + binary_encrypted).zfill(128)
        
        return binary_to_bytes(encrypted_block.encode()), len(binary_encrypted)

    def decrypt_block(self, encrypted_value: bytes, key: bytes) -> bytes:
        """
        Decrypts a single block of data using a provided key.
        
        This function reverses the encryption process by performing a series of
        subtractions and right bit shifts on the input value. The operations are
        derived from the provided 16-character key. The input `encrypted_value`
        is expected to be a byte string representing an integer in binary format.
        
        Args:
            encrypted_value (bytes): The encrypted block to be decrypted. This should
                be a byte string containing the binary representation of the
                encrypted integer.
            key (str): The 16-character string key used for decryption.
        
        Returns:
            bytes: The decrypted data as a 4-byte block in big-endian format.
        
        Raises:
            ValueError: If the provided key is in bytes format or is not 16 characters long.
        """
        if not isinstance(key, bytes):
            raise ValueError("Key must be a bytes object.")
        if len(key) != 16:
            raise ValueError("Invalid key size.")
        
        parts, shifts = split_key(key)
        value = int(encrypted_value.decode(), 2)
        
        for i in range(3, -1, -1):
            if i != 3:
                shift_value = shifts[i] & self.__SHIFT_MASK
                value >>= shift_value
            value -= int.from_bytes(parts[i], 'big')
        
        byte_length = (value.bit_length() + 7) // 8 if value > 0 else 1
        return value.to_bytes(byte_length, 'big')
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Generates a random 16-byte key for encryption.
        
        This method uses the os.urandom function to generate a secure random key.
        
        Returns:
            bytes: A 16-byte random key suitable for encryption.
        """
        return os.urandom(16)
