BIN=ezchlog
WINEXT=.exe
DST=target
TARGET=$(DST)/$(BIN)
ORIGINS=\
  $(DST)/x86_64-unknown-linux-musl/release/$(BIN) \
  $(DST)/aarch64-unknown-linux-musl/release/$(BIN) \
  $(DST)/arm-unknown-linux-musleabihf/release/$(BIN) \
  $(DST)/aarch64-apple-darwin/release/$(BIN) \
  $(DST)/x86_64-apple-darwin/release/$(BIN) \
  $(DST)/x86_64-pc-windows-gnu/release/$(BIN)$(WINEXT)
TARGETS=\
  $(DST)/$(BIN)-linux-x86_64 \
  $(DST)/$(BIN)-linux-aarch64 \
  $(DST)/$(BIN)-linux-arm \
  $(DST)/$(BIN)-darwin-aarch64 \
  $(DST)/$(BIN)-darwin-x86_64 \
  $(DST)/$(BIN)-windows-x86_64$(WINEXT)
CARGO_ZIG=$(shell which cargo-zigbuild)

.PHONY: help
help:
	@echo "rust targets":
	@echo "  - build                build a debug version"
	@echo "  - release              build a release version"
	@echo "  - list                 list release targets"
	@echo "  - multi-releases       create multiple releases with zig"
	@echo "  - docker-*             run make through cargo-zigbuild docker image"
	@echo "  - clean                clean the $(DST) directory"

.PHONY: clean
clean: $(DST)
	rm -rf $(DST)

$(DST)/debug/$(BIN):
	cargo build

$(DST)/release/$(BIN):
	cargo build --locked --release

$(TARGET): $(DST)/release/$(BIN)
	cp $< $@

.PHONY: build
build: $(DST)/debug/$(BIN)

.PHONY: release
release: $(TARGET)

.PHONY: list
list:
	@for name in $(addsuffix .sha256, $(TARGETS)); do echo $$name; done

.PHONY: docker-%
docker-%:
	docker run --rm -v "$${PWD}:/src:rw" -e "HUID=$$(id -u):$$(id -g)" -w /src messense/cargo-zigbuild bash -c "\
		make $(DST)/$*" \
		chown -R $${HUID:-$$(id -u):$$(id -g)} $(DST)

.PHONY: multi-releases
multi-releases: $(addsuffix .sha256, $(TARGETS))

define generate_rule
$$(addsuffix .sha256, $(1)): $(1)
	sha256sum $$< | sed 's, .*/, ,' > $$@
$(1): $(2)
	cp $$< $$@ # GEN
$(2): $(CARGO_ZIG)
	cargo zigbuild --locked --release --target $$(shell echo $$@ | sed -E 's|$(DST)/||;s|/.+||')
endef
$(foreach index,$(shell seq 1 $(words $(TARGETS))), \
  $(eval $(call generate_rule,$(word $(index),$(TARGETS)),$(word $(index),$(ORIGINS)))) \
)
