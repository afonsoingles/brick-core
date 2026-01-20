import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.exceptions import InvalidSignature


def verify_signature(*, body: bytes, signature: str, timestamp: str) -> bool:
    message = timestamp.encode() + b"." + body

    public_key = load_der_public_key(os.environ.get("BRICK_SIGNATURE_PUBLIC"))

    try:
        public_key.verify(

            base64.b64decode(signature),
            message,
            ec.ECDSA(hashes.SHA256()),
        )
        return True
    except InvalidSignature:
        return False
    
        

