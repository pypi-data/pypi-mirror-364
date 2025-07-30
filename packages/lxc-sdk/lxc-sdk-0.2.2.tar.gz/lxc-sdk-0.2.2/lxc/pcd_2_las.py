# from lasWriter import write_las
# from pcdReader import read_pcd
from tqdm import tqdm
import numpy as np
from laspy import LasHeader, LasData
from multiprocessing import Pool, cpu_count
from pathlib import Path
import moore

def write_las(
    xyz: np.ndarray,
    intensity: np.ndarray = None,
    rgb: np.ndarray = None,
    path: str = "output.las",
) -> None:
    """LAS Format Floating-Point Storage Strategy

    Notes:
    - Real: real_x = int_x * scale + offset
    - Stored: int_x = (real_x - offset) / scale
    - Validation: normalized coordinates (xyz) must fall within [0.0, 1.0]

    References:
    - https://www.loc.gov/preservation/digital/formats/fdd/fdd000418.shtml
    - https://github.com/potree/PotreeConverter/blob/develop/Converter/src/chunker_countsort_laszip.cpp
    """
    # Create LAS Header
    header = LasHeader(version="1.4", point_format=2)

    scales = np.array([2**-10, 2**-10, 2**-10])  # 0.001 meter -> 1 mm
    mins = np.min(xyz, axis=0)
    maxs = np.max(xyz, axis=0)

    # Cube millimeter offset
    cube_size = maxs - mins
    mins_scaled = ((mins - mins) / scales).astype(np.int32).astype(np.float32)
    maxs_scaled = ((maxs - mins) / scales).astype(np.int32).astype(np.float32)
    normalized_mins = (mins_scaled * scales + mins - mins) / cube_size
    normalized_maxs = (maxs_scaled * scales + mins - mins) / cube_size
    if np.any(normalized_mins < 0) or np.any(normalized_maxs > 1):
        mins -= 1e-3
        maxs += 1e-3

    header.scales = scales
    header.mins = mins
    header.maxs = maxs

    # Create LAS Data
    las = LasData(header)

    las.x = xyz[:, 0]
    las.y = xyz[:, 1]
    las.z = xyz[:, 2]

    if intensity is not None:
        las.intensity = intensity.astype(np.uint16)

    if rgb is not None:
        r = rgb[:, 0].astype(np.uint16) * 256
        g = rgb[:, 1].astype(np.uint16) * 256
        b = rgb[:, 2].astype(np.uint16) * 256
        las.red, las.green, las.blue = r, g, b

    las.write(path)

def pcd_to_las(pcd_path: str, las_path: str) -> None:
    pc, _ = moore.read_pcd(pcd_path)  
    write_las(pc[:, :3], intensity=pc[:, 3], path=las_path)


def pcd_2_las(data_path, clip_dir_name = '') -> None:

    for clip_dir in tqdm(Path(data_path).iterdir()):
        if clip_dir_name == '' or clip_dir.name == clip_dir_name:
            path = clip_dir
            print(path.with_suffix(".las"))
            pcd_to_las(path, path.with_suffix(".las"))