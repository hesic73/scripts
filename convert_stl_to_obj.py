import os
import trimesh
import numpy as np

from fire import Fire

from loguru import logger


def convert_stl_to_obj(input_dir: str, output_dir: str):
    """
    Convert all STL files in the input directory to OBJ files in the output directory.

    Args:
        input_dir (str): Path to the directory containing STL files.
        output_dir (str): Path to the directory to save converted OBJ files.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # List all files in the input directory
    stl_files = [f for f in os.listdir(input_dir) if f.endswith('.stl')]

    # Transformation matrix to convert STL to OBJ coordinate system
    transform_matrix = np.array([
        [1,  0,  0, 0],  # X remains unchanged
        [0,  0,  1, 0],  # Z becomes Y
        [0, -1,  0, 0],  # Y becomes -Z
        [0,  0,  0, 1],  # Homogeneous coordinates
    ])

    # Process each STL file
    for stl_file in stl_files:
        input_path = os.path.join(input_dir, stl_file)
        output_file = os.path.splitext(stl_file)[0] + '.obj'
        output_path = os.path.join(output_dir, output_file)

        if os.path.exists(output_path):
            logger.warning(
                f"Warning: {output_file} already exists. Skipping conversion.")
            continue

        try:
            # Load the STL file
            mesh = trimesh.load_mesh(input_path)

            # Apply the transformation
            mesh.apply_transform(transform_matrix)

            # Export the mesh to OBJ format
            mesh.export(output_path)
            logger.info(f"Converted: {stl_file} -> {output_file}")
        except Exception as e:
            logger.error(f"Failed to convert {stl_file}: {e}")


if __name__ == "__main__":
    Fire(convert_stl_to_obj)
