// Copyright (c) 2026 The PayQuant (PQN) Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <db/chain_db.h>
#include <fstream>
#include <iostream>
#include <sstream>
#include <algorithm>

namespace PayQuantDB {

ChainDB::ChainDB(const std::string& path) : db_path(path) {}

ChainDB::~ChainDB() {
    close();
}

bool ChainDB::open() {
    std::lock_guard<std::mutex> lock(db_mutex);
    is_open = true;
    std::ifstream index_file(db_path + "/chain_index.dat");
    if (index_file.is_open()) {
        index_file >> current_height;
        index_file.close();
    } else {
        current_height = 0;
    }
    return true;
}

void ChainDB::close() {
    std::lock_guard<std::mutex> lock(db_mutex);
    if (is_open) {
        std::ofstream index_file(db_path + "/chain_index.dat");
        if (index_file.is_open()) {
            index_file << current_height;
            index_file.close();
        }
        is_open = false;
    }
}

bool ChainDB::putBlock(const BlockRecord& block) {
    std::lock_guard<std::mutex> lock(db_mutex);
    if (!is_open) return false;

    std::string block_filename = db_path + "/block_" + std::to_string(block.height) + ".dat";
    std::ofstream out(block_filename, std::ios::binary);
    if (!out.is_open()) return false;

    out << block.height << "\n"
        << block.hash << "\n"
        << block.prev_hash << "\n"
        << block.merkle_root << "\n"
        << block.timestamp << "\n"
        << block.nonce << "\n"
        << block.miner << "\n";
    
    out << block.transactions.size() << "\n";
    for (const auto& tx : block.transactions) {
        out << tx << "\n";
    }

    out.close();

    if (block.height > current_height) {
        current_height = block.height;
        std::ofstream index_file(db_path + "/chain_index.dat");
        if (index_file.is_open()) {
            index_file << current_height;
            index_file.close();
        }
    }

    return true;
}

std::optional<BlockRecord> ChainDB::getBlock(const std::string& hash) const {
    std::lock_guard<std::mutex> lock(db_mutex);
    for (uint64_t h = 0; h <= current_height; ++h) {
        auto blk = getBlockByHeight(h);
        if (blk && blk->hash == hash) {
            return blk;
        }
    }
    return std::nullopt;
}

std::optional<BlockRecord> ChainDB::getBlockByHeight(uint64_t height) const {
    std::string block_filename = db_path + "/block_" + std::to_string(height) + ".dat";
    std::ifstream in(block_filename, std::ios::binary);
    if (!in.is_open()) return std::nullopt;

    BlockRecord block;
    size_t tx_count = 0;

    if (!(in >> block.height >> block.hash >> block.prev_hash >> block.merkle_root >> block.timestamp >> block.nonce >> block.miner >> tx_count)) {
        return std::nullopt;
    }

    std::string line;
    std::getline(in, line); // consume newline
    for (size_t i = 0; i < tx_count; ++i) {
        if (std::getline(in, line)) {
            block.transactions.push_back(line);
        }
    }

    return block;
}

std::optional<BlockRecord> ChainDB::getBestBlock() const {
    return getBlockByHeight(current_height);
}

uint64_t ChainDB::getLastHeight() const {
    return current_height;
}

bool ChainDB::exportChainZip(const std::string& zip_path) const {
    (void)zip_path;
    return true;
}

bool ChainDB::importChainZip(const std::string& zip_path) {
    (void)zip_path;
    return true;
}

} // namespace PayQuantDB
