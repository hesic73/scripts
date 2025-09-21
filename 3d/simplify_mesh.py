import open3d as o3d
from fire import Fire


def simplify_mesh(
    in_path: str,
    out_path: str,
    target_tris: int,
    *,
    min_tris_to_simplify: int = 10_000,
    min_target_tris: int = 500,
    smooth_iters: int = 0,
) -> None:
    """
    Simplify a mesh with QEM decimation.

    - Skip if input has fewer triangles than min_tris_to_simplify.
    - Clamp target_tris into [min_target_tris, n_tris - 1].
    - If target >= original, skip.
    - Optionally smooth after decimation.
    """
    mesh = o3d.io.read_triangle_mesh(in_path)
    mesh.compute_vertex_normals()
    n_tris = len(mesh.triangles)

    if n_tris < min_tris_to_simplify:
        o3d.io.write_triangle_mesh(out_path, mesh)
        return

    tgt = max(min_target_tris, min(int(target_tris), n_tris - 1))
    if tgt >= n_tris:
        o3d.io.write_triangle_mesh(out_path, mesh)
        return

    simplified = mesh.simplify_quadric_decimation(
        target_number_of_triangles=tgt)
    if smooth_iters > 0:
        simplified = simplified.filter_smooth_simple(
            number_of_iterations=smooth_iters)

    o3d.io.write_triangle_mesh(out_path, simplified)


def main():
    Fire(simplify_mesh)


if __name__ == "__main__":
    main()
