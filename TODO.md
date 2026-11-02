# TODO

## Rules

- All open work on the library is tracked here. Add new tasks as they come up.
- As soon as a task is completed, take it off this file, in the commit that finishes it.
- Only list what is really open. A task is done when it's verified, not just when it compiles.
- Any bug or error seen goes here right away, with what was seen and how to reproduce it.

## Open

- [ ] Raw formats still to do: Ethereum block headers, Stellar operations past payment, create account and change trust, and Stellar's older V0 and fee-bump envelopes. Clients still read what nodes render as JSON.
- [ ] Recovering the signer of an Ethereum transaction (`ecrecover`): `EvmRawTransaction` has no `from` yet.
- [ ] Signing: a whole scalar multiplication read in the assembly, and on more targets than x86-64: it's made of calls today, which the checker doesn't follow. Measuring it with a clock on real hardware.
- [ ] Schnorr (BIP-340) and P2TR spends, with taproot.
- [ ] Taproot: `tr(...)` descriptors, P2TR addresses, which need key tweaking.
- [ ] Muxed Stellar accounts (`M...`).
- [ ] When ablac gets its own `uint256` (its TODO.md), move to it. This type's surface is what's asked of it.
