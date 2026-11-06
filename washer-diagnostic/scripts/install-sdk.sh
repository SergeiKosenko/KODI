#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${ANDROID_SDK_ROOT:-$ROOT/.android-sdk}"
mkdir -p "$SDK" "$ROOT/.cache"
# Archives listed by Google's signed-over-TLS repository metadata. SHA-1 is the
# checksum format published by this SDK repository; TLS verification stays enabled.
fetch() {
  local filename="$1" expected="$2" archive="$ROOT/.cache/$1"
  if [[ ! -f "$archive" ]] || ! echo "$expected  $archive" | sha1sum -c --status; then
    curl --fail --location --retry 2 "https://dl.google.com/android/repository/$filename" -o "$archive"
  fi
  echo "$expected  $archive" | sha1sum -c -
  python3 - "$archive" "$SDK" <<'PY'
import sys,zipfile,os
with zipfile.ZipFile(sys.argv[1]) as z:
 for i in z.infolist():
  p=os.path.realpath(os.path.join(sys.argv[2],i.filename))
  if not p.startswith(os.path.realpath(sys.argv[2])+os.sep): raise ValueError('Unsafe archive member')
 z.extractall(sys.argv[2])
 for i in z.infolist():
  mode=i.external_attr>>16
  if mode: os.chmod(os.path.join(sys.argv[2],i.filename),mode)
PY
}
fetch platform-35_r02.zip 0bb560a90a7a2cbd0dd8348224d518b638fe7949
fetch build-tools_r35_linux.zip 2cfaa0bbb2336e9ec18ed3ecea84fa2e2af607bc
printf 'SDK ready: %s\n' "$SDK"
