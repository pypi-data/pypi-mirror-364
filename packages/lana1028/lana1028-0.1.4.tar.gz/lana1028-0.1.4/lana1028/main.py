import os
import hashlib
import base64
import secrets

# Constants
KEY_SIZE_BITS = 1028
KEY_SIZE_BYTES = (KEY_SIZE_BITS + 7) // 8  # Proper rounding (129 bytes)
BLOCK_SIZE = 64  # 512-bit block
NUM_ROUNDS = 64
IV_SIZE = BLOCK_SIZE  # 64 bytes

# --- Utility: Padding (PKCS7-style) ---
def pad(data):
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len] * pad_len)

def unpad(data):
    pad_len = data[-1]
    if pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding.")
    return data[:-pad_len]

# --- Key Generation ---
def generate_lana1028_key():
    return secrets.token_bytes(KEY_SIZE_BYTES)

# --- Key Expansion ---
def key_expansion(master_key):
    expanded_keys = []
    for i in range(NUM_ROUNDS):
        round_key = hashlib.sha512(master_key + i.to_bytes(4, 'big')).digest()
        expanded_keys.append(round_key[:BLOCK_SIZE])
    return expanded_keys

# --- S-Box (Non-linear substitution) ---
def s_box(data):
    return bytes((b ^ 0xA5) for b in data)

# --- P-Box (Permutation) ---
def p_box(data):
    return data[::-1]

# --- Encryption ---
def lana1028_encrypt(plaintext: str, key: bytes) -> str:
    if not isinstance(plaintext, bytes):
        plaintext = plaintext.encode()

    plaintext = pad(plaintext)
    iv = secrets.token_bytes(IV_SIZE)
    expanded_keys = key_expansion(key)

    ciphertext = bytearray(iv + plaintext)  # Prepend IV

    for round_num in range(NUM_ROUNDS):
        round_key = expanded_keys[round_num]
        ciphertext = bytearray([ciphertext[i] ^ round_key[i % BLOCK_SIZE] for i in range(len(ciphertext))])
        ciphertext = s_box(ciphertext)
        ciphertext = p_box(ciphertext)

    return base64.b64encode(ciphertext).decode()

# --- Decryption ---
def lana1028_decrypt(encoded_ciphertext: str, key: bytes) -> str:
    ciphertext = base64.b64decode(encoded_ciphertext)
    expanded_keys = key_expansion(key)

    data = bytearray(ciphertext)

    for round_num in reversed(range(NUM_ROUNDS)):
        round_key = expanded_keys[round_num]
        data = p_box(data)
        data = s_box(data)
        data = bytearray([data[i] ^ round_key[i % BLOCK_SIZE] for i in range(len(data))])

    iv = data[:IV_SIZE]
    plaintext = data[IV_SIZE:]
    return unpad(plaintext).decode()

# --- Example Usage ---
if __name__ == "__main__":
    key = generate_lana1028_key()
    message = "Secret message for encryption"
    
    print("[Original Message]:", message)
    
    encrypted = lana1028_encrypt(message, key)
    print("[Encrypted]:", encrypted)
    
    decrypted = lana1028_decrypt(encrypted, key)
    print("[Decrypted]:", decrypted)
