# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

datas = [('_internal\\ct-scan.ico', '.')]
hiddenimports = ['docopt', 'cv2', 'pydicom.encoders.gdcm', 'pydicom.encoders.pylibjpeg', 'imutils', 'skimage', 'skimage.filters', 'colorlog', 'skimage.segmentation']
datas += collect_data_files('sv_ttk')
hiddenimports += collect_submodules('hazenlib')

numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all('numpy')
datas += numpy_datas
binaries = numpy_binaries
hiddenimports += numpy_hiddenimports


a = Analysis(
    ['PyInstallerGUI\\GUI.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    '_internal\\SplashScreen.jpg',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    [],
    exclude_binaries=True,
    name='ACR QA Analysis',
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
    icon=['_internal\\ct-scan.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    splash.binaries,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ACR QA Analysis',
)
