import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_der_public_key, load_pem_public_key, Encoding, PublicFormat
from cryptography.exceptions import InvalidSignature


def verify_signature(body: bytes, signature: str, timestamp: str) -> bool:
    # Ensure timestamp is string
    timestamp_str = str(timestamp) if not isinstance(timestamp, str) else timestamp
    message = timestamp_str.encode() + b"." + body

    print(f"VERIFY DEBUG: message={message}")
    print(f"VERIFY DEBUG: message (str)={message.decode()}")

    decoded_key = base64.b64decode(os.environ.get("BRICK_SIGNATURE_PUBLIC"))
    
    # wonky logic to verify key (amp'd)
    x = int.from_bytes(decoded_key[1:33], byteorder='big')
    y = int.from_bytes(decoded_key[33:65], byteorder='big')
    
    # Create public key from coordinates
    public_numbers = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1())
    public_key = public_numbers.public_key()

    try:
        decoded_sig = base64.b64decode(signature)
        print(f"VERIFY DEBUG: decoded signature bytes={decoded_sig.hex()}")
        print(f"VERIFY DEBUG: decoded signature length={len(decoded_sig)}")
        
        public_key.verify(
            decoded_sig,
            message,
            ec.ECDSA(hashes.SHA256()),
        )
        print("VERIFY DEBUG: Signature valid!")
        return True
    except InvalidSignature as e:
        print(f"VERIFY DEBUG: Signature invalid - {e}")
        return False
    except Exception as e:
        print(f"VERIFY DEBUG: Error verifying - {e}")
        return False
    
        

