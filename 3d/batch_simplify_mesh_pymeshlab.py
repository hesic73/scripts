import os
from pathlib import Path
import pymeshlab
import trimesh
import tempfile
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
    - For GLB/GLTF files, converts via OBJ to preserve textures with PyMeshLab
    """
    suffix = in_path.suffix.lower()
    is_glb = suffix in {'.glb', '.gltf'}
    
    # For GLB/GLTF, convert to OBJ, simplify with pymeshlab (which preserves textures), then convert back
    if is_glb:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_dir = Path(tmpdir)
            tmp_obj = tmp_dir / 'mesh.obj'
            
            # Load GLB with trimesh and export as OBJ (this preserves materials and textures)
            scene = trimesh.load(str(in_path), force='scene')
            scene.export(str(tmp_obj), file_type='obj', include_texture=True)
            
            # Load into pymeshlab to check triangle count
            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(str(tmp_obj))
            n_tris = ms.current_mesh().face_number()
            
            if n_tris < min_tris_to_simplify:
                return
            
            tgt = max(min_target_tris, min(int(target_tris), n_tris - 1))
            if tgt >= n_tris:
                return
            
            # Simplify with pymeshlab (preserves texcoords)
            ms.meshing_decimation_quadric_edge_collapse(
                targetfacenum=tgt,
                preservetopology=True,
                preserveboundary=True,
                preservenormal=True,
                optimalplacement=True,
                planarquadric=True,
            )
            
            if smooth_iters > 0:
                ms.apply_coord_taubin_smoothing(stepsmoothnum=smooth_iters)
            
            # Save simplified OBJ
            ms.save_current_mesh(str(tmp_obj))
            
            # Load simplified OBJ and convert back to GLB (this preserves the materials)
            simplified_scene = trimesh.load(str(tmp_obj), force='scene')
            simplified_scene.export(str(in_path))
    else:
        # For non-GLB formats, process directly with pymeshlab
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(str(in_path))
        n_tris = ms.current_mesh().face_number()
        
        if n_tris < min_tris_to_simplify:
            return
        
        tgt = max(min_target_tris, min(int(target_tris), n_tris - 1))
        if tgt >= n_tris:
            return
        
        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=tgt)
        
        if smooth_iters > 0:
            ms.apply_coord_taubin_smoothing(stepsmoothnum=smooth_iters)
        
        ms.save_current_mesh(str(in_path))


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