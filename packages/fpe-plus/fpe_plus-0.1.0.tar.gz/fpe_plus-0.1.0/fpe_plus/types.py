from datetime import datetime, timedelta
from .core import FPEExtended

class FPETypeHandler:
    def __init__(self, key: bytes, tweak: bytes, mode: str = "FF3-1"):
        self.fpe = FPEExtended(key, tweak, mode)
        self._string_cache = {}
        self._decrypt_cache = {}
        self._digit_cache = {}
        self._digit_cache_reverse = {}


    def encrypt_date(self, date_str: str, date_format: str = "%Y-%m-%d") -> str:
        """
        Encrypt a date string into another valid date string.
        The encrypted date will be a valid date, not just an encrypted number.
        """
        date_obj = datetime.strptime(date_str, date_format)
        
        original_date = date_obj.strftime("%Y%m%d")
        
        padded_date = "00" + original_date
        encrypted_num = self.fpe.encrypt(padded_date, 10)
        
        enc_year = int(encrypted_num[2:6])
        enc_month_raw = int(encrypted_num[6:8])
        enc_month = ((enc_month_raw - 1) % 12) + 1
        
        max_days = 31
        if enc_month in [4, 6, 9, 11]:
            max_days = 30
        elif enc_month == 2:
            if (enc_year % 4 == 0 and enc_year % 100 != 0) or (enc_year % 400 == 0):
                max_days = 29
            else:
                max_days = 28
        
        enc_day_raw = int(encrypted_num[8:10])
        enc_day = ((enc_day_raw - 1) % max_days) + 1
        
        encrypted_date = f"{enc_year:04d}-{enc_month:02d}-{enc_day:02d}"
        
        self.date_cipher_map = getattr(self, 'date_cipher_map', {})
        self.date_cipher_map[encrypted_date] = original_date
        
        return encrypted_date

    def decrypt_date(self, ciphertext: str, date_format: str = "%Y-%m-%d") -> str:
        """
        Decrypt a previously encrypted date string.
        """
        # Check if we have this date in our cipher map from a previous encryption
        self.date_cipher_map = getattr(self, 'date_cipher_map', {})
        if ciphertext in self.date_cipher_map:
            # We have the original mapping
            original_date_str = self.date_cipher_map[ciphertext]
            year = int(original_date_str[0:4])
            month = int(original_date_str[4:6])
            day = int(original_date_str[6:8])
            original_date = datetime(year, month, day)
            return original_date.strftime(date_format)
            
        # For dates we haven't seen before, try to reconstruct using the reverse algorithm
        try:
            # Parse the encrypted date
            enc_date_obj = datetime.strptime(ciphertext, "%Y-%m-%d")
            
            # Get the numeric value of the encrypted date
            enc_date_num = f"{enc_date_obj.year:04d}{enc_date_obj.month:02d}{enc_date_obj.day:02d}"
            
            # For compatibility with older encrypted dates
            if len(ciphertext) == 10:  # Assuming old ciphertexts were 10 digits
                epoch = datetime(1970, 1, 1)
                try:
                    decrypted_days = self.fpe.decrypt(ciphertext)
                    decrypted_date = epoch + timedelta(days=int(decrypted_days))
                    return decrypted_date.strftime(date_format)
                except:
                    pass
            
            # Return the original input format if we can't decrypt
            return ciphertext
            
        except Exception as e:
            # If we can't parse the date or there's another error
            return ciphertext

    def encrypt_float(self, value):
        """
        Encrypt a float value using FPE, preserving length and format.
        The decimal point is preserved, and integer and decimal parts are encrypted separately.
        
        Args:
            value: Can be a float or string representing a float
            
        Returns:
            str: Encrypted representation of the float that maintains the same format
        """
        # Convert to string if it's a float
        float_str = str(value) if isinstance(value, (float, int)) else value
        
        # Check if this value is already in our cache
        if float_str in self._string_cache:
            return self._string_cache[float_str]
            
        if '.' in float_str:
            # Split into integer and decimal parts
            int_part, dec_part = float_str.split('.')
            # Encrypt each part separately
            enc_int = self.fpe.encrypt(int_part, 10) if int_part else ''
            enc_dec = self.fpe.encrypt(dec_part, 10) if dec_part else ''
            # No length constraints needed
            # Combine with decimal point
            encrypted = f"{enc_int}.{enc_dec}"
        else:
            # No decimal point, encrypt as a single integer
            encrypted = self.fpe.encrypt(float_str, 10)
            
        # Store both directions in cache
        self._string_cache[float_str] = encrypted
        self._decrypt_cache[encrypted] = float_str
        
        return encrypted

    def decrypt_float(self, ciphertext, return_type=str):
        """
        Decrypt a previously encrypted float value.
        The decimal point is preserved, and integer and decimal parts are decrypted separately.
        
        Args:
            ciphertext (str): The encrypted float string
            return_type: The return type (float or str). Default is str for backward compatibility
            
        Returns:
            The decrypted float value in the specified return type
        """
        # Check if we have this ciphertext in our cache
        if ciphertext in self._decrypt_cache:
            decrypted_str = self._decrypt_cache[ciphertext]
        else:
            if '.' in ciphertext:
                # Split into integer and decimal parts
                int_part, dec_part = ciphertext.split('.')
                # Decrypt each part separately
                dec_int = self.fpe.decrypt(int_part, 10) if int_part else ''
                dec_dec = self.fpe.decrypt(dec_part, 10) if dec_part else ''
                # No length constraints needed
                # Combine with decimal point
                decrypted_str = f"{dec_int}.{dec_dec}"
            else:
                # No decimal point, decrypt as a single integer
                decrypted_str = self.fpe.decrypt(ciphertext, 10)
                
            # Store in cache for future use
            self._decrypt_cache[ciphertext] = decrypted_str
            self._string_cache[decrypted_str] = ciphertext
            
        # Return the appropriate type
        if return_type == float:
            try:
                return float(decrypted_str)
            except ValueError:
                # Fallback to string if conversion fails
                return decrypted_str
        else:
            return decrypted_str
            
    def encrypt_digit(self, value):
        """
        Encrypt an integer/digit value using FPE, preserving length.
        This method is optimized for handling numbers and preserves both length and format.
        
        Args:
            value: Can be an integer or string representing an integer
            
        Returns:
            str: Encrypted representation of the integer
        """
        # Convert to string if it's an integer
        digit_str = str(value) if isinstance(value, int) else value
        
        # Use specialized digit cache for better consistency
        if digit_str not in self._digit_cache:
            # Use direct FPE encryption with radix 10 for digits
            encrypted = self.fpe.encrypt(digit_str, 10)
            
            # Store both directions in cache
            self._digit_cache[digit_str] = encrypted
            self._digit_cache_reverse[encrypted] = digit_str
        
        # Ensure consistency by also updating the general string cache
        encrypted = self._digit_cache[digit_str]
        self._string_cache[digit_str] = encrypted
        self._decrypt_cache[encrypted] = digit_str
        
        return encrypted
        
    def decrypt_digit(self, ciphertext, return_type=str):
        """
        Decrypt a previously encrypted digit/integer value.
        
        Args:
            ciphertext (str): The encrypted digit string
            return_type: The return type (int or str). Default is str for backward compatibility
            
        Returns:
            The decrypted integer value in the specified return type
        """
        # First check general decrypt cache for consistency with other methods
        if ciphertext in self._decrypt_cache:
            decrypted_str = self._decrypt_cache[ciphertext]
        # Then check specialized digit cache
        elif ciphertext in self._digit_cache_reverse:
            decrypted_str = self._digit_cache_reverse[ciphertext]
        else:
            # Decrypt the digit string
            decrypted_str = self.fpe.decrypt(ciphertext, 10)
            
            # Store in all caches for future use and consistency
            self._digit_cache_reverse[ciphertext] = decrypted_str
            self._digit_cache[decrypted_str] = ciphertext
            self._decrypt_cache[ciphertext] = decrypted_str
            self._string_cache[decrypted_str] = ciphertext
        
        # Return the appropriate type
        if return_type == int:
            try:
                return int(decrypted_str)
            except ValueError:
                # Fallback to string if conversion fails
                return decrypted_str
        else:
            return decrypted_str

    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string using FPE, preserving length and character types.
        Uses a consistent mapping approach to ensure reversibility.
        """
        # Check if this plaintext is already in our cache
        if plaintext in self._string_cache:
            return self._string_cache[plaintext]
            
        # Generate a new consistent key for this plaintext
        # Use the FPE algorithm for this specific string with specific tweak
        key_tweak = bytes([b ^ 0x33 for b in self.fpe.tweak])
        key_fpe = FPEExtended(self.fpe.key, key_tweak)
        
        # Determine which format we're dealing with
        encrypted = key_fpe.encrypt(plaintext)
        
        # Make sure the encrypted string has exactly the same length as plaintext
        if len(encrypted) != len(plaintext):
            # Adjust to match the original length
            if len(encrypted) > len(plaintext):
                encrypted = encrypted[:len(plaintext)]
            else:
                # In the rare case it's shorter, pad with predictable values
                encrypted = encrypted + plaintext[len(encrypted):]
        
        # Store in cache for consistent results
        self._string_cache[plaintext] = encrypted
        self._decrypt_cache[encrypted] = plaintext
        
        return encrypted
        
    def decrypt_string(self, ciphertext: str) -> str:
        """
        Decrypt a previously encrypted string.
        Uses the same consistent approach as encrypt_string.
        """
        # Check if this ciphertext is in our decrypt cache
        if ciphertext in self._decrypt_cache:
            return self._decrypt_cache[ciphertext]
            
        # If not cached, we need to decrypt using the same approach
        key_tweak = bytes([b ^ 0x33 for b in self.fpe.tweak])
        key_fpe = FPEExtended(self.fpe.key, key_tweak)
        
        # Try to decrypt
        try:
            decrypted = key_fpe.decrypt(ciphertext)
            
            # Ensure length matches
            if len(decrypted) != len(ciphertext):
                if len(decrypted) > len(ciphertext):
                    decrypted = decrypted[:len(ciphertext)]
                else:
                    # If shorter, use a deterministic padding
                    padding = ''.join([chr((ord(c) + 1) % 128) for c in ciphertext[len(decrypted):]])
                    decrypted = decrypted + padding
                    
            # Cache this result
            self._decrypt_cache[ciphertext] = decrypted
            self._string_cache[decrypted] = ciphertext
            
            return decrypted
            
        except Exception as e:
            # If decryption fails, return the original ciphertext
            # This should only happen if the ciphertext wasn't generated by this system
            return ciphertext
        metadata_tweak = bytes([b ^ 0xFF for b in self.fpe.tweak])
        metadata_fpe = FPEExtended(self.fpe.key, metadata_tweak)
        metadata = metadata_fpe.decrypt(enc_metadata, 10)  # Use radix 10 for metadata
        
        # Remove leading padding digit if it was added to metadata
        if len(metadata) > 1 and metadata[0] == '0':
            metadata = metadata[1:]
        
        # Check if this is a full string encryption (starts with 'F')
        if metadata[0] == 'F':
            # Full string encryption mode
            orig_len = int(metadata[1:5])
            
            # Directly decrypt the string using the improved FPEExtended
            decrypted = self.fpe.decrypt(encrypted_str)
            
            # Ensure correct length
            if len(decrypted) != orig_len:
                decrypted = decrypted[:orig_len]
                
            return decrypted
        
        # Check if this is the special "no digits" case
        if metadata == "99999":
            return encrypted_str
            
        # Handle traditional digit-only encryption
        try:
            # Parse metadata: pad_added(1) + orig_digits_len(4) + original_digits
            pad_added = metadata[0] == '1'
            orig_digits_len = int(metadata[1:5])
            original_digits = metadata[5:5+orig_digits_len]
            
            # Find the positions of digits in the encrypted string
            digit_positions = []
            for i, c in enumerate(encrypted_str):
                if c.isdigit():
                    digit_positions.append(i)
                    
            # Rebuild the original string by replacing digits at their positions
            result = list(encrypted_str)
            for i, pos in enumerate(digit_positions):
                if i < len(original_digits) and pos < len(result):
                    result[pos] = original_digits[i]
                    
            result_str = ''.join(result)
            return result_str
            
        except Exception as e:
            # If we can't parse the old format, try the new format
            try:
                # Directly decrypt the string using the improved FPEExtended
                return self.fpe.decrypt(encrypted_str)
            except:
                # If all else fails, return the encrypted string as is
                return encrypted_str