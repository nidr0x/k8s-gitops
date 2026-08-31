"""Install the pinned LocalThings integration and its Python dependency."""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import tarfile
from pathlib import Path
from urllib.request import urlopen

# renovate: datasource=git-refs depName=mbillow/localthings
COMMIT = "20b479bfd634c647d5be7c0468f543185d9ebcfe"
ARCHIVE_URL = f"https://github.com/mbillow/localthings/archive/{COMMIT}.tar.gz"
# renovate: datasource=pypi depName=smartthings-local
DEPENDENCY = "smartthings-local==0.1.12"

# Home Assistant 2026.8.3 provides these versions.  thinqconnect==1.0.13
# still uses OpenSSL.crypto.X509Req, which was removed in pyOpenSSL 26.3.
PYTHON_DEPENDENCIES = (
    DEPENDENCY,
    "pyOpenSSL==26.2.0",
    "cryptography==48.0.1",
    "cffi==2.0.0",
)

MANAGED_DEPENDENCY_PATTERNS = (
    "OpenSSL",
    "pyopenssl-*.dist-info",
    "cryptography",
    "cryptography-*.dist-info",
    "cryptography.libs",
    "cffi",
    "cffi-*.dist-info",
    "_cffi_backend*.so",
    "pycparser",
    "pycparser-*.dist-info",
    "smartthings_local",
    "smartthings_local-*.dist-info",
)

config_dir = Path(os.environ.get("LOCALTHINGS_CONFIG_DIR", "/config"))
custom_components_dir = config_dir / "custom_components"
deps_dir = config_dir / "deps"
target_dir = custom_components_dir / "localthings"

custom_components_dir.mkdir(parents=True, exist_ok=True)
deps_dir.mkdir(parents=True, exist_ok=True)

with urlopen(ARCHIVE_URL, timeout=60) as response:
    archive_data = response.read()

with tarfile.open(fileobj=io.BytesIO(archive_data), mode="r:gz") as archive:
    archive.extractall(config_dir, filter="data")

source_candidates = list(
    config_dir.glob(f"localthings-{COMMIT}/custom_components/localthings")
)
if len(source_candidates) != 1:
    raise RuntimeError(
        "Pinned LocalThings archive did not contain one custom component"
    )

source_dir = source_candidates[0]
shutil.rmtree(target_dir, ignore_errors=True)
shutil.copytree(source_dir, target_dir)
shutil.rmtree(source_dir.parents[1], ignore_errors=True)

for pattern in MANAGED_DEPENDENCY_PATTERNS:
    for path in deps_dir.glob(pattern):
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()

subprocess.run(
    [
        os.environ.get("PYTHON", "python"),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-cache-dir",
        "--upgrade",
        "--force-reinstall",
        "--target",
        str(deps_dir),
        *PYTHON_DEPENDENCIES,
    ],
    check=True,
)

print(f"Installed LocalThings {COMMIT} and {', '.join(PYTHON_DEPENDENCIES)}")
