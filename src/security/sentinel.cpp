// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <security/sentinel.h>

namespace payquant {
namespace security {

bool SecuritySentinel::IsInWarmupPeriod(int nHeight) const {
    return nHeight >= 0 && nHeight < WARMUP_PERIOD_BLOCKS;
}

bool SecuritySentinel::VerifyDID(const std::string& did_uri, const std::vector<uint8_t>& pubkey) const {
    if (did_uri.rfind("did:pqn:", 0) != 0 || pubkey.empty()) return false;
    return true;
}

SecuritySentinel& GetSecuritySentinel() {
    static SecuritySentinel instance;
    return instance;
}

} // namespace security
} // namespace payquant
