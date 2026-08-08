// Copyright (c) 2025-2026 PayQuant Contributors
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef PAYQUANT_CRYPTO_MLDSA65_H
#define PAYQUANT_CRYPTO_MLDSA65_H

#include <cstddef>
#include <cstdint>
#include <vector>
#include <string>
#include <array>

/**
 * PayQuant Post-Quantum Cryptography Module: ML-DSA-65 (FIPS 204) & SLH-DSA (FIPS 205)
 */
namespace payquant {
namespace crypto {

static constexpr size_t MLDSA65_PUBLIC_KEY_BYTES = 1952;
static constexpr size_t MLDSA65_SECRET_KEY_BYTES = 4032;
static constexpr size_t MLDSA65_SIGNATURE_BYTES  = 3309;

struct MLDSA65KeyPair {
    std::vector<uint8_t> pubkey;
    std::vector<uint8_t> privkey;
};

/**
 * Generate a new ML-DSA-65 post-quantum keypair from seed/entropy
 */
MLDSA65KeyPair MLDSA65_KeyGen(const std::vector<uint8_t>& seed = {});

/**
 * Create an ML-DSA-65 signature for a message hash
 */
std::vector<uint8_t> MLDSA65_Sign(const std::vector<uint8_t>& privkey, const uint8_t* msg, size_t msg_len);

/**
 * Verify an ML-DSA-65 post-quantum signature
 */
bool MLDSA65_Verify(const std::vector<uint8_t>& pubkey, const uint8_t* msg, size_t msg_len, const std::vector<uint8_t>& sig);

/**
 * Fallback SLH-DSA verification for secondary quantum verification layer
 */
bool SLHDSA_Verify(const std::vector<uint8_t>& pubkey, const uint8_t* msg, size_t msg_len, const std::vector<uint8_t>& sig);

} // namespace crypto
} // namespace payquant

#endif // PAYQUANT_CRYPTO_MLDSA65_H
