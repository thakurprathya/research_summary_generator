import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from dotenv import load_dotenv
from .models import get_research_by_title

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

def update_df(df):
    for index, row in df.iterrows():
        research = get_research_by_title(row['email'], row['publicationTitle'])
        if research:
            df.at[index, 'abstract'] = research['abstract']
            df.at[index, 'publicationLink'] = research['publicationLink']
            if not row['journal'] or row['journal'] == '':
                df.at[index, 'journal'] = research['journal']
    return df

def df_to_profile(df):
    profiles = []

    # Grouping by 'name' to handle multiple faculties
    grouped = df.groupby('name')

    for name, group in grouped:
        email = group['email'].iloc[0] if 'email' in group else ""
        institution = group['institution'].iloc[0] if 'institution' in group else ""
        address = group['address'].iloc[0] if 'address' in group else ""

        research_list = []
        for _, row in group.iterrows():
            research_item = {
                "publicationTitle": row.get("publicationTitle", ""),
                "year": int(row.get("year", 0)) if str(row.get("year", "")).isdigit() else row.get("year", ""),
                "journal": row.get("journal", ""),
                "abstract": row.get("abstract", ""),
                "publicationLink": row.get("publicationLink", "")
            }
            research_list.append(research_item)

        profile = {
            "name": name,
            "email": email,
            "institution": institution,
            "address": address,
            "research": research_list
        }
        profiles.append(profile)

    return profiles