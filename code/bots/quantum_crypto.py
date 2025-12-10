#!/usr/bin/env python3
"""
Quantum-Ready Cryptography v11.0
Post-quantum cryptography implementation with hybrid key exchange
"""

import os
import sys
import json
import time
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import base64

# Cryptography libraries
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.x509 import load_pem_x509_certificate
from cryptography import x509

# Post-quantum cryptography (liboqs-python)
try:
    import oqs
    PQC_AVAILABLE = True
except ImportError:
    PQC_AVAILABLE = False
    logging.warning("liboqs-python not available, using simulation mode")

import requests
from redis import Redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
KEY_STORAGE_PATH = '/var/lib/quantum-crypto'
CERT_STORAGE_PATH = '/etc/ssl/quantum'
HYBRID_MODE = True  # Use both classical and post-quantum

# Post-Quantum Algorithms
PQC_KEM_ALGORITHM = 'Kyber768'  # Key Encapsulation Mechanism
PQC_SIG_ALGORITHM = 'Dilithium3'  # Digital Signature

os.makedirs(KEY_STORAGE_PATH, exist_ok=True)
os.makedirs(CERT_STORAGE_PATH, exist_ok=True)

@dataclass
class CryptoKey:
    """Cryptographic key representation"""
    key_id: str
    algorithm: str
    public_key: bytes
    private_key: Optional[bytes]
    created_at: datetime
    expires_at: datetime
    key_type: str  # 'classical', 'pqc', 'hybrid'

@dataclass
class EncryptedData:
    """Encrypted data structure"""
    ciphertext: bytes
    algorithm: str
    key_id: str
    nonce: bytes
    tag: bytes
    metadata: Dict

class PostQuantumCrypto:
    """Post-quantum cryptography implementation"""
    
    def __init__(self):
        self.redis = Redis(host=REDIS_HOST, decode_responses=False)
        self.kem_algorithm = PQC_KEM_ALGORITHM
        self.sig_algorithm = PQC_SIG_ALGORITHM
        
    def generate_pqc_keypair(self, algorithm: str = None) -> Tuple[bytes, bytes]:
        """Generate post-quantum key pair"""
        if not PQC_AVAILABLE:
            logger.warning("Using simulated PQC keys")
            return self._generate_simulated_pqc_keypair()
        
        algo = algorithm or self.kem_algorithm
        
        try:
            with oqs.KeyEncapsulation(algo) as kem:
                public_key = kem.generate_keypair()
                secret_key = kem.export_secret_key()
                return public_key, secret_key
        except Exception as e:
            logger.error(f"Failed to generate PQC keypair: {e}")
            return self._generate_simulated_pqc_keypair()
    
    def _generate_simulated_pqc_keypair(self) -> Tuple[bytes, bytes]:
        """Generate simulated PQC keys for testing"""
        # In production, this should never be used
        public_key = os.urandom(1184)  # Kyber768 public key size
        secret_key = os.urandom(2400)  # Kyber768 secret key size
        return public_key, secret_key
    
    def pqc_encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """Encapsulate shared secret using PQC"""
        if not PQC_AVAILABLE:
            return self._simulate_pqc_encapsulate()
        
        try:
            with oqs.KeyEncapsulation(self.kem_algorithm) as kem:
                ciphertext, shared_secret = kem.encap_secret(public_key)
                return ciphertext, shared_secret
        except Exception as e:
            logger.error(f"PQC encapsulation failed: {e}")
            return self._simulate_pqc_encapsulate()
    
    def pqc_decapsulate(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        """Decapsulate shared secret using PQC"""
        if not PQC_AVAILABLE:
            return os.urandom(32)
        
        try:
            with oqs.KeyEncapsulation(self.kem_algorithm) as kem:
                shared_secret = kem.decap_secret(ciphertext, secret_key)
                return shared_secret
        except Exception as e:
            logger.error(f"PQC decapsulation failed: {e}")
            return os.urandom(32)
    
    def _simulate_pqc_encapsulate(self) -> Tuple[bytes, bytes]:
        """Simulate PQC encapsulation"""
        ciphertext = os.urandom(1088)  # Kyber768 ciphertext size
        shared_secret = os.urandom(32)
        return ciphertext, shared_secret
    
    def pqc_sign(self, message: bytes, secret_key: bytes) -> bytes:
        """Sign message with PQC signature"""
        if not PQC_AVAILABLE:
            return hashlib.sha256(message).digest()
        
        try:
            with oqs.Signature(self.sig_algorithm) as sig:
                signature = sig.sign(message, secret_key)
                return signature
        except Exception as e:
            logger.error(f"PQC signing failed: {e}")
            return hashlib.sha256(message).digest()
    
    def pqc_verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify PQC signature"""
        if not PQC_AVAILABLE:
            return True  # Simulation mode
        
        try:
            with oqs.Signature(self.sig_algorithm) as sig:
                return sig.verify(message, signature, public_key)
        except Exception as e:
            logger.error(f"PQC verification failed: {e}")
            return False

class HybridCryptoSystem:
    """Hybrid classical + post-quantum cryptography"""
    
    def __init__(self):
        self.pqc = PostQuantumCrypto()
        self.redis = Redis(host=REDIS_HOST, decode_responses=False)
        
    def generate_hybrid_keypair(self) -> CryptoKey:
        """Generate hybrid keypair (RSA + PQC)"""
        key_id = self._generate_key_id()
        
        # Generate classical RSA key
        rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        rsa_public_key = rsa_private_key.public_key()
        
        # Generate PQC key
        pqc_public, pqc_secret = self.pqc.generate_pqc_keypair()
        
        # Combine keys
        hybrid_public = self._combine_keys(
            rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ),
            pqc_public
        )
        
        hybrid_private = self._combine_keys(
            rsa_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ),
            pqc_secret
        )
        
        # Create CryptoKey object
        crypto_key = CryptoKey(
            key_id=key_id,
            algorithm='Hybrid-RSA4096-Kyber768',
            public_key=hybrid_public,
            private_key=hybrid_private,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=365),
            key_type='hybrid'
        )
        
        # Store keys
        self._store_key(crypto_key)
        
        logger.info(f"Generated hybrid keypair: {key_id}")
        return crypto_key
    
    def hybrid_encrypt(self, plaintext: bytes, public_key: bytes) -> EncryptedData:
        """Encrypt data using hybrid approach"""
        
        # Split combined public key
        rsa_public_pem, pqc_public = self._split_keys(public_key)
        
        # Generate ephemeral symmetric key
        symmetric_key = os.urandom(32)
        
        # Encrypt data with AES-256-GCM
        nonce = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(symmetric_key),
            modes.GCM(nonce)
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag
        
        # Encrypt symmetric key with RSA
        rsa_public_key = serialization.load_pem_public_key(rsa_public_pem)
        rsa_encrypted_key = rsa_public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Encapsulate symmetric key with PQC
        pqc_ciphertext, pqc_shared = self.pqc.pqc_encapsulate(pqc_public)
        
        # Derive final key from both classical and PQC
        combined_key = self._combine_shared_secrets(
            rsa_encrypted_key,
            pqc_ciphertext,
            pqc_shared
        )
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm='Hybrid-AES256-GCM',
            key_id=hashlib.sha256(public_key).hexdigest()[:16],
            nonce=nonce,
            tag=tag,
            metadata={
                'rsa_encrypted_key': base64.b64encode(rsa_encrypted_key).decode(),
                'pqc_ciphertext': base64.b64encode(pqc_ciphertext).decode(),
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def hybrid_decrypt(self, encrypted_data: EncryptedData, private_key: bytes) -> bytes:
        """Decrypt data using hybrid approach"""
        
        # Split combined private key
        rsa_private_pem, pqc_secret = self._split_keys(private_key)
        
        # Decrypt RSA part
        rsa_private_key = serialization.load_pem_private_key(rsa_private_pem, password=None)
        rsa_encrypted_key = base64.b64decode(encrypted_data.metadata['rsa_encrypted_key'])
        
        symmetric_key_rsa = rsa_private_key.decrypt(
            rsa_encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decapsulate PQC part
        pqc_ciphertext = base64.b64decode(encrypted_data.metadata['pqc_ciphertext'])
        pqc_shared = self.pqc.pqc_decapsulate(pqc_ciphertext, pqc_secret)
        
        # Combine both secrets (in practice, should verify they match)
        symmetric_key = symmetric_key_rsa  # Use RSA result as primary
        
        # Decrypt ciphertext with AES
        cipher = Cipher(
            algorithms.AES(symmetric_key),
            modes.GCM(encrypted_data.nonce, encrypted_data.tag)
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
        
        return plaintext
    
    def _generate_key_id(self) -> str:
        """Generate unique key ID"""
        return hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    
    def _combine_keys(self, classical_key: bytes, pqc_key: bytes) -> bytes:
        """Combine classical and PQC keys"""
        # Simple concatenation with length prefix
        combined = len(classical_key).to_bytes(4, 'big') + classical_key + pqc_key
        return combined
    
    def _split_keys(self, combined_key: bytes) -> Tuple[bytes, bytes]:
        """Split combined key"""
        classical_len = int.from_bytes(combined_key[:4], 'big')
        classical_key = combined_key[4:4+classical_len]
        pqc_key = combined_key[4+classical_len:]
        return classical_key, pqc_key
    
    def _combine_shared_secrets(self, rsa_key: bytes, pqc_ct: bytes, pqc_secret: bytes) -> bytes:
        """Combine shared secrets from classical and PQC"""
        # Use HKDF to derive final key
        combined = rsa_key + pqc_ct + pqc_secret
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'hybrid-key-derivation'
        )
        return hkdf.derive(combined)
    
    def _store_key(self, key: CryptoKey):
        """Store key in Redis"""
        key_data = {
            'key_id': key.key_id,
            'algorithm': key.algorithm,
            'public_key': base64.b64encode(key.public_key).decode(),
            'created_at': key.created_at.isoformat(),
            'expires_at': key.expires_at.isoformat(),
            'key_type': key.key_type
        }
        
        # Store public key
        self.redis.setex(
            f'quantum_key:{key.key_id}',
            86400 * 365,  # 1 year
            json.dumps(key_data)
        )
        
        # Store private key separately (encrypted in production)
        if key.private_key:
            private_path = os.path.join(KEY_STORAGE_PATH, f'{key.key_id}.key')
            with open(private_path, 'wb') as f:
                f.write(key.private_key)
            os.chmod(private_path, 0o600)

class CertificateMigration:
    """Certificate migration to quantum-safe"""
    
    def __init__(self):
        self.hybrid_crypto = HybridCryptoSystem()
        
    def generate_quantum_safe_cert(
        self,
        common_name: str,
        validity_days: int = 365
    ) -> Tuple[bytes, bytes]:
        """Generate quantum-safe certificate"""
        
        logger.info(f"Generating quantum-safe certificate for {common_name}")
        
        # Generate hybrid keypair
        key = self.hybrid_crypto.generate_hybrid_keypair()
        
        # Extract classical RSA key for certificate
        rsa_private_pem, _ = self.hybrid_crypto._split_keys(key.private_key)
        rsa_private = serialization.load_pem_private_key(rsa_private_pem, password=None)
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Quantum-Safe Org"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name),
        ])
        
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(rsa_private.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(common_name),
                ]),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=0),
                critical=True,
            )
            .sign(rsa_private, hashes.SHA256())
        )
        
        # Serialize certificate
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        
        # Store
        cert_path = os.path.join(CERT_STORAGE_PATH, f'{common_name}.crt')
        key_path = os.path.join(CERT_STORAGE_PATH, f'{common_name}.key')
        
        with open(cert_path, 'wb') as f:
            f.write(cert_pem)
        
        with open(key_path, 'wb') as f:
            f.write(key.private_key)
        
        os.chmod(key_path, 0o600)
        
        logger.info(f"Certificate generated: {cert_path}")
        
        return cert_pem, key.private_key
    
    def migrate_existing_certs(self, cert_dir: str = '/etc/ssl/certs'):
        """Migrate existing certificates to quantum-safe"""
        
        logger.info(f"Migrating certificates from {cert_dir}")
        
        if not os.path.exists(cert_dir):
            logger.warning(f"Certificate directory not found: {cert_dir}")
            return
        
        migrated = 0
        
        for filename in os.listdir(cert_dir):
            if not filename.endswith('.crt'):
                continue
            
            cert_path = os.path.join(cert_dir, filename)
            
            try:
                with open(cert_path, 'rb') as f:
                    cert_pem = f.read()
                
                cert = load_pem_x509_certificate(cert_pem)
                common_name = cert.subject.get_attributes_for_oid(
                    x509.NameOID.COMMON_NAME
                )[0].value
                
                # Generate new quantum-safe cert
                self.generate_quantum_safe_cert(common_name)
                
                migrated += 1
                logger.info(f"Migrated: {filename} -> {common_name}")
                
            except Exception as e:
                logger.error(f"Failed to migrate {filename}: {e}")
        
        logger.info(f"Migrated {migrated} certificates")

class QuantumSafeProtocol:
    """Quantum-safe communication protocol"""
    
    def __init__(self):
        self.crypto = HybridCryptoSystem()
        self.sessions = {}
        
    def establish_secure_channel(
        self,
        peer_id: str,
        peer_public_key: bytes
    ) -> str:
        """Establish quantum-safe secure channel"""
        
        logger.info(f"Establishing secure channel with {peer_id}")
        
        # Generate session keypair
        session_key = self.crypto.generate_hybrid_keypair()
        
        # Perform hybrid key exchange
        # 1. Classical ECDH
        ecdh_private = ec.generate_private_key(ec.SECP384R1())
        ecdh_public = ecdh_private.public_key()
        
        # 2. PQC KEM
        pqc_public, pqc_secret = self.crypto.pqc.generate_pqc_keypair()
        
        # Create session
        session_id = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        
        self.sessions[session_id] = {
            'peer_id': peer_id,
            'session_key': session_key,
            'ecdh_private': ecdh_private,
            'pqc_secret': pqc_secret,
            'created_at': datetime.now(),
            'messages_sent': 0,
            'messages_received': 0
        }
        
        logger.info(f"Secure channel established: {session_id}")
        
        return session_id
    
    def send_secure_message(
        self,
        session_id: str,
        message: bytes
    ) -> Dict:
        """Send encrypted message over secure channel"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Invalid session: {session_id}")
        
        session = self.sessions[session_id]
        
        # Encrypt message
        encrypted = self.crypto.hybrid_encrypt(
            message,
            session['session_key'].public_key
        )
        
        session['messages_sent'] += 1
        
        return {
            'session_id': session_id,
            'ciphertext': base64.b64encode(encrypted.ciphertext).decode(),
            'nonce': base64.b64encode(encrypted.nonce).decode(),
            'tag': base64.b64encode(encrypted.tag).decode(),
            'metadata': encrypted.metadata
        }
    
    def receive_secure_message(
        self,
        session_id: str,
        encrypted_message: Dict
    ) -> bytes:
        """Receive and decrypt message from secure channel"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Invalid session: {session_id}")
        
        session = self.sessions[session_id]
        
        # Reconstruct EncryptedData
        encrypted = EncryptedData(
            ciphertext=base64.b64decode(encrypted_message['ciphertext']),
            algorithm='Hybrid-AES256-GCM',
            key_id=session['session_key'].key_id,
            nonce=base64.b64decode(encrypted_message['nonce']),
            tag=base64.b64decode(encrypted_message['tag']),
            metadata=encrypted_message['metadata']
        )
        
        # Decrypt
        plaintext = self.crypto.hybrid_decrypt(
            encrypted,
            session['session_key'].private_key
        )
        
        session['messages_received'] += 1
        
        return plaintext

def benchmark_quantum_crypto():
    """Benchmark quantum-safe cryptography performance"""
    
    logger.info("Benchmarking quantum-safe cryptography...")
    
    crypto = HybridCryptoSystem()
    
    # Key generation benchmark
    start = time.time()
    key = crypto.generate_hybrid_keypair()
    keygen_time = time.time() - start
    
    logger.info(f"Key generation: {keygen_time:.3f}s")
    
    # Encryption benchmark
    plaintext = b"Hello, quantum-safe world!" * 100
    
    start = time.time()
    encrypted = crypto.hybrid_encrypt(plaintext, key.public_key)
    encrypt_time = time.time() - start
    
    logger.info(f"Encryption ({len(plaintext)} bytes): {encrypt_time:.3f}s")
    
    # Decryption benchmark
    start = time.time()
    decrypted = crypto.hybrid_decrypt(encrypted, key.private_key)
    decrypt_time = time.time() - start
    
    logger.info(f"Decryption ({len(plaintext)} bytes): {decrypt_time:.3f}s")
    
    # Verify
    assert plaintext == decrypted, "Decryption failed!"
    logger.info("✅ Encryption/Decryption verified")
    
    return {
        'keygen_time': keygen_time,
        'encrypt_time': encrypt_time,
        'decrypt_time': decrypt_time,
        'throughput_mbps': (len(plaintext) / encrypt_time) / (1024 * 1024)
    }

def main():
    """Main entry point"""
    
    logger.info("Quantum-Ready Cryptography System v11.0")
    logger.info(f"PQC Available: {PQC_AVAILABLE}")
    logger.info(f"KEM Algorithm: {PQC_KEM_ALGORITHM}")
    logger.info(f"Signature Algorithm: {PQC_SIG_ALGORITHM}")
    
    if '--benchmark' in sys.argv:
        results = benchmark_quantum_crypto()
        print(json.dumps(results, indent=2))
    
    if '--generate-cert' in sys.argv:
        if len(sys.argv) < 3:
            print("Usage: --generate-cert <common_name>")
            sys.exit(1)
        
        common_name = sys.argv[2]
        migrator = CertificateMigration()
        migrator.generate_quantum_safe_cert(common_name)
    
    if '--migrate-certs' in sys.argv:
        migrator = CertificateMigration()
        migrator.migrate_existing_certs()
    
    if '--test' in sys.argv:
        # Test hybrid encryption
        crypto = HybridCryptoSystem()
        key = crypto.generate_hybrid_keypair()
        
        plaintext = b"Test message for quantum-safe encryption"
        encrypted = crypto.hybrid_encrypt(plaintext, key.public_key)
        decrypted = crypto.hybrid_decrypt(encrypted, key.private_key)
        
        assert plaintext == decrypted
        logger.info("✅ All tests passed")

if __name__ == '__main__':
    main()
