"""Affiche les infos d'une image : taille, voxels, orientation, contrastes, SNR, uniformite du bruit.
  python show_image_stats.py t1.nii
  python show_image_stats.py t1.nii --signal-roi 100 120 100 120 50 50 --noise-roi 5 25 5 25 50 50 --plots stats_t1.png
  python show_image_stats.py epaule.nii.gz --noise-auto
ROI = x0 x1 y0 y1 z0 z1 (indices de voxels, bornes incluses).
Image 4D : on utilise le volume --vol (defaut 0).
"""
import argparse
import nibabel as nib
from utils.io_utils import load_nifti, get_volume
from utils.stats_report import (print_header_info, print_contrasts, compute_and_print_snr,
                                print_noise_uniformity, save_stats_plots,
                                print_snr_estimated_noise)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--vol", type=int, default=0)
    ap.add_argument("--signal-roi", nargs=6, type=int)
    ap.add_argument("--noise-roi", nargs=6, type=int)
    ap.add_argument("--noise-auto", action="store_true",
                    help="SNR sans ROI : bruit estime dans le tissu (utile si le fond est a zero)")
    ap.add_argument("--plots", default=None, help="png : histogramme + carte de bruit local")
    a = ap.parse_args()

    print_header_info(a.image, nib.load(a.image))
    data, _, _ = load_nifti(a.image, canonical=False)
    vol = get_volume(data, a.vol)
    print_contrasts(vol)

    if a.noise_auto:
        print_snr_estimated_noise(vol)
        return

    noise_mask = compute_and_print_snr(vol, a.signal_roi, a.noise_roi)
    lstd, zc = print_noise_uniformity(vol, noise_mask)
    if a.plots:
        save_stats_plots(vol, lstd, zc, a.plots)


if __name__ == "__main__":
    main()