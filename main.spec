# main.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[('./utils', 'utils'), ('./ui', 'ui')], # Include utils and ui directories
             hiddenimports=['tkinter', 'tkinter.ttk', 'spellchecker'], # Ensure pyspellchecker (spellchecker) and ttk is included
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='TextEditorApp', # Name of the executable
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False, # UPX disabled
          console=False, # False for windowed (GUI) application
          icon=None) # Can specify an icon file here if available
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False, # UPX disabled
               upx_exclude=[],
               name='TextEditorApp')
