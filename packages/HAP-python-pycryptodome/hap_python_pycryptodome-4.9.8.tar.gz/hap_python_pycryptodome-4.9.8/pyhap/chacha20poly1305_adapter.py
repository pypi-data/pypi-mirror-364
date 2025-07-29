"""ChaCha20-Poly1305 implementation using pycryptodome as a replacement for chacha20poly1305_reuseable."""

from Crypto.Cipher import ChaCha20_Poly1305
from .crypto_adapter import InvalidTag


class ChaCha20Poly1305Reusable:
    """ChaCha20-Poly1305 cipher that can be reused for multiple operations."""
    
    def __init__(self, key: bytes):
        """Initialize with a key."""
        self.key = key
    
    def encrypt(self, nonce: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
        """Encrypt plaintext with the given nonce and optional additional authenticated data.
        
        Returns ciphertext + tag (concatenated).
        """
        cipher = ChaCha20_Poly1305.new(key=self.key, nonce=nonce)
        if aad:
            cipher.update(aad)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        return ciphertext + tag
    
    def decrypt(self, nonce: bytes, ciphertext_with_tag: bytes, aad: bytes = b"") -> bytes:
        """Decrypt ciphertext with the given nonce and optional additional authenticated data.
        
        The ciphertext_with_tag should be ciphertext + tag (concatenated).
        """
        if len(ciphertext_with_tag) < 16:  # Tag is 16 bytes
            raise InvalidTag("Ciphertext too short to contain a valid tag")
        
        # Split ciphertext and tag
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]
        
        cipher = ChaCha20_Poly1305.new(key=self.key, nonce=nonce)
        if aad:
            cipher.update(aad)
        
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext
        except ValueError as e:
            raise InvalidTag(str(e))


# For backward compatibility
ChaCha20Poly1305Reusable = ChaCha20Poly1305Reusable
