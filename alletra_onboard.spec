# -*- mode: python ; coding: utf-8 -*-
# Build: from the package dir, `pyinstaller --noconfirm --clean alletra_onboard.spec`
# Set ALLETRA_BUNDLE_CHROMIUM=1 to also bundle Chromium (offline build); unset for the slim build
# that downloads Chromium on first run. Prereq for the offline build: `playwright install chromium`.
import os

from PyInstaller.building.datastruct import Tree
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

bundle_chromium = os.environ.get("ALLETRA_BUNDLE_CHROMIUM") == "1"

datas = collect_data_files("playwright")  # the Playwright Node driver + package data (both builds)

# Chromium needs the MSVC runtime (vcruntime140*/msvcp140). Ship those DLLs app-local so the .exe
# runs on a box without the VC++ Redistributable installed. Bundled under vcredist/ for the slim
# build (copied next to the downloaded chrome.exe at runtime); the offline build also bakes them
# straight into chrome-win64 below.
_sys32 = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "System32")
_VC_DLLS = ("vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll")
for _dll in _VC_DLLS:
    _src = os.path.join(_sys32, _dll)
    if os.path.isfile(_src):
        datas.append((_src, "vcredist"))

hiddenimports = collect_submodules("uvicorn") + collect_submodules("alletra_onboard")
hiddenimports += ["anyio", "httptools", "websockets", "watchfiles", "h11"]

a = Analysis(
    ["packaging/app_main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=["packaging/rthook_playwright.py"],
    excludes=["tkinter"],
    noarchive=False,
    optimize=0,
)

# Always bundle the built React UI and the Discovery Tool.
a.datas += Tree("frontend/dist", prefix="frontend/dist")
a.datas += Tree("tools/discovery", prefix="tools/discovery")

# Offline build only: bundle Chromium, minus the headless-shell + ffmpeg we never use (we launch
# the full headed browser). Saves ~270 MB vs. the whole ms-playwright cache.
if bundle_chromium:
    pw_browsers = os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "ms-playwright"
    )
    assert os.path.isdir(pw_browsers), (
        f"Playwright browsers not found at {pw_browsers!r}. Run `playwright install chromium` first."
    )
    for entry in os.listdir(pw_browsers):
        if entry.startswith(("chromium_headless_shell", "ffmpeg")):
            continue  # unused — the cloudinit wizard launches the headed full Chromium
        full = os.path.join(pw_browsers, entry)
        if os.path.isdir(full):
            a.datas += Tree(full, prefix=f"ms-playwright/{entry}")
            # bake the VC++ runtime right next to chrome.exe so the offline build is fully portable
            chrome_win = os.path.join(full, "chrome-win64")
            if entry.startswith("chromium-") and os.path.isdir(chrome_win):
                for _dll in _VC_DLLS:
                    _src = os.path.join(_sys32, _dll)
                    if os.path.isfile(_src):
                        a.datas.append((f"ms-playwright/{entry}/chrome-win64/{_dll}", _src, "DATA"))

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AlletraOnboard",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="AlletraOnboard",
)
