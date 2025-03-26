import subprocess
import os
import fire

from loguru import logger


def find_cuda_dependencies(directory: str = "."):

    cuda_dependent_libraries = []
    for filename in os.listdir(directory):
        if filename.endswith(".so"):  # 只处理共享库文件
            filepath = os.path.join(directory, filename)
            try:
                # 运行 ldd 命令
                result = subprocess.run(
                    ["ldd", filepath], capture_output=True, text=True, check=True)
                if "libcuda.so" in result.stdout:
                    cuda_dependent_libraries.append(filename)
            except subprocess.CalledProcessError as e:
                logger.warning(f"Error running ldd on {filename}: {e}")
            except FileNotFoundError:
                logger.error(f"ldd command not found.")
                return

    if cuda_dependent_libraries:
        print("CUDA dependent libraries found:")
        for lib in cuda_dependent_libraries:
            print(lib)
    else:
        logger.warning("No CUDA dependent libraries found.")


if __name__ == '__main__':
    fire.Fire(find_cuda_dependencies)
