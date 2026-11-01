# abla-blockchain

Blockchain algorithms and formats for [Abla](https://github.com/AndreBaltazar8/ablac): hashes, curves, address formats, key derivation, and clients that read chains. Mozilla Public License 2.0.

It reads public data only. **Nothing here signs, spends or holds a private key**, and BIP32 derivation is public only.

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

## What's in it

| Folder | |
|---|---|
| `src/uint256` | `U256`: checked by default, wrapping as the EVM does when asked; decimal and hex text, big-endian bytes, division, `u256FormatUnits` for display |
| `src/hash` | Keccak-256, RIPEMD-160, HASH160. SHA-2 and HMAC come from `abla/crypto` |
| `src/curve` | secp256k1 public-key arithmetic: decompress, multiply and add, on-curve check. Not constant time, as it only takes public values |
| `src/encoding` | Base58, Base58Check, Bech32, Bech32m, segwit addresses |
| `src/net` | `ChainEndpoint`, what the clients talk through |
| `src/bitcoin` | BIP32 public derivation and extended keys, addresses (P2WPKH, P2PKH, P2SH-P2WPKH), single-key descriptors with their checksum, BIP-21, an Esplora client |
| `src/evm` | EIP-55 addresses, JSON-RPC for blocks, logs and receipts, ERC-20 `Transfer` decoding, EIP-681 |
| `src/stellar` | StrKey, a Horizon client for payments, its amounts and times, SEP-7 |

An amount is an integer in the asset's smallest unit, always: `U256` for wei, `int` for satoshis. No floats anywhere.

## Testing

`make test` needs only the compiler. Vectors come from the specifications, and client tests replay answers captured from real testnets: see [SOURCES.md](SOURCES.md).
