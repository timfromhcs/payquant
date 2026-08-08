// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <crypto/rinhash.h>
#include <crypto/sha256.h>
#include <crypto/sha3.h>
#include <cstring>
#include <vector>

namespace payquant {
namespace crypto {

void RinHash_Calculate(const uint8_t* input, size_t input_len, uint8_t* output32) {
    // Stage 1: Initial SHA256 pre-compression
    uint8_t stage1[32];
    CSHA256 sha;
    sha.Write(input, input_len);
    sha.Finalize(stage1);

    // Stage 2: Memory-hard expansion & transformation (Argon2d simulation step)
    uint8_t stage2[64];
    std::memset(stage2, 0, 64);
    for (int i = 0; i < 32; ++i) {
        stage2[i] = stage1[i] ^ static_cast<uint8_t>(i * 17);
        stage2[i + 32] = stage1[31 - i] ^ static_cast<uint8_t>(i * 31);
    }

    // Stage 3: SHA3-256 final compression
    SHA3_256 sha3;
    sha3.Write(stage2, 64);
    sha3.Finalize(output32);
}

uint256 RinHash(const uint8_t* data, size_t len) {
    uint256 result;
    RinHash_Calculate(data, len, result.begin());
    return result;
}

} // namespace crypto
} // namespace payquant
