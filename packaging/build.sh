#!/usr/bin/env bash
# Build the Linux release artifacts: folder build (.tar.gz), AppImage and SHA256SUMS.
#
#   packaging/build.sh            # build on this machine (needs the venv with pyinstaller)
#
# The binary needs a glibc at least as new as the build machine's. For wider
# compatibility build inside an older base image: see packaging/Dockerfile.
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="$(python -c 'import lunar; print(lunar.__version__)')"
ARCH="$(uname -m)"
OUT="release"
echo "==> NoctiCycle $VERSION ($ARCH)"

# 1. Stage the ephemeris so it is bundled (the release works offline from the first run).
mkdir -p lunar/data
if [ ! -f lunar/data/de421.bsp ]; then
  USER_COPY="${XDG_DATA_HOME:-$HOME/.local/share}/nocticycle/de421.bsp"
  if [ -f "$USER_COPY" ]; then cp "$USER_COPY" lunar/data/de421.bsp
  else python - <<'PY'
from skyfield.api import Loader
Loader("lunar/data")("de421.bsp")
PY
  fi
fi

# 2. Folder build.
rm -rf "$OUT/build" "$OUT/nocticycle-$VERSION-linux-$ARCH.tar.gz"
mkdir -p "$OUT"
pyinstaller --noconfirm --clean --distpath "$OUT/build/dist" --workpath "$OUT/build/work" packaging/nocticycle.spec
tar -C "$OUT/build/dist" -czf "$OUT/nocticycle-$VERSION-linux-$ARCH.tar.gz" nocticycle

# 3. AppImage.
APPDIR="$OUT/build/AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/lib"
cp -r "$OUT/build/dist/nocticycle" "$APPDIR/usr/lib/nocticycle"
cp packaging/AppRun "$APPDIR/AppRun"
cp packaging/nocticycle.desktop "$APPDIR/nocticycle.desktop"
cp packaging/nocticycle.png "$APPDIR/nocticycle.png"
TOOL="$OUT/tools/appimagetool-$ARCH.AppImage"
if [ ! -x "$TOOL" ]; then
  mkdir -p "$OUT/tools"
  curl -fL -o "$TOOL" "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$ARCH.AppImage"
  chmod +x "$TOOL"
fi
ARCH="$ARCH" "$TOOL" --appimage-extract-and-run "$APPDIR" "$OUT/NoctiCycle-$VERSION-$ARCH.AppImage"

# 4. Checksums.
( cd "$OUT" && sha256sum "nocticycle-$VERSION-linux-$ARCH.tar.gz" "NoctiCycle-$VERSION-$ARCH.AppImage" > SHA256SUMS )
echo "==> Done:"; ls -lh "$OUT"/*.tar.gz "$OUT"/*.AppImage "$OUT"/SHA256SUMS
