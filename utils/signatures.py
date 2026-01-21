import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_der_public_key, load_pem_public_key, Encoding, PublicFormat
from cryptography.exceptions import InvalidSignature


def verify_signature(body: bytes, signature: str, timestamp: str) -> bool:
    message = timestamp.encode() + b"." + body

    decoded_key = base64.b64decode(os.environ.get("BRICK_SIGNATURE_PUBLIC"))
    
    # wonky logic to verify key (amp'd)
    x = int.from_bytes(decoded_key[1:33], byteorder='big')
    y = int.from_bytes(decoded_key[33:65], byteorder='big')
    
    # Create public key from coordinates
    public_numbers = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1())
    public_key = public_numbers.public_key()

    try:
        public_key.verify(

            base64.b64decode(signature),
            message,
            ec.ECDSA(hashes.SHA256()),
        )
        return True
    except InvalidSignature:
        return False
    
        

