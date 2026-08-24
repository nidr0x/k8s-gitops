"""Install the pinned LocalThings integration and its Python dependency."""

from __future__ import annotations

import io
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
from urllib.request import urlopen


# renovate: datasource=git-refs depName=mbillow/localthings
COMMIT = "b5e25d72d3585dcc68f93d668aef404201fe9dbe"
ARCHIVE_URL = f"https://github.com/mbillow/localthings/archive/{COMMIT}.tar.gz"
# renovate: datasource=pypi depName=smartthings-local
DEPENDENCY = "smartthings-local==0.1.10"

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

source_candidates = list(config_dir.glob(f"localthings-{COMMIT}/custom_components/localthings"))
if len(source_candidates) != 1:
    raise RuntimeError("Pinned LocalThings archive did not contain one custom component")

source_dir = source_candidates[0]
shutil.rmtree(target_dir, ignore_errors=True)
shutil.copytree(source_dir, target_dir)
shutil.rmtree(source_dir.parents[1], ignore_errors=True)

subprocess.run(
    [
        os.environ.get("PYTHON", "python"),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-cache-dir",
        "--upgrade",
        "--target",
        str(deps_dir),
        DEPENDENCY,
    ],
    check=True,
)

print(f"Installed LocalThings {COMMIT} and {DEPENDENCY}")
