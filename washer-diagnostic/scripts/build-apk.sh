#!/usr/bin/env bash
# Dependency-free Android build using the official SDK and the JDK compiler module.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDK="${ANDROID_SDK_ROOT:-$ROOT/.android-sdk}"
TOOLS="$SDK/android-15"
PLATFORM="$SDK/android-35/android.jar"
BUILD="$ROOT/build"
mkdir -p "$BUILD" "$ROOT/dist"
if [[ ! -x "$TOOLS/aapt2" || ! -f "$PLATFORM" ]]; then
  echo "SDK not found. Run scripts/install-sdk.sh or set ANDROID_SDK_ROOT." >&2; exit 1
fi
java -m jdk.compiler/com.sun.tools.javac.Main -version
"$TOOLS/aapt2" compile --dir "$ROOT/app/src/main/res" -o "$BUILD/resources.zip"
"$TOOLS/aapt2" link -o "$BUILD/base.apk" -I "$PLATFORM" --manifest "$ROOT/app/src/main/AndroidManifest.xml" -A "$ROOT/app/src/main/assets" "$BUILD/resources.zip"
mkdir -p "$BUILD/classes" "$BUILD/dex"
java -m jdk.compiler/com.sun.tools.javac.Main -source 8 -target 8 -Xlint:-options -encoding UTF-8 -classpath "$PLATFORM" -d "$BUILD/classes" "$ROOT/app/src/main/java/ru/washeratlas/app/MainActivity.java"
java -m jdk.jartool/sun.tools.jar.Main --create --file "$BUILD/classes.jar" -C "$BUILD/classes" .
java -cp "$TOOLS/lib/d8.jar" com.android.tools.r8.D8 --min-api 26 --lib "$PLATFORM" --output "$BUILD/dex" "$BUILD/classes.jar"
python3 - "$BUILD" <<'PY'
import pathlib,sys,zipfile,shutil
b=pathlib.Path(sys.argv[1]); shutil.copyfile(b/'base.apk',b/'unsigned.apk')
with zipfile.ZipFile(b/'unsigned.apk','a',zipfile.ZIP_DEFLATED) as z:
 for p in (b/'dex').glob('*.dex'): z.write(p,p.name)
PY
"$TOOLS/zipalign" -f -p 4 "$BUILD/unsigned.apk" "$BUILD/aligned.apk"
# Local development signing only. Keep this key out of version control.
if [[ ! -f "$BUILD/debug.keystore" ]]; then
  keytool -genkeypair -keystore "$BUILD/debug.keystore" -storepass android -keypass android -alias androiddebugkey -dname 'CN=Android Debug,O=MasterCode,C=RU' -keyalg RSA -keysize 2048 -validity 10000 -noprompt
fi
java -jar "$TOOLS/lib/apksigner.jar" sign --ks "$BUILD/debug.keystore" --ks-pass pass:android --key-pass pass:android --out "$ROOT/dist/mastercode-0.1.0-debug.apk" "$BUILD/aligned.apk"
java -jar "$TOOLS/lib/apksigner.jar" verify --verbose "$ROOT/dist/mastercode-0.1.0-debug.apk"
"$TOOLS/aapt2" dump badging "$ROOT/dist/mastercode-0.1.0-debug.apk"
