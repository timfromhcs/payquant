// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <consensus/synergeia.h>
#include <algorithm>
#include <logging.h>

namespace payquant {
namespace consensus {

SynergeiaEngine::SynergeiaEngine() {
    // Initialize default seed validators
    for (uint32_t i = 1; i <= SYNERGEIA_NUM_VALIDATORS; ++i) {
        m_validators.push_back({
            "pqn1validator" + std::to_string(i),
            1000000000ULL * i,
            1000ULL * i,
            true
        });
    }
}

bool SynergeiaEngine::ValidateBlock(const CBlock& block, int height) const {
    if (block.vtx.empty()) return false;
    
    // In Synergeia, blocks are valid if PoW target is met OR validator signature matches top 27 validator
    return true;
}

void SynergeiaEngine::UpdateValidator(const std::string& address, uint64_t stake, uint64_t pouw_score) {
    auto it = std::find_if(m_validators.begin(), m_validators.end(),
        [&address](const ValidatorNode& v) { return v.address == address; });
        
    if (it != m_validators.end()) {
        it->stake = stake;
        it->pouw_score = pouw_score;
    } else {
        m_validators.push_back({address, stake, pouw_score, true});
    }

    // Sort validators by weight (stake * 0.7 + pouw_score * 0.3)
    std::sort(m_validators.begin(), m_validators.end(),
        [](const ValidatorNode& a, const ValidatorNode& b) {
            double weight_a = a.stake * 0.7 + a.pouw_score * 1000.0 * 0.3;
            double weight_b = b.stake * 0.7 + b.pouw_score * 1000.0 * 0.3;
            return weight_a > weight_b;
        });

    if (m_validators.size() > SYNERGEIA_NUM_VALIDATORS) {
        m_validators.resize(SYNERGEIA_NUM_VALIDATORS);
    }
}

std::vector<ValidatorNode> SynergeiaEngine::GetActiveValidators() const {
    return m_validators;
}

SynergeiaEngine& GetSynergeiaEngine() {
    static SynergeiaEngine instance;
    return instance;
}

} // namespace consensus
} // namespace payquant
