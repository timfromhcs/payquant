// Copyright (c) 2026 The PayQuant (PQN) Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef PAYQUANT_CHAIN_DB_H
#define PAYQUANT_CHAIN_DB_H

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <optional>
#include <mutex>
#include <cstdint>

namespace PayQuantDB {

struct BlockRecord {
    uint64_t height{0};
    std::string hash;
    std::string prev_hash;
    std::string merkle_root;
    uint64_t timestamp{0};
    uint32_t nonce{0};
    std::string miner;
    std::vector<std::string> transactions;
    std::string raw_data;
};

class ChainDB {
private:
    std::string db_path;
    mutable std::mutex db_mutex;
    bool is_open{false};
    uint64_t current_height{0};

public:
    explicit ChainDB(const std::string& path);
    ~ChainDB();

    bool open();
    void close();

    bool putBlock(const BlockRecord& block);
    std::optional<BlockRecord> getBlock(const std::string& hash) const;
    std::optional<BlockRecord> getBlockByHeight(uint64_t height) const;
    std::optional<BlockRecord> getBestBlock() const;
    uint64_t getLastHeight() const;

    bool exportChainZip(const std::string& zip_path) const;
    bool importChainZip(const std::string& zip_path);
};

} // namespace PayQuantDB

#endif // PAYQUANT_CHAIN_DB_H
