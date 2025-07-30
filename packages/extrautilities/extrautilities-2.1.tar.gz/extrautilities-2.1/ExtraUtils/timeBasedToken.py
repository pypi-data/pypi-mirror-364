import time
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

class TimeBasedToken:
    def __init__(self, primary_toke:str, secondary_token:str):
        '''keep the order of the tokens in mind while setting up the other communication endpoints.'''
        self.__enckey = None
        if not primary_toke or not secondary_token:
            raise ValueError("Token can't be empty")
        if not isinstance(primary_toke, str) or not isinstance(secondary_token, str):
            raise ValueError("Token must be string")
        self.__primary = primary_toke
        self.__special = secondary_token
        self.regenerate()


    def regenerate(self):
        timestamp = int(time.time() // 10 * 10)
        combined = f"{self.__special}{timestamp}".encode()
        hash_result = hashlib.sha256(combined).hexdigest()
        bitmap = bin(int(hash_result[:8], 16))[2:].zfill(32)
        order_seed = int(hash_result[8:16], 16)
        order = sorted(range(32), key=lambda x: (order_seed >> (x % 8)) & 1)
        extracted_chars = ''.join([self.__special[i] for i, bit in enumerate(bitmap) if bit == '1'])
        sorted_chars = ''.join([extracted_chars[i] for i in order if i < len(extracted_chars)])
        final_combined = f"{self.__primary}{sorted_chars}".encode()
        final_hash = hashlib.sha256(final_combined).hexdigest()
        self.__enckey = final_hash
        return str(final_hash)
    
    def encrypt(self, plaintext):
        # Generiere einen zufälligen IV für jede Verschlüsselung
        iv = get_random_bytes(AES.block_size)
        key_bytes = bytes.fromhex(self.__enckey)

        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        encrypted_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        encrypted_data = base64.b64encode(iv + encrypted_bytes).decode()
        return encrypted_data

    def decrypt(self, encrypted):
        # Konvertiere den Hex-Schlüssel in Bytes
        key_bytes = bytes.fromhex(self.__enckey)
        if not isinstance(encrypted, str):
            raise ValueError("Encrypted data must be string")
        # Dekodiere die Daten aus Base64
        encrypted_bytes = base64.b64decode(encrypted)
        

        iv = encrypted_bytes[:AES.block_size]
        encrypted_text = encrypted_bytes[AES.block_size:]

        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        decrypted_bytes = unpad(cipher.decrypt(encrypted_text), AES.block_size)
        
        return decrypted_bytes.decode()
    
    def __str__(self):
        return self.__enckey



# Example
# primary = "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
# special = "7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f"
# import timeit
# def main():
#     final_token = TimeBasedToken(primary, special)
# 
#     print(final_token.regenerate())
#     enc = final_token.encrypt("in Python umsetzen könnte:")
#     print(enc)
#     dec = final_token.decrypt(enc)
#     print(dec)
# 
# if __name__ == "__main__":
#     print(timeit.timeit(main, number=1))