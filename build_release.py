#!/usr/bin/env python3
"""
build_release.py - Build a standalone release of the Pong game

This script:
1. Runs PyInstaller to create a standalone executable
2. Packages it into a zip file ready for GitHub Releases

Usage:
    pip install pyinstaller
    python build_release.py
"""

import subprocess
import sys
import os
import zipfile
import shutil
import platform
from pathlib import Path
from datetime import datetime

def _get_version():
    v = os.environ.get("VERSION", "1.0.0")
    return v.lstrip("v") if v.startswith("v") else v

VERSION = _get_version()

PLATFORM_NAMES = {
    'Darwin': 'macOS',
    'Linux': 'Linux',
    'Windows': 'Windows',
}


def run(cmd, **kwargs):
    print(f"\n→ {' '.join(cmd)}\n")
    result = subprocess.run(cmd, check=True, **kwargs)
    return result


def check_pyinstaller():
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])


def build():
    system = platform.system()
    platform_name = PLATFORM_NAMES.get(system, system)
    arch = platform.machine()  # arm64, x86_64, AMD64, etc.

    print(f"=== Building Pong Game {VERSION} for {platform_name} ({arch}) ===\n")

    check_pyinstaller()

    # clean previous build
    for folder in ['build', 'dist']:
        if Path(folder).exists():
            shutil.rmtree(folder)
            print(f"✓ Cleaned {folder}/")

    # run PyInstaller
    run([
        sys.executable, '-m', 'PyInstaller',
        'pong.spec',
        '--clean',
        '--noconfirm',
    ])

    # figure out what was produced
    dist_path = Path('dist') / 'PongGame'
    app_bundle = Path('dist') / 'PongGame.app'

    if system == 'Darwin' and app_bundle.exists():
        # package the .app bundle into a zip
        archive_name = f"PongGame-{VERSION}-{platform_name}-{arch}.zip"
        archive_path = Path(archive_name)
        print(f"\n→ Creating {archive_name}...")
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in app_bundle.rglob('*'):
                zf.write(file, file.relative_to(Path('dist')))
        print(f"✓ Created: {archive_name}")
        print(f"  Size: {archive_path.stat().st_size / 1024 / 1024:.1f} MB")

    elif system == 'Windows':
        # package the dist folder into a zip
        archive_name = f"PongGame-{VERSION}-{platform_name}-{arch}.zip"
        archive_path = Path(archive_name)
        print(f"\n→ Creating {archive_name}...")
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in dist_path.rglob('*'):
                zf.write(file, file.relative_to(Path('dist')))
        print(f"✓ Created: {archive_name}")
        print(f"  Size: {archive_path.stat().st_size / 1024 / 1024:.1f} MB")

    else:
        # Linux: package as tar.gz (more appropriate for Linux)
        import tarfile
        archive_name = f"PongGame-{VERSION}-{platform_name}-{arch}.tar.gz"
        archive_path = Path(archive_name)
        print(f"\n→ Creating {archive_name}...")
        with tarfile.open(archive_path, 'w:gz') as tf:
            tf.add(dist_path, arcname='PongGame')
        print(f"✓ Created: {archive_name}")
        print(f"  Size: {archive_path.stat().st_size / 1024 / 1024:.1f} MB")

    print(f"\n{'='*50}")
    print(f"Release artifact ready: {archive_name}")
    print(f"Upload this file to your GitHub Release.")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    build()
