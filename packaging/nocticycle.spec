# PyInstaller spec for the NoctiCycle folder build (run via packaging/build.sh).
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files

root = os.path.abspath(os.path.join(SPECPATH, ".."))

datas = [(os.path.join(root, "lunar", "assets"), "lunar/assets")]
ephemeris = os.path.join(root, "lunar", "data", "de421.bsp")
if not os.path.exists(ephemeris):
    raise SystemExit("lunar/data/de421.bsp is missing: run packaging/build.sh, which stages it.")
datas.append((ephemeris, "lunar/data"))

binaries, hiddenimports = [], []
for pkg in ("timezonefinder", "timezonefinder_data", "h3", "skyfield", "tzdata", "certifi"):
    try:
        d, b, h = collect_all(pkg)
    except Exception:
        continue
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    [os.path.join(root, "nocticycle.py")],
    pathex=[root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "matplotlib", "PIL", "IPython", "pytest"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="nocticycle", console=True)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="nocticycle")
