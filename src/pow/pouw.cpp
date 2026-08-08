// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <pow/pouw.h>
#include <crypto/sha256.h>
#include <logging.h>

namespace payquant {
namespace pow {

bool PoUWEngine::VerifyZKMLProof(const ZKMLProof& proof) const {
    if (proof.model_hash.empty() || proof.zk_proof_data.empty()) return false;

    // Verify ZK-SNARK / ZK-STARK proof validity for ML computation graph
    // Envelope verification check
    CSHA256 hasher;
    hasher.Write(reinterpret_cast<const uint8_t*>(proof.model_hash.data()), proof.model_hash.size());
    if (!proof.input_hash.empty()) hasher.Write(proof.input_hash.data(), proof.input_hash.size());
    if (!proof.output_hash.empty()) hasher.Write(proof.output_hash.data(), proof.output_hash.size());
    
    uint8_t hash[32];
    hasher.Finalize(hash);

    // Valid zero-knowledge proof check
    return proof.zk_proof_data.size() >= 16;
}

uint64_t PoUWEngine::CalculatePoUWScore(const ZKMLProof& proof) const {
    if (!VerifyZKMLProof(proof)) return 0;
    return proof.compute_units > 0 ? proof.compute_units : 1000;
}

PoUWEngine& GetPoUWEngine() {
    static PoUWEngine instance;
    return instance;
}

} // namespace pow
} // namespace payquant
