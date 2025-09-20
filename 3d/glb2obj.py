import os
import shutil
import pathlib
from typing import List

import trimesh
from fire import Fire
from loguru import logger


def _gather_glb_files(input_dir: str) -> List[str]:
    input_dir = os.path.abspath(input_dir)
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"Input dir not found: {input_dir}")
    patterns = ["*.glb", "*.gltf"]
    files = []
    for pat in patterns:
        files.extend(pathlib.Path(input_dir).glob(pat))
    return sorted(str(p) for p in files)


def convert_glb_to_obj(
    input_dir: str,
    output_dir: str,
    overwrite: bool = False,
):
    """
    Convert all GLB/GLTF files in input_dir to per-asset folders:
      <output_dir>/<stem>/<stem>.obj  (+ material.mtl + textures)

    Args:
        input_dir: Directory containing .glb/.gltf files.
        output_dir: Directory to save converted assets.
        overwrite: If True, remove existing per-asset folder before exporting.
    """
    os.makedirs(output_dir, exist_ok=True)
    glb_files = _gather_glb_files(input_dir)

    if not glb_files:
        logger.warning("No .glb/.gltf files found.")
        return

    logger.info(f"Found {len(glb_files)} GLB/GLTF file(s).")

    for in_path in glb_files:
        stem = pathlib.Path(in_path).stem
        out_base_dir = os.path.join(output_dir, stem)
        out_obj_path = os.path.join(out_base_dir, f"{stem}.obj")
        out_mtl_path = os.path.join(
            out_base_dir, "material.mtl")  # trimesh 默认命名

        if os.path.exists(out_base_dir):
            if overwrite:
                shutil.rmtree(out_base_dir)
            else:
                if os.path.exists(out_obj_path):
                    logger.warning(f"Skip (exists): {out_obj_path}")
                    continue

        os.makedirs(out_base_dir, exist_ok=True)

        # 读 Scene 以保留材质/贴图
        scene_or_mesh = trimesh.load(in_path, force="scene")
        scene = (
            trimesh.Scene(scene_or_mesh)
            if isinstance(scene_or_mesh, trimesh.Trimesh)
            else scene_or_mesh
        )

        # 导出到该资产子目录；trimesh 会在同目录写 material.mtl 和纹理
        scene.export(out_obj_path, file_type="obj", include_texture=True)

        if not os.path.exists(out_mtl_path):
            logger.warning(
                f"No .mtl generated (may be untextured): {out_obj_path}")

        logger.info(f"Converted: {in_path} -> {out_obj_path}")

    logger.info("Done.")


if __name__ == "__main__":
    Fire(convert_glb_to_obj)
