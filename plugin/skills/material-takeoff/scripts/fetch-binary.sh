#!/usr/bin/env bash
# Download the platform-specific `mto` binary from GitHub Releases on first
# run. No license gating in this version — public download, SHA verified
# against the published SHA256SUMS manifest. License gating moves in later.
#
# Usage (called by SKILL.md when the binary is missing):
#   fetch-binary.sh
#
# Output: prints the absolute path to the downloaded binary on stdout.
# Exits non-zero on any failure.

set -euo pipefail

skill_dir="$(cd "$(dirname "$0")/.." && pwd)"
bin_root="$skill_dir/bin"
version="$(cat "$skill_dir/bin-version.txt" | tr -d '[:space:]')"
release_base="https://github.com/blackmirror-media/nio-material-take-off/releases/download/$version"

platform=""
artifact=""
case "$(uname -s)-$(uname -m)" in
  Darwin-arm64)  platform="darwin-arm64"; artifact="mto-darwin-arm64" ;;
  Darwin-x86_64) platform="darwin-x64";   artifact="mto-darwin-x64" ;;
  Linux-x86_64)
    echo "Linux is not a supported platform for this plugin." >&2
    exit 2 ;;
  *)
    echo "Unsupported platform: $(uname -s)-$(uname -m)" >&2
    exit 2 ;;
esac

out_dir="$bin_root/$platform"
out_path="$out_dir/mto"
mkdir -p "$out_dir"

if [[ -x "$out_path" ]]; then
  echo "$out_path"
  exit 0
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "Downloading $artifact ($version)..." >&2
curl -fsSL --retry 3 -o "$tmp/$artifact" "$release_base/$artifact"
curl -fsSL --retry 3 -o "$tmp/SHA256SUMS" "$release_base/SHA256SUMS"

expected="$(grep " $artifact\$" "$tmp/SHA256SUMS" | awk '{print $1}')"
if [[ -z "$expected" ]]; then
  echo "Checksum entry for $artifact not found in SHA256SUMS." >&2
  exit 1
fi
actual="$(shasum -a 256 "$tmp/$artifact" | awk '{print $1}')"
if [[ "$expected" != "$actual" ]]; then
  echo "Checksum mismatch for $artifact." >&2
  echo "  expected: $expected" >&2
  echo "  actual:   $actual" >&2
  exit 1
fi

mv "$tmp/$artifact" "$out_path"
chmod +x "$out_path"

# Strip the macOS quarantine attribute so Gatekeeper doesn't pop up. The
# binary is ad-hoc signed in CI; quarantine removal is what makes that
# signature trusted by the OS on first run.
if [[ "$(uname -s)" == "Darwin" ]]; then
  xattr -d com.apple.quarantine "$out_path" 2>/dev/null || true
fi

echo "$out_path"
