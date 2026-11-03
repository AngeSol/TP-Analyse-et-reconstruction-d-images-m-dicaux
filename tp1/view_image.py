"""Viewer interactif NIfTI (2D/3D/4D).
  python view_image.py t1.nii                   -> 3 vues (axiale, coronale, sagittale)
  python view_image.py t1.nii --view axial      -> une seule vue
  python view_image.py dwi.nii --mode mean      -> 4D : moyenne sur la 4e dimension (sinon slider)
"""
import argparse
import matplotlib.pyplot as plt
from utils.io_utils import load_nifti, reduce_4d
from utils.viewer import launch_viewer


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--view", choices=["axial", "coronal", "sagittal", "all"], default="all")
    ap.add_argument("--mode", choices=["slider", "mean", "max"], default="slider",
                    help="gestion de la 4e dimension")
    ap.add_argument("--no-canonical", action="store_true", help="ne pas reorienter en RAS")
    a = ap.parse_args()

    data, zooms, _ = load_nifti(a.image, canonical=not a.no_canonical)
    if a.mode != "slider":
        data = reduce_4d(data, a.mode)
    title = f"{a.image}  shape={data.shape}  voxel={tuple(round(float(z), 3) for z in zooms)} mm"
    launch_viewer(data, zooms, a.view, title)
    plt.show()


if __name__ == "__main__":
    main()
