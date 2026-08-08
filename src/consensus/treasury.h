// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef PAYQUANT_CONSENSUS_TREASURY_H
#define PAYQUANT_CONSENSUS_TREASURY_H

#include <cstdint>
#include <string>
#include <amount.h>

namespace payquant {
namespace consensus {

static constexpr int TREASURY_INTERVAL = 1440; // Every 1,440 blocks (~6 hours at 15s/block)
static constexpr CAmount TREASURY_REWARD_AMOUNT = 50 * COIN; // 50 PQN treasury allocation

class TreasuryManager {
public:
    TreasuryManager();

    /**
     * Check if block height triggers treasury payout
     */
    bool IsTreasuryBlock(int nHeight) const;

    /**
     * Get target treasury donation wallet address
     */
    std::string GetTreasuryAddress() const;

    /**
     * Validate anti-sybil score for recipient wallet
     */
    bool ValidateAntiSybil(const std::string& address) const;
};

TreasuryManager& GetTreasuryManager();

} // namespace consensus
} // namespace payquant

#endif // PAYQUANT_CONSENSUS_TREASURY_H
