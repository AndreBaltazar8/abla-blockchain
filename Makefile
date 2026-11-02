ABLAC_DIR ?= $(abspath ../ablac)
COMPILER ?= ablac
TESTS := tests/u256_test.ab tests/vectors_test.ab tests/bitcoin_test.ab tests/evm_test.ab tests/stellar_test.ab tests/signature_test.ab tests/raw_test.ab tests/wallet_test.ab

.PHONY: test test-ct

# No OpenSSL needed: the clients take an HTTP client from whoever uses them.
test:
	! grep -rnE '^import "abla/http/tls|\b(f32|f64)\b' src
	# Asked for by name: nothing else reaches what holds a key.
	! grep -rnE 'import .*wallet' src --include='*.ab' --exclude-dir=wallet
	$(COMPILER) test $(TESTS)
	tests/subpaths.sh $(COMPILER)
# Reads the assembly of what handles secrets. Needs ablac's sources and llvm-objdump.
test-ct:
	tools/test-ct.sh $(COMPILER) $(ABLAC_DIR)
