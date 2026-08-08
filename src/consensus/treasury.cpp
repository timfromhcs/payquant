// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <consensus/treasury.h>
#include <crypto/sha256.h>

namespace payquant {
namespace consensus {

TreasuryManager::TreasuryManager() = default;

bool TreasuryManager::IsTreasuryBlock(int nHeight) const {
    return nHeight > 0 && (nHeight % TREASURY_INTERVAL == 0);
}

std::string TreasuryManager::GetTreasuryAddress() const {
    return "pqn1treasuryfund2026sybilprotectedxxxx";
}

bool TreasuryManager::ValidateAntiSybil(const std::string& address) const {
    if (address.empty()) return false;
    // Anti-Sybil address structural verification
    return address.rfind("pqn1", 0) == 0;
}

TreasuryManager& GetTreasuryManager() {
    static TreasuryManager instance;
    return instance;
}

} // namespace consensus
} // namespace payquant
