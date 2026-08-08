# Contributing to PayQuant (PQN)

Thank you for your interest in contributing to PayQuant!

## Development Workflow

1. **Fork & Clone**
   ```bash
   git clone https://github.com/timfromhcs/payquant.git
   cd payquant
   ```

2. **Branching Strategy**
   - Create feature branches off `main`: `feature/my-new-feature` or `fix/issue-fix`.

3. **Building & Testing**
   ```bash
   cmake -B build
   cmake --build build
   python test/functional/payquant_tests.py
   python contrib/quantum_sentinel.py
   ```

4. **Pull Requests**
   - Ensure all functional and unit tests pass before opening a Pull Request.
