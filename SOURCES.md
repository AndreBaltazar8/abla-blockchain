# Sources

Where each test's expected values come from.

| What | Vectors | Test |
|---|---|---|
| Keccak-256 | Known answers, including Ethereum's `Transfer` topic | `vectors_test` |
| RIPEMD-160 | The authors' paper | `vectors_test` |
| Base58Check | The well-known address example | `vectors_test` |
| Bech32, Bech32m | BIP-173, BIP-350 | `vectors_test` |
| EIP-55 | The EIP's own list | `vectors_test` |
| StrKey, CRC16-XModem | SEP-23's valid and invalid accounts; the CRC catalogue's check value | `vectors_test` |
| secp256k1 | 2G and 7G, n*G | `vectors_test` |
| BIP32 | BIP-32 test vectors 1 and 2, public steps | `vectors_test` |
| BIP-84 addresses | The BIP's published addresses | `vectors_test` |
| EVM addresses | Hardhat's well-known accounts, from its public mnemonic | `vectors_test` |
| Testnet addresses | `tools/vectors.py`, an independent BIP32 in Python, from that public mnemonic. It derives privately, and is test tooling only: nothing like it is in `src` | `bitcoin_test` |
| Descriptor checksum | BIP-380 | `bitcoin_test` |
| ECDSA on secp256k1 | Project Wycheproof, `ecdsa_secp256k1_sha256_test.json`, whole | `signature_test` |
| Ed25519 | RFC 8032 tests 1 and 2; Project Wycheproof, `ed25519_test.json`, whole; real Stellar signatures | `signature_test`, `raw_test` |
| Bitcoin raw formats | The genesis header and coinbase; a real signet segwit transaction and block header, by their hashes | `raw_test` |
| RLP | Examples in Ethereum's documentation | `raw_test` |
| Ethereum transactions | EIP-155's example; real Sepolia EIP-1559 ones, by their hashes | `raw_test` |
| Stellar envelopes | Real testnet envelopes, by their hashes, with their signatures checked | `raw_test` |
| U256 | 2^256-1 and arithmetic identities worked by hand | `u256_test` |

Fixtures in `tests/fixtures` are real public answers, captured on 2026-11-01: a mined signet transaction from mempool.space, a Sepolia block (pruned to the transactions that matter) with a USDC transfer and an ether payment from publicnode, and Stellar testnet payments from Horizon.

`tests/wycheproof` is copied unchanged from [C2SP/wycheproof](https://github.com/C2SP/wycheproof) at commit d17cc89fa5c8f4f4d378b5385ebf75da5d0926c9, `testvectors_v1`, under the Apache License 2.0 of that project. Those test data keep that licence.
