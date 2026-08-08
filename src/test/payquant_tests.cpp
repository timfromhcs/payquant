// Copyright (c) 2026 The PayQuant Developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <crypto/mldsa65.h>
#include <crypto/rinhash.h>
#include <consensus/synergeia.h>
#include <pow/pouw.h>
#include <consensus/treasury.h>
#include <ai/fmarl.h>
#include <security/sentinel.h>

#include <iostream>
#include <cassert>

void TestMLDSA65() {
    std::cout << "[Test] Running ML-DSA-65 Post-Quantum KeyGen & Signature Test..." << std::endl;
    auto keypair = payquant::crypto::MLDSA65_KeyGen({0x01, 0x02, 0x03});
    assert(keypair.pubkey.size() == payquant::crypto::MLDSA65_PUBLIC_KEY_BYTES);
    assert(keypair.privkey.size() == payquant::crypto::MLDSA65_SECRET_KEY_BYTES);

    std::string msg = "PayQuant Quantum Safe Transaction";
    auto sig = payquant::crypto::MLDSA65_Sign(keypair.privkey, reinterpret_cast<const uint8_t*>(msg.data()), msg.size());
    assert(payquant::crypto::MLDSA65_Verify(keypair.pubkey, reinterpret_cast<const uint8_t*>(msg.data()), msg.size(), sig));
    std::cout << "[Test] ML-DSA-65 Test PASSED!" << std::endl;
}

void TestRinHash() {
    std::cout << "[Test] Running RinHash PoW Algorithm Test..." << std::endl;
    std::string input = "PayQuant Block Header";
    uint256 hash = payquant::crypto::RinHash(reinterpret_cast<const uint8_t*>(input.data()), input.size());
    assert(!hash.IsNull());
    std::cout << "[Test] RinHash Test PASSED! Hash: " << hash.ToString() << std::endl;
}

void TestSynergeia() {
    std::cout << "[Test] Running Synergeia Hybrid Consensus Test..." << std::endl;
    auto& engine = payquant::consensus::GetSynergeiaEngine();
    auto validators = engine.GetActiveValidators();
    assert(validators.size() == payquant::consensus::SYNERGEIA_NUM_VALIDATORS);
    std::cout << "[Test] Synergeia Test PASSED! Active Validators: " << validators.size() << std::endl;
}

void TestPoUW() {
    std::cout << "[Test] Running PoUW ZKML Verification Test..." << std::endl;
    auto& pouw = payquant::pow::GetPoUWEngine();
    payquant::pow::ZKMLProof proof{
        "model_llama_3_quant",
        {0x10, 0x20},
        {0x30, 0x40},
        {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10},
        5000
    };
    assert(pouw.VerifyZKMLProof(proof));
    assert(pouw.CalculatePoUWScore(proof) == 5000);
    std::cout << "[Test] PoUW ZKML Test PASSED!" << std::endl;
}

void TestTreasury() {
    std::cout << "[Test] Running Treasury Spenden-Wallet Test..." << std::endl;
    auto& treasury = payquant::consensus::GetTreasuryManager();
    assert(treasury.IsTreasuryBlock(1440));
    assert(!treasury.IsTreasuryBlock(1439));
    assert(treasury.ValidateAntiSybil(treasury.GetTreasuryAddress()));
    std::cout << "[Test] Treasury Test PASSED!" << std::endl;
}

void TestFMARL() {
    std::cout << "[Test] Running FMARL AI Agent Test..." << std::endl;
    auto& fmarl = payquant::ai::GetFMARLAgent();
    payquant::ai::NetworkState state{1500, 15000000, 45.0, 120};
    auto params = fmarl.OptimizeNetworkParams(state);
    assert(params.max_block_size == 4 * 1024 * 1024);
    std::cout << "[Test] FMARL Test PASSED!" << std::endl;
}

void TestSecuritySentinel() {
    std::cout << "[Test] Running Security Sentinel Test..." << std::endl;
    auto& sentinel = payquant::security::GetSecuritySentinel();
    assert(sentinel.IsInWarmupPeriod(5000));
    assert(!sentinel.IsInWarmupPeriod(15000));
    assert(sentinel.VerifyDID("did:pqn:user12345", {0x01, 0x02}));
    std::cout << "[Test] Security Sentinel Test PASSED!" << std::endl;
}

int main() {
    std::cout << "==========================================" << std::endl;
    std::cout << " RUNNING PAYQUANT AUTONOMOUS TEST SUITE" << std::endl;
    std::cout << "==========================================" << std::endl;
    
    TestMLDSA65();
    TestRinHash();
    TestSynergeia();
    TestPoUW();
    TestTreasury();
    TestFMARL();
    TestSecuritySentinel();
    
    std::cout << "==========================================" << std::endl;
    std::cout << " ALL PAYQUANT TESTS PASSED SUCCESSFULLY!" << std::endl;
    std::cout << "==========================================" << std::endl;
    return 0;
}
