#!/usr/bin/env bash
# Reads the generated code of the wallet's steps on secrets (tests/ct/fixture.ab) with ablac's own checker, tools/ct/check-asm.py: no conditional branch, memory index, division or
# call from a secret, on x86-64, in a release object. A deliberate leak has to be caught too. Needs llvm-objdump and ablac's sources, at the release in use, in ABLAC_DIR.
set -euo pipefail
compiler=${1:-ablac}
ablac_dir=${2:-${ABLAC_DIR:-../ablac}}
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"
mkdir -p build/ct
check="python3 -I $ablac_dir/tools/ct/check-asm.py x86_64 build/ct/fixture.o"
"$compiler" build tests/ct/fixture.ab -o build/ct/fixture.o --emit object --no-cache
fixtures=(wallet_fix_add:@0,@1,@2,@3,@5 wallet_fix_sub:@0,@1,@2,@3 wallet_fix_select:0,@1,@2,@3 wallet_fix_bit:@0 wallet_fix_montgomery:@0,@1,@2,@3)
$check "${fixtures[@]}" > build/ct/x86_64.log 2>&1 || { cat build/ct/x86_64.log >&2; echo "ct: a secret reached a branch or an address" >&2; exit 1; }
if $check wallet_leak_branch:0 > build/ct/leak.log 2>&1 || ! grep -q '^LEAK' build/ct/leak.log; then cat build/ct/leak.log >&2; echo "ct: the checker missed a leak" >&2; exit 1; fi
echo "ok   x86_64: ${#fixtures[@]} fixtures clean in the assembly, a leak caught"
