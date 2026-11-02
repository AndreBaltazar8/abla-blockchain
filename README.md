# abla-blockchain

Blockchain algorithms and formats for [Abla](https://github.com/AndreBaltazar8/ablac): hashes, curves, signature checks, address formats, key derivation, transaction and block formats, and clients that read chains. Mozilla Public License 2.0.

What you get by importing the library, or any subpath outside `wallet`, reads public data only: **it can't sign, spend or hold a private key**. Signatures are only checked, and BIP32 derivation is public only.

[`abla-blockchain/wallet`](docs/signing.md) is the part that signs, asked for by name: BIP-39, private BIP-32, ECDSA with RFC 6979, Ed25519, and building and signing Bitcoin, EVM and Stellar transactions. Read what it says about timing before giving it a key that matters.

```abla
import github("AndreBaltazar8/abla-blockchain")
import "abla/http/tls"

fun main: int {
    // The address of one child of an account key, as a wallet shows it.
    val account = bip32Parse("xpub6Ce9NcJvTk36xtLSrJLZqE7wtgA5deCeYs7rSQtreh4cj6ByPtrg9sD7V2FNFLPnf8heNP3FGkeV9qwfzvZNSd54JoNXVsXFYSYwHsnJxqP").key
    if (account == null) return 1
    val child = bip32Path(account, [0, 0]).key
    if (child != null) println(evmAddressOfKey(child.key))    // 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

    // Who's been paid on Stellar's testnet.
    val horizon = horizonClient(chainEndpoint(httpsClient("horizon-testnet.stellar.org", 443, 16777216, 15000)))
    for (p in horizon.accountPayments("GAHWFLAWPDPDTOCCMIXF4AJI7UFZLGKVEPUEZGKDE33OFH3EGDWO5GZT", "0").records) println("${p.amount.toDecimal()} ${p.asset}")
    0
}
```

The library itself doesn't import TLS. The clients take any `HttpClient`, so a program that only needs hashes or addresses needs no OpenSSL.

## Importing a part of it

`abla-blockchain` is the whole library. A subpath is one folder, or one module of it, and only what it needs gets compiled (ablac 0.2.29 or later):

```abla fragment
import github("AndreBaltazar8/abla-blockchain/evm")
import github("AndreBaltazar8/abla-blockchain/hash/keccak")
```

All of a package's subpaths are one locked revision, so a program can use several. What can be imported is listed under `[exports]` in `abla.toml`, and anything else is refused with `E_PACKAGE_SUBPATH_PRIVATE`:

| Subpath |
|---|
| `uint256` |
| `hash`, `hash/keccak`, `hash/ripemd160` |
| `curve`, `curve/secp256k1`, `curve/modular` |
| `signature`, `signature/ecdsa`, `signature/ed25519` |
| `encoding`, `encoding/base58`, `encoding/bech32` |
| `net`, `net/endpoint` |
| `bitcoin`, `bitcoin/address`, `bitcoin/bip32`, `bitcoin/descriptor`, `bitcoin/esplora`, `bitcoin/esplora-stream`, `bitcoin/raw` |
| `evm`, `evm/address`, `evm/erc20`, `evm/rlp`, `evm/rpc` |
| `stellar`, `stellar/horizon`, `stellar/strkey`, `stellar/xdr` |
| `wallet`, `wallet/secp256k1`, `wallet/ed25519`, `wallet/bip39`, `wallet/bip32`, `wallet/bitcoin`, `wallet/evm`, `wallet/stellar`, `wallet/field`, `wallet/bip39_english` |

## What's in it

| Folder | |
|---|---|
| `src/uint256` | ablac's `uint256` (`abla/uint256`) with checked forms in one shape, the sixteen-limb product the curves use, and `u256FormatUnits` for display |
| `src/hash` | Keccak-256, RIPEMD-160, HASH160. SHA-2 and HMAC come from `abla/crypto` |
| `src/curve` | secp256k1 public-key arithmetic: decompress, multiply and add, on-curve check; arithmetic modulo a prime. Not constant time, as it only takes public values |
| `src/signature` | Checking ECDSA on secp256k1, with strict DER, and Ed25519 |
| `src/encoding` | Base58, Base58Check, Bech32, Bech32m, segwit addresses |
| `src/net` | `ChainEndpoint`, what the clients talk through |
| `src/bitcoin` | BIP32 public derivation and extended keys, addresses (P2WPKH, P2PKH, P2SH-P2WPKH), single-key descriptors with their checksum, BIP-21, raw transactions and block headers, an Esplora client |
| `src/evm` | EIP-55 addresses, JSON-RPC for blocks, logs and receipts, ERC-20 `Transfer` decoding, EIP-681, RLP, raw transactions |
| `src/stellar` | StrKey, a Horizon client for payments, its amounts and times, SEP-7, transaction envelopes in XDR for the common operations |

An amount is an integer in the asset's smallest unit, always: `uint256` for wei, `int` for satoshis. No floats anywhere.

## Testing

`make test` needs only the compiler and git; `tests/subpaths.sh` imports each subpath from a copy of the working tree. Vectors come from the specifications, and client tests replay answers captured from real testnets: see [SOURCES.md](SOURCES.md).

The Esplora address client returns `ok=false`, `complete=false`, partial `transactions` and `nextTxid` when its page budget is exhausted. Resume with `addressTransactions(address, maxPages, nextTxid)`; only the actual end returns `complete=true`.

For large HTTP bodies, `bitcoin/esplora-stream` exposes `EsploraStream(address, receive)`. Feed decoded HTTP body chunks into `feed`, then require `finish()` before committing the callback observations. Script and witness fields are discarded as they arrive; retained scalar tokens are capped at 512 bytes, nesting at 64, transactions at 75 per page and matching outputs at 32768 per transaction (the latter two are configurable). The callback receives original output positions and only outputs to `address`, or all outputs if it is empty. HTTP framing and transport deadlines remain the caller's responsibility.
