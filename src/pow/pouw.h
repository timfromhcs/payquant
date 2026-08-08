// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef PAYQUANT_POW_POUW_H
#define PAYQUANT_POW_POUW_H

#include <cstdint>
#include <vector>
#include <string>

namespace payquant {
namespace pow {

struct ZKMLProof {
    std::string model_hash;
    std::vector<uint8_t> input_hash;
    std::vector<uint8_t> output_hash;
    std::vector<uint8_t> zk_proof_data;
    uint64_t compute_units;
};

class PoUWEngine {
public:
    PoUWEngine() = default;

    /**
     * Verify zero-knowledge machine learning compute proof for PoUW
     */
    bool VerifyZKMLProof(const ZKMLProof& proof) const;

    /**
     * Calculate PoUW difficulty score reward adjustment
     */
    uint64_t CalculatePoUWScore(const ZKMLProof& proof) const;
};

PoUWEngine& GetPoUWEngine();

} // namespace pow
} // namespace payquant

#endif // PAYQUANT_POW_POUW_H
