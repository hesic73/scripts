import os
from pathlib import Path
import open3d as o3d
from fire import Fire

from loguru import logger


def _simplify_one(
    in_path: Path,
    target_tris: int,
    *,
    min_tris_to_simplify: int = 10_000,
    min_target_tris: int = 500,
    smooth_iters: int = 0,
) -> None:
    """
    Simplify one mesh in-place using QEM decimation.
    - Skip if triangles < min_tris_to_simplify
    - Clamp target_tris to [min_target_tris, n_tris-1]
    - Optional smoothing
    """
    mesh = o3d.io.read_triangle_mesh(str(in_path))
    mesh.compute_vertex_normals()
    n_tris = len(mesh.triangles)

    if n_tris < min_tris_to_simplify:
        return

    tgt = max(min_target_tris, min(int(target_tris), n_tris - 1))
    if tgt >= n_tris:
        return

    simplified = mesh.simplify_quadric_decimation(
        target_number_of_triangles=tgt)
    if smooth_iters > 0:
        simplified = simplified.filter_smooth_simple(
            number_of_iterations=smooth_iters)

    o3d.io.write_triangle_mesh(str(in_path), simplified)


def simplify_dir(
    root: str,
    target_tris: int,
    *,
    exts: str = ".glb,.gltf",        # comma-separated; e.g. ".glb,.gltf,.obj"
    recursive: bool = True,
    min_tris_to_simplify: int = 10_000,
    min_target_tris: int = 500,
    smooth_iters: int = 0,
) -> None:
    """
    Simplify all meshes under a directory in-place.
    - Recurses by default
    - Filters by extensions
    """
    root_p = Path(root)
    suffixes = {e.strip().lower() for e in exts.split(",") if e.strip()}
    it = root_p.rglob("*") if recursive else root_p.glob("*")

    for p in it:
        if not p.is_file():
            continue
        if p.suffix.lower() not in suffixes:
            continue
        logger.info(f"Simplifying: {p}")
        _simplify_one(
            p,
            target_tris,
            min_tris_to_simplify=min_tris_to_simplify,
            min_target_tris=min_target_tris,
            smooth_iters=smooth_iters,
        )


if __name__ == "__main__":
    Fire(simplify_dir)
