"""Convertit pgm/tif/jpg, vff et dossier de .fdf en NIfTI.
Exemples :
  python convert_to_nifti.py Epaule.pgm Epaule.nii.gz
  python convert_to_nifti.py rat111.vff rat111.nii.gz --zooms 1 1 1
  python convert_to_nifti.py Heart/PetitAxe heart.nii.gz        (dossier de .fdf)
"""
import argparse
import os
from utils.io_utils import read_vff, read_2d_image, fdf_folder_to_array, save_nifti


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entree")
    ap.add_argument("sortie")
    ap.add_argument("--zooms", nargs=3, type=float, help="taille des voxels en mm (ecrase la valeur lue)")
    ap.add_argument("--vff-dtype", default=None, help="i2, u1, f4... (defaut : deduit de bits=)")
    ap.add_argument("--vff-endian", choices=["big", "little"], default=None)
    a = ap.parse_args()

    if os.path.isdir(a.entree):
        data, zooms = fdf_folder_to_array(a.entree)
    elif a.entree.lower().endswith(".vff"):
        data, zooms, hdr = read_vff(a.entree, a.vff_dtype, a.vff_endian)
        print("En-tete vff :", hdr)
    else:
        data, zooms = read_2d_image(a.entree), [1.0, 1.0, 1.0]
    if a.zooms:
        zooms = a.zooms
    save_nifti(data, zooms, a.sortie)
    print("Ecrit", a.sortie, "shape", data.shape, "zooms", zooms, "min/max", data.min(), data.max())


if __name__ == "__main__":
    main()
