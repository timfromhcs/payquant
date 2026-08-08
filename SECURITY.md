# PayQuant Security Policy

## Post-Quantum Cryptography & Quantum Sentinel

PayQuant mandates ML-DSA-65 (FIPS 204) signatures for transaction verification.
Quantum Sentinel (`contrib/quantum_sentinel.py`) actively audits address entropy to prevent ECDSA Shor's algorithm vulnerabilities.

## Reporting Security Vulnerabilities

Please report security issues to `security@payquant.org`.
