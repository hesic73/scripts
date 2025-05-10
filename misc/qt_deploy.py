import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Set
import fire
from loguru import logger

"""qt_deploy.py – bundle a Qt6 application into a self‑contained directory

Example:
    python path/to/qt_deploy.py \
        --qt_root /home/admin1/Qt/6.6.2/gcc_64 \
        --exe_path ./build/video_speed_changer \
        --deploy_dir ./deploy
"""

###############################################################
# helpers
###############################################################


def _run_ldd(path: Path, extra_lib_dir: Path | None = None) -> List[str]:
    """Return `ldd path` lines; optionally prepend *extra_lib_dir* to LD_LIBRARY_PATH
    so ldd can resolve freshly-copied libs inside *deploy/lib*.
    """
    env = os.environ.copy()
    if extra_lib_dir:
        env["LD_LIBRARY_PATH"] = f"{extra_lib_dir}:{env.get('LD_LIBRARY_PATH', '')}"
    try:
        output = subprocess.check_output(
            ["ldd", str(path)], text=True, env=env)
        return output.splitlines()
    except subprocess.CalledProcessError as exc:
        logger.error(f"ldd failed on {path}: {exc}")
        raise


def _extract_qt_libs(ldd_lines: List[str], qt_root: Path) -> List[Path]:
    """Pick out paths that lie in *qt_root* (Qt & ICU libs)."""
    needed = []
    for line in ldd_lines:
        parts = line.strip().split("=>")
        if len(parts) != 2:
            continue
        lib_path = parts[1].strip().split()[0]
        if lib_path in {"", "not", "found"}:
            continue
        p = Path(lib_path)
        if not p.exists():
            continue
        if qt_root in p.parents or p.name.startswith("libicu") or p.name.startswith("libQt6"):
            needed.append(p)
    return needed


def _copy_unique(libs: List[Path], dest: Path, copied: Set[str]):
    dest.mkdir(parents=True, exist_ok=True)
    for lib in libs:
        if lib.name in copied:
            continue
        shutil.copy2(lib, dest / lib.name)
        logger.info(f"Copied {lib.name}")
        copied.add(lib.name)


def _generate_run_sh(exe_name: str, deploy: Path):
    sh = deploy / "run.sh"
    sh.write_text(
        f"""#!/bin/bash\nDIR=\"$(cd \"$(dirname \"$0\")\" && pwd)\"\nexport LD_LIBRARY_PATH=\"$DIR/lib:$LD_LIBRARY_PATH\"\nexport QT_QPA_PLATFORM_PLUGIN_PATH=\"$DIR/platforms\"\nexec \"$DIR/{exe_name}\" \"$@\"\n"""
    )
    sh.chmod(0o755)
    logger.info("run.sh generated")

###############################################################
# main
###############################################################


def deploy_qt_app(qt_root: str, exe_path: str, deploy_dir: str):
    qt_root = Path(qt_root).resolve()
    exe_path = Path(exe_path).resolve()
    deploy_dir = Path(deploy_dir).resolve()

    logger.info(
        f"Deploying {exe_path.name} using Qt at {qt_root} → {deploy_dir}")

    # Prepare dirs
    (deploy_dir / "lib").mkdir(parents=True, exist_ok=True)
    (deploy_dir / "platforms").mkdir(parents=True, exist_ok=True)

    # Copy executable
    shutil.copy2(exe_path, deploy_dir / exe_path.name)

    copied: Set[str] = set()

    # Copy exe deps
    _copy_unique(_extract_qt_libs(_run_ldd(exe_path), qt_root),
                 deploy_dir / "lib", copied)

    # Analyse plugin in qt_root first
    plugin_src = qt_root / "plugins" / "platforms" / "libqxcb.so"
    if not plugin_src.exists():
        logger.error("libqxcb.so not found in Qt installation")
        return

    _copy_unique(_extract_qt_libs(_run_ldd(plugin_src),
                 qt_root), deploy_dir / "lib", copied)

    # Copy plugin itself
    shutil.copy2(plugin_src, deploy_dir / "platforms" / plugin_src.name)
    logger.info("Qt platform plugin copied")

    # Verify again but allow deploy/lib resolution
    unresolved = [ln for ln in _run_ldd(
        deploy_dir / "platforms" / plugin_src.name, deploy_dir / "lib") if "not found" in ln]
    if unresolved:
        logger.warning("Still unresolved deps for plugin:" +
                       "\n".join(unresolved))
    else:
        logger.info("All plugin deps resolved")

    _generate_run_sh(exe_name=exe_path.name, deploy=deploy_dir)
    logger.success(f"Deployment finished - run {deploy_dir/'run.sh'}")


if __name__ == "__main__":
    fire.Fire(deploy_qt_app)
