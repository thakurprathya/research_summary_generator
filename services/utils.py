import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from dotenv import load_dotenv
from models import get_research_by_title

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

def update_row(row):
    research = get_research_by_title(row['email'], row['publicationTitle'])
    if research:
        row['abstract'] = research['abstract']
        row['publicationLink'] = research['publicationLink']
        if not row['journal'] or row['journal'] == '':
            row['journal'] = research['journal']
        return False  # Skip this row as it exists
    return True  # Keep this row