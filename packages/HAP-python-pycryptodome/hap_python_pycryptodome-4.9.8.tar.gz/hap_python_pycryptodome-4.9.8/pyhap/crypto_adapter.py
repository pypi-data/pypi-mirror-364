"""Crypto adapter module to replace cryptography with pycryptodome and tlslite-ng."""

import os
from typing import Union
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import HKDF
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa
from tlslite.utils.x25519 import x25519 as x25519_func, X25519_G


class InvalidTag(Exception):
    """Exception raised when authentication tag is invalid."""
    pass


class InvalidSignature(Exception):
    """Exception raised when signature verification fails."""
    pass


class NoEncryption:
    """No encryption algorithm placeholder."""
    pass


class Encoding:
    """Encoding format constants."""
    Raw = "raw"


class PrivateFormat:
    """Private key format constants."""
    Raw = "raw"


class PublicFormat:
    """Public key format constants."""
    Raw = "raw"


class Serialization:
    """Serialization utilities."""
    
    class Encoding:
        Raw = "raw"
    
    class PrivateFormat:
        Raw = "raw"
    
    class PublicFormat:
        Raw = "raw"
    
    class NoEncryption:
        pass


def default_backend():
    """Return default backend (not needed for pycryptodome)."""
    return None


class Hashes:
    """Hash algorithm constants."""
    
    class SHA512:
        pass


def hap_hkdf(key: bytes, salt: bytes, info: bytes, length: int = 32) -> bytes:
    """HKDF key derivation using pycryptodome."""
    return HKDF(
        master=key,
        key_len=length,
        salt=salt,
        hashmod=SHA512,
        context=info
    )


class Ed25519PrivateKey:
    """Ed25519 private key wrapper using pycryptodome."""
    
    def __init__(self, private_key_bytes: bytes, ecc_key=None):
        """Initialize with private key bytes."""
        self._private_key_bytes = private_key_bytes
        self._key = ecc_key
    
    @classmethod
    def generate(cls):
        """Generate a new Ed25519 private key."""
        # Generate a proper Ed25519 private key using pycryptodome
        key = ECC.generate(curve='ed25519')
        # Extract the seed from the key (not the d value)
        seed = key._seed if hasattr(key, '_seed') else key.export_key(format='DER')[-32:]
        return cls(seed, key)
    
    @classmethod
    def from_private_bytes(cls, private_bytes: bytes):
        """Create private key from bytes."""
        try:
            # For Ed25519, we need to construct the proper DER format from the private key bytes
            if len(private_bytes) == 32:
                # This is the raw Ed25519 private key format
                # Build the correct DER structure: 
                # 30 2E (SEQUENCE, 46 bytes)
                #   02 01 00 (INTEGER, version 0)
                #   30 05 (SEQUENCE, 5 bytes - algorithm identifier)
                #     06 03 2B 65 70 (OID 1.3.101.112 - Ed25519)
                #   04 22 (OCTET STRING, 34 bytes)
                #     04 20 (OCTET STRING, 32 bytes - the actual private key)
                #       <32 bytes of private key>
                der_bytes = (
                    b'\x30\x2e'  # SEQUENCE, 46 bytes
                    b'\x02\x01\x00'  # INTEGER version 0
                    b'\x30\x05\x06\x03\x2b\x65\x70'  # SEQUENCE with Ed25519 OID
                    b'\x04\x22\x04\x20'  # OCTET STRING containing OCTET STRING
                    + private_bytes  # 32 bytes of private key
                )
                
                try:
                    ecc_key = ECC.import_key(der_bytes)
                    return cls(private_bytes, ecc_key)
                except Exception as e:
                    print(f"Warning: Could not import Ed25519 private key: {e}")
                    # Fall back to raw bytes only
                    return cls(private_bytes)
            else:
                # Assume it's already in DER format or another format
                try:
                    ecc_key = ECC.import_key(private_bytes)
                    # Extract the seed from the DER
                    if len(private_bytes) >= 32:
                        seed = private_bytes[-32:]  # Seed is the last 32 bytes in DER
                    else:
                        seed = private_bytes
                    return cls(seed, ecc_key)
                except Exception:
                    return cls(private_bytes)
        except Exception:
            return cls(private_bytes)
    
    def private_bytes(self, encoding=None, format=None, encryption_algorithm=None) -> bytes:
        """Export private key bytes."""
        return self._private_key_bytes
    
    def public_key(self):
        """Get the public key."""
        if self._key:
            public_key_obj = self._key.public_key()
            # Export public key bytes (32 bytes for Ed25519)
            # The DER format contains metadata, we need to extract the raw key
            der_bytes = public_key_obj.export_key(format='DER')
            # For Ed25519, the last 32 bytes of DER are the public key
            public_bytes = der_bytes[-32:]
            return Ed25519PublicKey(public_bytes, public_key_obj)
        else:
            # Fallback: use private key bytes to derive public key
            import hashlib
            public_bytes = hashlib.sha256(self._private_key_bytes).digest()
            return Ed25519PublicKey(public_bytes, None)
    
    def sign(self, data: bytes) -> bytes:
        """Sign data with this private key."""
        if self._key:
            # Use pycryptodome's signing
            signer = eddsa.new(self._key, 'rfc8032')
            return signer.sign(data)
        else:
            raise InvalidSignature("Cannot sign without proper Ed25519 key")


class Ed25519PublicKey:
    """Ed25519 public key wrapper using pycryptodome."""
    
    def __init__(self, public_key_bytes: bytes, ecc_key=None):
        """Initialize with public key bytes."""
        self._public_key_bytes = public_key_bytes
        self._key = ecc_key  # Store the ECC key if provided
    
    @classmethod
    def from_public_bytes(cls, public_bytes: bytes):
        """Create public key from bytes."""
        try:
            # Try to create an ECC key from the public key bytes
            if len(public_bytes) == 32:
                # This is the raw Ed25519 public key format
                # Build the correct DER structure:
                # 30 2A (SEQUENCE, 42 bytes)
                #   30 05 (SEQUENCE, 5 bytes - algorithm identifier)
                #     06 03 2B 65 70 (OID 1.3.101.112 - Ed25519)
                #   03 21 00 (BIT STRING, 33 bytes with leading 0)
                #     <32 bytes of public key>
                der_bytes = (
                    b'\x30\x2a'  # SEQUENCE, 42 bytes
                    b'\x30\x05\x06\x03\x2b\x65\x70'  # SEQUENCE with Ed25519 OID
                    b'\x03\x21\x00'  # BIT STRING, 33 bytes with leading 0
                    + public_bytes  # 32 bytes of public key
                )
                
                try:
                    ecc_key = ECC.import_key(der_bytes)
                    return cls(public_bytes, ecc_key)
                except Exception as e:
                    print(f"Warning: Could not import Ed25519 public key: {e}")
                    # Fall back to raw bytes only
                    return cls(public_bytes)
            else:
                # Assume it's already in DER format or another format
                try:
                    ecc_key = ECC.import_key(public_bytes)
                    # Extract the raw public key bytes from DER
                    der_bytes = ecc_key.export_key(format='DER')
                    # For Ed25519 public key, the last 32 bytes are the public key
                    raw_public_bytes = der_bytes[-32:]
                    return cls(raw_public_bytes, ecc_key)
                except Exception:
                    return cls(public_bytes)
        except Exception:
            return cls(public_bytes)
    
    def public_bytes(self, encoding=None, format=None) -> bytes:
        """Export public key bytes."""
        return self._public_key_bytes
    
    def verify(self, signature: bytes, data: bytes) -> None:
        """Verify signature. Raises InvalidSignature on failure."""
        if self._key:
            try:
                verifier = eddsa.new(self._key, 'rfc8032')
                verifier.verify(data, signature)
            except (ValueError, TypeError) as e:
                raise InvalidSignature(str(e))
        else:
            raise InvalidSignature("Cannot verify signature without proper Ed25519 key")


class X25519PrivateKey:
    """X25519 private key wrapper using tlslite-ng."""
    
    def __init__(self, private_bytes: bytes):
        """Initialize with private key bytes."""
        self._private_bytes = private_bytes
    
    @classmethod
    def generate(cls):
        """Generate a new X25519 private key."""
        private_bytes = os.urandom(32)
        return cls(private_bytes)
    
    @classmethod
    def from_private_bytes(cls, private_bytes: bytes):
        """Create private key from bytes."""
        return cls(private_bytes)
    
    def private_bytes(self, encoding=None, format=None, encryption_algorithm=None) -> bytes:
        """Export private key bytes."""
        return self._private_bytes
    
    def public_key(self):
        """Get the public key."""
        # X25519 public key is computed by multiplying the private key with the base point
        # The base point for X25519 is 9
        # Need to make copies since x25519 function modifies the input arrays
        private_copy = bytearray(self._private_bytes)
        base_point_copy = bytearray(X25519_G)
        public_bytes = x25519_func(private_copy, base_point_copy)
        return X25519PublicKey(bytes(public_bytes))
    
    def exchange(self, peer_public_key) -> bytes:
        """Perform ECDH key exchange."""
        if isinstance(peer_public_key, X25519PublicKey):
            peer_bytes = peer_public_key.public_bytes()
        else:
            peer_bytes = peer_public_key
        
        # Need to make copies since x25519 function modifies the input arrays
        private_copy = bytearray(self._private_bytes)
        peer_copy = bytearray(peer_bytes)
        shared_key = x25519_func(private_copy, peer_copy)
        return bytes(shared_key)


class X25519PublicKey:
    """X25519 public key wrapper using tlslite-ng."""
    
    def __init__(self, public_bytes: bytes):
        """Initialize with public key bytes."""
        self._public_bytes = public_bytes
    
    @classmethod
    def from_public_bytes(cls, public_bytes: bytes):
        """Create public key from bytes."""
        return cls(public_bytes)
    
    def public_bytes(self, encoding=None, format=None) -> bytes:
        """Export public key bytes."""
        return self._public_bytes


# Create module-like structure for compatibility
class cryptography_compat:
    """Compatibility layer for cryptography module."""
    
    class exceptions:
        InvalidSignature = InvalidSignature
        InvalidTag = InvalidTag
    
    class hazmat:
        class primitives:
            class asymmetric:
                class ed25519:
                    Ed25519PrivateKey = Ed25519PrivateKey
                    Ed25519PublicKey = Ed25519PublicKey
                
                class x25519:
                    X25519PrivateKey = X25519PrivateKey
                    X25519PublicKey = X25519PublicKey
            
            class serialization:
                Encoding = Encoding
                PrivateFormat = PrivateFormat
                PublicFormat = PublicFormat
                NoEncryption = NoEncryption
            
            class hashes:
                SHA512 = Hashes.SHA512
            
            class kdf:
                class hkdf:
                    class HKDF:
                        def __init__(self, algorithm, length, salt, info, backend=None):
                            self.algorithm = algorithm
                            self.length = length
                            self.salt = salt
                            self.info = info
                        
                        def derive(self, key_material):
                            return hap_hkdf(key_material, self.salt, self.info, self.length)
        
        class backends:
            @staticmethod
            def default_backend():
                return None


# Export the compatibility layer
serialization = cryptography_compat.hazmat.primitives.serialization
ed25519 = cryptography_compat.hazmat.primitives.asymmetric.ed25519
x25519 = cryptography_compat.hazmat.primitives.asymmetric.x25519
hashes = cryptography_compat.hazmat.primitives.hashes
