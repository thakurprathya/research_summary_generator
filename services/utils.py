import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import json
from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv('SECRET_KEY').encode('utf-8')

def encrypt_data(data):
    key = secret_key[:32]
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    padded_text = pad(data.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_text)
    
    return base64.b64encode(iv + encrypted).decode('utf-8')

def decrypt_data(data):
    encrypted_data = base64.b64decode(data)
    iv = encrypted_data[:16]
    encrypted_data = encrypted_data[16:]
    key = secret_key[:32]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size)

    return decrypted.decode('utf-8')