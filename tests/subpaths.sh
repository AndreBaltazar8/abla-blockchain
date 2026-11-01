#!/usr/bin/env bash
# `import github("AndreBaltazar8/abla-blockchain/...")` against this working tree: what [exports] lists is what src has, a subpath
# works and brings only itself, and the rest is refused.
set -euo pipefail

compiler=${1:-ablac}
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mkdir -p "$root/build"
work=$(mktemp -d "$root/build/subpaths.XXXXXX")
trap 'rm -rf -- "$work"' EXIT
export ABLA_PACKAGE_CACHE=$work/cache GIT_CONFIG_GLOBAL=$work/gitconfig

fail() { printf 'subpaths: %s\n' "$1" >&2; exit 1; }

# The listing and the folders.
listed=$(sed -n 's/^"[^"]*" = "\(.*\)"$/\1/p' "$root/abla.toml" | sort)
found=$(cd "$root" && find src -name '*.ab' ! -name blockchain.ab | sort)
[[ $listed == "$found" ]] || { diff <(echo "$listed") <(echo "$found") >&2 || true; fail '[exports] and src differ'; }

# github() goes to a copy of what's here, committed.
package=$work/package
mkdir "$package"
cp -r "$root/abla.toml" "$root/src" "$package/"
git -C "$package" init --quiet --initial-branch=main
git -C "$package" add -A
git -C "$package" -c user.name=t -c user.email=t@example.invalid commit --quiet -m c
git config --file "$GIT_CONFIG_GLOBAL" url."$package".insteadOf https://github.com/AndreBaltazar8/abla-blockchain.git

app() { # name, main.ab on stdin
    mkdir -p "$work/$1/src"
    printf 'name = "%s"\nversion = "0.1.0"\nentry = "src/main.ab"\n' "$1" > "$work/$1/abla.toml"
    cat > "$work/$1/src/main.ab"
}
pkg() { echo "github(\"AndreBaltazar8/abla-blockchain/$1\")"; }

# Every export builds on its own and leaves no second copy when two of them share a module.
while read -r path; do
    name=${path//\//-}
    app "one-$name" <<AB
import $(pkg "$path")
fun main: int = 0
AB
    "$compiler" package update --project "$work/one-$name" >/dev/null
    "$compiler" build --project "$work/one-$name" -o "$work/one-$name/out" --fast >/dev/null || fail "$path doesn't build"
done < <(sed -n 's/^"\([^"]*\)" = ".*"$/\1/p' "$root/abla.toml")

# They work together: a folder, a module of another folder, and what both import once.
app together <<AB
import "abla/text"
import $(pkg evm)
import $(pkg hash/keccak)
import $(pkg uint256)
import $(pkg encoding/base58)
fun main: int {
    if (hexEncode(keccak256("")) != "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470") return 1
    if (evmAddressNormal("0x52908400098527886e0f7030069857d2e4169ee7") != "0x52908400098527886E0F7030069857D2E4169EE7") return 2
    if (u256FromInt(7).toDecimal() != "7") return 3
    0
}
AB
"$compiler" package update --project "$work/together" >/dev/null
[[ $(grep -c '^name = ' "$work/together/abla.lock") -eq 1 ]] || fail 'not one lock record'
"$compiler" build --project "$work/together" -o "$work/together/out" --fast || fail "subpaths together don't build"
"$work/together/out" || fail "subpaths together exited $?"

# Only what's imported is compiled: with the clients not parsing, hashes still build.
echo 'this is not abla (' > "$package/src/net/endpoint.ab"
git -C "$package" add -A
git -C "$package" -c user.name=t -c user.email=t@example.invalid commit --quiet -m broken
app narrow <<AB
import $(pkg hash/keccak)
fun main: int = keccak256("").size - 32
AB
"$compiler" package update --project "$work/narrow" >/dev/null
"$compiler" build --project "$work/narrow" -o "$work/narrow/out" --fast || fail 'hash/keccak brought what it does not import'
"$work/narrow/out" || fail "hash/keccak exited $?"

# Refused: no build goes further than this.
refused() { # name, code, path
    app "$1" <<AB
import $(pkg "$3")
fun main: int = 0
AB
    local log=$work/$1.log
    if "$compiler" package update --project "$work/$1" > "$log" 2>&1 && "$compiler" build --project "$work/$1" -o "$work/$1/out" >> "$log" 2>&1; then
        fail "$3 wasn't refused"
    fi
    grep -qF "$2" "$log" || { cat "$log" >&2; fail "$3 didn't report $2"; }
}
refused file E_PACKAGE_SUBPATH_PRIVATE src/hash/keccak
refused extension E_PACKAGE_SUBPATH_PRIVATE hash/keccak.ab
refused entry E_PACKAGE_SUBPATH_PRIVATE blockchain
refused unknown E_PACKAGE_SUBPATH_PRIVATE evm/nothing
refused escape E_PACKAGE_SUBPATH_INVALID ../etc

echo 'subpaths: exports match src, each builds, together one package, only what is imported, the rest refused'
