// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef PAYQUANT_SECURITY_SENTINEL_H
#define PAYQUANT_SECURITY_SENTINEL_H

#include <cstdint>
#include <string>
#include <vector>

namespace payquant {
namespace security {

static constexpr int WARMUP_PERIOD_BLOCKS = 10000;

struct DIDIdentity {
    std::string did_uri;
    std::vector<uint8_t> public_key;
    bool verified;
};

class SecuritySentinel {
public:
    SecuritySentinel() = default;

    /**
     * Check if network is in early Warmup Period (0 to 10,000 blocks)
     */
    bool IsInWarmupPeriod(int nHeight) const;

    /**
     * Verify W3C Decentralized Identifier (DID)
     */
    bool VerifyDID(const std::string& did_uri, const std::vector<uint8_t>& pubkey) const;
};

SecuritySentinel& GetSecuritySentinel();

} // namespace security
} // namespace payquant

#endif // PAYQUANT_SECURITY_SENTINEL_H
