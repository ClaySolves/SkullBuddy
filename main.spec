# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['python\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('python/DAD_Utils.py', '.'), ('python/gui.py', '.'), ('python/config.py', '.')],
    hidden_imports = [
        "psutil"
        "pyautogui"
        "pytesseract"
        "pillow"
        "pynput"
        "PyQt5"
        "PyQt5-Qt5"
        "PyQt5_sip"
        "pyinstaller"
        "keyboard"
        "pywin32"
        "screeninfo"
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SkullBuddy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon = "img/SkullBuddy.ico"
)
