import hashlib
import secrets

import string

class FPEExtended:
    ALPHABET = string.printable[:-6]
    RADIX = len(ALPHABET)

    def __init__(self, key: bytes, tweak: bytes, mode: str = "FF3-1"):
        if len(key) not in [16, 24, 32]:
            raise ValueError("Key must be 16, 24, or 32 bytes long")
        if mode == "FF3-1" and len(tweak) != 7:
            raise ValueError("Tweak must be 7 bytes for FF3-1")
        self.key = key
        self.tweak = tweak
        self.mode = mode
        self.alphabet = FPEExtended.ALPHABET
        self.radix = FPEExtended.RADIX

    @staticmethod
    def generate_key() -> bytes:
        return secrets.token_bytes(16)

    @staticmethod
    def generate_tweak(tweak_length: int = 7) -> bytes:
        return secrets.token_bytes(tweak_length)

    def _prf(self, input_num: int, round_num: int) -> int:
        tweak_int = int.from_bytes(self.tweak, 'big')
        input_bytes = int.to_bytes(input_num ^ round_num ^ tweak_int, 8, 'big')
        hash_input = self.key + self.tweak + input_bytes
        hash_output = hashlib.sha512(hash_input).digest()[:8]
        return int.from_bytes(hash_output, 'big')

    def encrypt(self, plaintext: str, radix: int = None) -> str:
        if radix is None:
            radix = self.radix
        if radix > self.radix:
            raise ValueError(f"Radix {radix} exceeds supported alphabet size {self.radix}")
        
        if len(plaintext) > 16:
            chunks = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]
            if len(chunks[-1]) % 2 != 0 and len(chunks) > 1:
                chunks[-1] = chunks[-2][-1] + chunks[-1]
                chunks[-2] = chunks[-2][:-1]
                if len(chunks[-2]) % 2 != 0:
                    chunks[-2] = chunks[-2] + plaintext[0]
            encrypted_chunks = [self._encrypt_chunk(chunk, radix) for chunk in chunks]
            return ''.join(encrypted_chunks)
        
        return self._encrypt_chunk(plaintext, radix)
    
    def _encrypt_chunk(self, plaintext: str, radix: int = None) -> str:
        """Encrypt a chunk of text that is small enough to convert to an integer."""
        if radix is None:
            radix = self.radix
        
        try:
            indices = [self.alphabet.index(c) for c in plaintext]
        except ValueError as e:
            new_text = ''.join([c if c in self.alphabet else ' ' for c in plaintext])
            indices = [self.alphabet.index(c) for c in new_text]
            
        n = len(indices)
        if n % 2 != 0:
            indices.append(0)
            n += 1
            pad = True
        else:
            pad = False
            
        half = n // 2
        left = 0
        right = 0
        for i in range(half):
            left = left * radix + indices[i]
            right = right * radix + indices[half + i]
            
        max_val = radix ** half
        for i in range(8):
            new_left = right
            prf_output = self._prf(right, i) % max_val
            new_right = (left + prf_output) % max_val
            left = new_left
            right = new_right
        left_indices = []
        right_indices = []
        l = left
        r = right
        for _ in range(half):
            left_indices.append(l % radix)
            l //= radix
        for _ in range(half):
            right_indices.append(r % radix)
            r //= radix
        left_indices = left_indices[::-1]
        right_indices = right_indices[::-1]
        result_indices = left_indices + right_indices
        if pad:
            result_indices = result_indices[:-1]
        result = ''.join(self.alphabet[i] for i in result_indices)
        return result

    def decrypt(self, ciphertext: str, radix: int = None) -> str:
        if radix is None:
            radix = self.radix
        if radix > self.radix:
            raise ValueError(f"Radix {radix} exceeds supported alphabet size {self.radix}")
            
        if len(ciphertext) > 16:
            chunks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
            if len(chunks[-1]) % 2 != 0 and len(chunks) > 1:
                chunks[-1] = chunks[-2][-1] + chunks[-1]
                chunks[-2] = chunks[-2][:-1]
                # Add padding to second-to-last chunk if it's now odd
                if len(chunks[-2]) % 2 != 0:
                    chunks[-2] = chunks[-2] + ciphertext[0]  # Use first char as padding
            # Decrypt each chunk
            decrypted_chunks = [self._decrypt_chunk(chunk, radix) for chunk in chunks]
            return ''.join(decrypted_chunks)
            
        return self._decrypt_chunk(ciphertext, radix)
    
    def _decrypt_chunk(self, ciphertext: str, radix: int = None) -> str:
        """Decrypt a chunk of text that is small enough to convert to an integer."""
        if radix is None:
            radix = self.radix
            
        try:
            indices = [self.alphabet.index(c) for c in ciphertext]
        except ValueError as e:
            # If character not in alphabet, replace with a placeholder
            new_text = ''.join([c if c in self.alphabet else ' ' for c in ciphertext])
            indices = [self.alphabet.index(c) for c in new_text]
            
        n = len(indices)
        # Store original length before potential padding
        original_length = n
        pad = False
        if n % 2 != 0:
            indices.append(0)
            n += 1
            pad = True
            
        half = n // 2
        left = 0
        right = 0
        for i in range(half):
            left = left * radix + indices[i]
            right = right * radix + indices[half + i]
            
        max_val = radix ** half
        for i in range(7, -1, -1):
            new_right = left
            prf_output = self._prf(left, i) % max_val
            new_left = (right - prf_output) % max_val
            left = new_left
            right = new_right
        # Convert back to indices
        left_indices = []
        right_indices = []
        l = left
        r = right
        for _ in range(half):
            left_indices.append(l % radix)
            l //= radix
        for _ in range(half):
            right_indices.append(r % radix)
            r //= radix
        left_indices = left_indices[::-1]
        right_indices = right_indices[::-1]
        result_indices = left_indices + right_indices
        if pad:
            result_indices = result_indices[:-1]
        result = ''.join(self.alphabet[i] for i in result_indices)
        return result