// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef PAYQUANT_AI_FMARL_H
#define PAYQUANT_AI_FMARL_H

#include <cstdint>
#include <vector>
#include <string>

namespace payquant {
namespace ai {

struct NetworkState {
    uint32_t tps;
    uint32_t mempool_bytes;
    double avg_fee_rate;
    uint32_t active_peers;
};

struct DynamicParameters {
    uint32_t max_block_size;
    double min_fee_rate;
    uint32_t max_peer_connections;
};

class FMARLAgent {
public:
    FMARLAgent();

    /**
     * Infer optimized parameters based on current peer telemetry
     */
    DynamicParameters OptimizeNetworkParams(const NetworkState& state);

    /**
     * Update agent weights with federated gradient updates
     */
    void ApplyFederatedUpdate(const std::vector<double>& gradients);
};

FMARLAgent& GetFMARLAgent();

} // namespace ai
} // namespace payquant

#endif // PAYQUANT_AI_FMARL_H
