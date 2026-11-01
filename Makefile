ABLAC_DIR ?= $(abspath ../ablac)
COMPILER ?= ablac
TESTS := tests/u256_test.ab tests/vectors_test.ab tests/bitcoin_test.ab tests/evm_test.ab tests/stellar_test.ab

.PHONY: test

# No OpenSSL needed: the clients take an HTTP client from whoever uses them.
test:
	! grep -rnE '^import "abla/http/tls|\b(f32|f64)\b' src
	$(COMPILER) test $(TESTS)
