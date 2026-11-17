#!/usr/bin/env python3
"""
Generate RSA key pair for RS256 JWT signing.
Run this once to generate keys/private_key.pem and keys/public_key.pem
"""
import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Create keys directory
keys_dir = Path("keys")
keys_dir.mkdir(exist_ok=True)

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Write private key
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
with open(keys_dir / "private_key.pem", "wb") as f:
    f.write(private_key_pem)

# Write public key
public_key = private_key.public_key()
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
with open(keys_dir / "public_key.pem", "wb") as f:
    f.write(public_key_pem)

print(f"Keys generated in {keys_dir}/")
print("Private key: keys/private_key.pem")
print("Public key: keys/public_key.pem")

# Also generate JWKS
from cryptography.hazmat.primitives.asymmetric import rsa as rsa_types
import json
import base64

numbers = public_key.public_numbers()
e = base64.urlsafe_b64encode(numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, 'big')).decode().rstrip('=')
n = base64.urlsafe_b64encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, 'big')).decode().rstrip('=')

jwks = {
    "keys": [
        {
            "kty": "RSA",
            "kid": "agribrain-key-1",
            "use": "sig",
            "alg": "RS256",
            "n": n,
            "e": e
        }
    ]
}

with open(keys_dir / "jwks.json", "w") as f:
    json.dump(jwks, f, indent=2)

print("JWKS generated: keys/jwks.json")