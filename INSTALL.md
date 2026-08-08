# Installing PayQuant (PQN)

## Requirements

- C++20 compatible compiler (GCC 11+, Clang 13+, MSVC 2022+)
- CMake 3.22+
- Python 3.10+

## Building with CMake

```bash
cmake -B build
cmake --build build -j$(nproc)
```

## Running Tests

```bash
python test/functional/payquant_tests.py
```