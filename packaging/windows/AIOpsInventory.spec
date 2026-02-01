# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Get the directory of this spec file
spec_root = os.path.abspath(os.path.dirname(__file__))
# Calculate project root (2 levels up: packaging/windows -> project_root)
project_root = os.path.abspath(os.path.join(spec_root, '..', '..'))

a = Analysis(
    [os.path.join(project_root, 'src', 'main.py')],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'src', 'database', 'schema.sql'), os.path.join('src', 'database')),
        (os.path.join(project_root, 'resources'), 'resources')
    ],
    hiddenimports=['sqlite3', 'PyQt6', 'pandas', 'reportlab'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AIOpsInventory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AIOpsInventory',
)
