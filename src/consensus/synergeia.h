// Copyright (c) 2025-2026 PayQuant Contributors
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef PAYQUANT_CONSENSUS_SYNERGEIA_H
#define PAYQUANT_CONSENSUS_SYNERGEIA_H

#include <cstdint>
#include <vector>
#include <string>
#include <memory>
#include <uint256.h>
#include <primitives/block.h>

namespace payquant {
namespace consensus {

static constexpr uint32_t SYNERGEIA_TARGET_SPACING = 15; // 15 seconds target block time
static constexpr uint32_t SYNERGEIA_NUM_VALIDATORS = 27;  // Top 27 validators

struct ValidatorNode {
    std::string address;
    uint64_t stake;
    uint64_t pouw_score;
    bool active;
};

class SynergeiaEngine {
public:
    SynergeiaEngine();
    
    /**
     * Validate block consensus under Synergeia PoW+PoS rules
     */
    bool ValidateBlock(const CBlock& block, int height) const;

    /**
     * Register or update a validator's stake & PoUW score
     */
    void UpdateValidator(const std::string& address, uint64_t stake, uint64_t pouw_score);

    /**
     * Get active 27 validators for block height
     */
    std::vector<ValidatorNode> GetActiveValidators() const;

private:
    std::vector<ValidatorNode> m_validators;
};

SynergeiaEngine& GetSynergeiaEngine();

} // namespace consensus
} // namespace payquant

#endif // PAYQUANT_CONSENSUS_SYNERGEIA_H
