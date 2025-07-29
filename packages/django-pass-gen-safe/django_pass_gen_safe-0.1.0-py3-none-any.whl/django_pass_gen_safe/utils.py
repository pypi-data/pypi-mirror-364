import json
import os
from cryptography.fernet import Fernet
import base64

# Générer une clé de chiffrement (à sauvegarder sécurisément)
def generate_key():
    return Fernet.generate_key()

# Charger ou créer le fichier chiffré
SAFE_FILE = os.path.join(os.path.dirname(__file__), 'password_safe.json')
KEY = generate_key()  # À remplacer par une clé fixe ou demander à l'utilisateur
cipher = Fernet(KEY)

def load_safe():
    if os.path.exists(SAFE_FILE):
        with open(SAFE_FILE, 'rb') as f:
            encrypted_data = f.read()
            data = json.loads(cipher.decrypt(encrypted_data).decode())
            return data
    return {}

def save_safe(data):
    encrypted_data = cipher.encrypt(json.dumps(data).encode())
    with open(SAFE_FILE, 'wb') as f:
        f.write(encrypted_data)