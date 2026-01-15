# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 【2. 收集 vosk 的所有依赖】
# collect_all 会自动去你的虚拟环境里找 vosk 的 dll 和数据
# 返回三个列表：datas(数据), binaries(二进制dll), hiddenimports(隐式导入)
vosk_datas, vosk_binaries, vosk_hiddenimports = collect_all('vosk')

# 【3. 收集 sounddevice 的依赖 (预防万一)】
# sounddevice 也依赖 portaudio 的 dll，顺手也收集了，防止下一个报错
sd_datas, sd_binaries, sd_hiddenimports = collect_all('sounddevice')

a = Analysis(
    ['main.py'],
    pathex=[],
    # 【4. 把收集到的 binaries 合并进去】
    binaries=vosk_binaries + sd_binaries,
    # 【5. 把收集到的 datas 合并进去，别忘了加上我们自己的 web 文件夹】
    # 格式: ('源路径', '目标路径')
    # 把 web 文件夹打包到内部的 web 目录
    datas=vosk_datas + sd_datas + [('web', 'web'),],
    hiddenimports=vosk_hiddenimports + sd_hiddenimports + ['engineio.async_drivers.threading'],
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
    a.binaries,
    a.datas,
    [],
    name='VoxForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' # 如果你有图标，取消注释这行
)
