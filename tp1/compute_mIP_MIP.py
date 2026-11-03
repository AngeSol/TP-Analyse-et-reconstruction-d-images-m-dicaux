"""Projection d'intensite minimale (mIP) ou maximale (MIP) le long d'un axe.
  python compute_mIP_MIP.py t1.nii --axis 2 --mode max --out mip_axial.png
Axes (image en RAS) : 0 = sagittal (X), 1 = coronal (Y), 2 = axial (Z).
--start/--end : ne projeter que sur une plage de coupes (utile pour eviter le crane, par ex.).
"""
import argparse
from utils.io_utils import load_nifti, get_volume
from utils.projections import projection, show_projection


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--axis", type=int, choices=[0, 1, 2], required=True)
    ap.add_argument("--mode", choices=["min", "max"], required=True)
    ap.add_argument("--start", type=int, default=None)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--vol", type=int, default=0, help="volume a utiliser si image 4D")
    ap.add_argument("--out", default=None, help="png de sortie (sinon affichage)")
    a = ap.parse_args()

    data, zooms, _ = load_nifti(a.image)
    proj = projection(get_volume(data, a.vol), a.axis, a.mode, a.start, a.end)
    show_projection(proj, a.axis, a.mode, zooms, a.start, a.end, a.out)


if __name__ == "__main__":
    main()
