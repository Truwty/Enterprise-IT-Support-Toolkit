# build.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('scripts', 'scripts'),
    ],
    hiddenimports=[
        'customtkinter',
        'psutil',
        'paramiko',
        'matplotlib',
        'networkx',
        'PIL',
        'requests',
        'scapy',
        'fpdf',
        'msal',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EnterpriseITToolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # No console window
    uac_admin=True,          # Request admin on launch
    icon='assets/icons/app_icon.ico',
)
