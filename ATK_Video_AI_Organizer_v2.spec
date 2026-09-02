# -*- mode: python ; coding: utf-8 -*-
import os
_HERE = os.path.abspath('.')   # e:\workspace\atk_video_ai_organizer
a = Analysis(
    ['app.py'],
    pathex=[_HERE],
    binaries=[],
    datas=[('config.json', '.'), ('ui/styles', 'ui/styles')],
    hiddenimports=['PySide6.QtSvg','PySide6.QtXml','sqlalchemy.dialects.sqlite','sqlite3','cv2','numpy','PIL','PIL.Image'],
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
    name='ATK_Video_AI_Organizer_v6',
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
    icon=None,
)
