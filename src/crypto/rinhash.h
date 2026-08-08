// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef PAYQUANT_CRYPTO_RINHASH_H
#define PAYQUANT_CRYPTO_RINHASH_H

#include <cstddef>
#include <cstdint>
#include <uint256.h>
#include <vector>

namespace payquant {
namespace crypto {

/**
 * RinHash PoW algorithm: Multi-stage Memory-Hard & ASIC-Resistant Hashing
 * Stage 1: BLAKE3 (Fast pre-hash expansion)
 * Stage 2: Argon2d (Memory-hard execution)
 * Stage 3: SHA3-256 (Final compression)
 */
uint256 RinHash(const uint8_t* data, size_t len);

void RinHash_Calculate(const uint8_t* input, size_t input_len, uint8_t* output32);

} // namespace crypto
} // namespace payquant

#endif // PAYQUANT_CRYPTO_RINHASH_H
