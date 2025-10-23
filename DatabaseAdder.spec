# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['MedACRModules.SNR_Module', 'MedACRModules.Geo_Acc_Module', 'MedACRModules.Empty_Module', 'MedACRModules.Ghosting_Module', 'MedACRModules.SlicePos_Module', 'MedACRModules.SliceThickness_Module', 'MedACRModules.Spatial_res_Module', 'MedACRModules.Uniformity_Module']
hiddenimports += collect_submodules('MedACRModules')


a = Analysis(
    ['DatabaseWriter/DatabaseAdder.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='DatabaseAdder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
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
    upx=True,
    upx_exclude=[],
    name='DatabaseAdder',
)
