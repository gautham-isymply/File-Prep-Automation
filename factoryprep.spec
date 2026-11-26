from pathlib import Path

root = Path(SPECPATH)
a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root / "src")],
    datas=[(str(root / "src/factoryprep/profiles"), "factoryprep/profiles")],
    hiddenimports=[],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas,
    name="factoryprep", console=True, upx=False,
)
