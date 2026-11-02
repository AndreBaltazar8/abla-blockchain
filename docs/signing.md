# Signing

`abla-blockchain/wallet` is the only part of this library that touches a private key. The library's entry doesn't bring it in, and neither does any other subpath: a program has to ask for it by name.

| Subpath | |
|---|---|
| `wallet/secp256k1` | Public keys from secrets, ECDSA with RFC 6979 nonces and low `s`, DER |
| `wallet/ed25519` | RFC 8032 keys and signatures |
| `wallet/bip39` | Word lists and seeds, in English |
| `wallet/bip32` | Private derivation, `xprv` text, down to the public side |
| `wallet/bitcoin` | Spending from P2WPKH: BIP-143, SIGHASH_ALL, any standard output |
| `wallet/evm` | EIP-1559 transactions, ERC-20 `transfer` data |
| `wallet/stellar` | V1 envelopes: payment, create account, change trust |
| `wallet/field` | Their arithmetic |

No Schnorr or taproot yet (`TODO.md`).

## Timing: what's done, and what isn't

Read ablac's [constant-time.md](https://github.com/AndreBaltazar8/ablac/blob/master/docs/constant-time.md) first. Its limits are these limits: nothing here is promised by a CPU, and it says nothing of speculation, power or fault injection.

**Protected.** In ECDSA and Ed25519, the key and nonce go into `abla/ct`'s secret types as they come out of a string, and the arithmetic is `abla/crypto/bignum`'s Montgomery multiplication, plus addition, subtraction and selection in the same style (`wallet/field`). A multiplication by a secret scalar does the same 256 doublings and 256 complete additions whatever its bits are, and takes each result by mask. There's no table. Inverses are by Fermat's theorem, whose exponent is public. RFC 6979's candidates are compared by reading every byte, and only the answer is public, as a refused candidate is thrown away.

**Read in the assembly.** `tools/test-ct.sh` runs ablac's checker over addition, subtraction, selection, a scalar's bit and Montgomery multiplication, in a release object on x86-64, and it must catch a deliberate leak. That covers these steps and **not** a whole multiplication or signature: those are made of calls, which the checker doesn't follow. So the composition is by review and by the types: the loops above have public bounds, and their only secrets are in those steps. ablac's own test reads Montgomery multiplication on more targets. Nothing has been measured with a clock on real hardware.

**Not protected.**

- A secret's journey as bytes: each key arrives in a `string`, and each byte is an `int` for a moment before it's a secret. Reading a byte is an ordinary load, at a public position. `sha512`, `sha256` and HMAC have no branch or table from their data, by abla/crypto's account, and aren't read by this test.
- `wallet/bip39`: words are looked up by value, so it branches on the secret. So does Base58 in `bip32PrivateSerialize` and `bip32PrivateParse`, and hex and Base64 anywhere. These are for a backup done once, where nobody can measure it, and not for each signature.
- A scalar added in BIP32 goes back into a string through plain integers.
- Memory: working memory is wiped on release, except what stays in strings, which nothing wipes. A garbage collector's copies aren't traced. This is a process that holds a key: treat it as one.
- Threads: a modulus has one scratch area, so two threads mustn't sign at once.

Nothing here has had what libsecp256k1 has had: years of attack. Use it for test wallets and tools, and for a key that holds real value, weigh that first.

## How it's checked

`tests/wallet_test.ab`, with [SOURCES.md](../SOURCES.md) saying where each comes from: BIP-39's, BIP-32's, RFC 6979's and RFC 8032's vectors, BIP-143's signature and EIP-155's, then byte-for-byte with other implementations. Wycheproof's files have no private keys, so they test the verifier, which these signatures must pass. And real testnets accepted transactions signed by it: the ids are in SOURCES.md.
