# 🤝 Contributing to PayQuant (PQN)

Thank you for contributing to PayQuant (PQN)! We welcome contributions from developers and researchers across the globe.

---

## 🛠️ Contribution Guidelines

1. **Pull Requests**:
   - Create a feature branch (`git checkout -b feat/my-feature`).
   - Run `python scripts/local_test_suite.py` to verify that all ecosystem tests pass 100%.
   - Open a PR targeting `main`.

2. **NAT Traversal Engine Testing**:
   - Testing the NAT Traversal engine (`contrib/nat_p2p_transport.py`, `contrib/webrtc_p2p_engine.py`, `contrib/irc_dcc_engine.py`) requires multi-network verification.
   - Verify that your changes fall back gracefully across all 5 transport layers:
     1. WebRTC DataChannels (STUN/ICE)
     2. IRC DCC (Direct Client-to-Client)
     3. STUN UDP Hole Punching
     4. Direct TCP Socket
     5. Encrypted IRC Base64 Relay Stream

3. **Code Style**:
   - Python code must follow PEP-8 conventions.
   - Frontend JavaScript must use modern async/await patterns and clean modular scopes.
