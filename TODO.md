# TODO

## Rules

- All open work on the library is tracked here. Add new tasks as they come up.
- As soon as a task is completed, take it off this file, in the commit that finishes it.
- Only list what is really open. A task is done when it's verified, not just when it compiles.
- Any bug or error seen goes here right away, with what was seen and how to reproduce it.

## Open

- [ ] Signature verification: ECDSA on secp256k1, Ed25519.
- [ ] Raw formats: Bitcoin transactions and block headers, RLP and Ethereum transactions, Stellar XDR. Today clients read what nodes render as JSON.
- [ ] Taproot: `tr(...)` descriptors, P2TR addresses, which need key tweaking.
- [ ] Muxed Stellar accounts (`M...`).
- [ ] When ablac gets its own `uint256` (its TODO.md), move to it. This type's surface is what's asked of it.
