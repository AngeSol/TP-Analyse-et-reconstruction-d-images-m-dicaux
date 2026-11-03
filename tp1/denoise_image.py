"""Debruitage : NLMEANS + filtre anisotrope (Perona-Malik) + filtre median (ou bilateral/gaussien).
  python denoise_image.py flair.nii --slice 80 --out flair_denoise.png
  python denoise_image.py t1.nii --full --save-prefix t1_den     (volume 3D complet, plus lent)
  python denoise_image.py t1.nii --slice 88 --nlm-h 1.5 --aniso-iter 40 --aniso-kappa 3 --median-size 5
"""
import argparse
from utils.io_utils import load_nifti, get_volume, save_nifti
from utils.metrics import auto_masks, estimate_noise_sigma
from utils.denoising import METHODS, run_methods, plot_comparison


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--methods", nargs="+", default=["nlm", "aniso", "median"], choices=list(METHODS))
    ap.add_argument("--slice", type=int, default=None, help="coupe axiale (defaut : milieu)")
    ap.add_argument("--full", action="store_true", help="debruiter tout le volume 3D")
    ap.add_argument("--nlm-h", type=float, default=0.8, help="NLM : h = valeur * sigma estime")
    ap.add_argument("--aniso-iter", type=int, default=15, help="Perona-Malik : nombre d'iterations")
    ap.add_argument("--aniso-kappa", type=float, default=1.5, help="Perona-Malik : kappa = valeur * sigma estime")
    ap.add_argument("--median-size", type=int, default=3, help="median : taille de la fenetre")
    ap.add_argument("--out", default="denoise_result.png")
    ap.add_argument("--save-prefix", default=None, help="sauver les volumes debruites en NIfTI (avec --full)")
    a = ap.parse_args()

    data, zooms, _ = load_nifti(a.image)
    vol = get_volume(data)
    vol = vol / vol.max()                       # normalisation [0,1] : h et kappa comparables
    k = a.slice if a.slice is not None else vol.shape[2] // 2
    work = vol if a.full else vol[:, :, k]
    print(f"sigma de bruit estime (Immerkaer) : {estimate_noise_sigma(work):.5f}")

    _, bg, _ = auto_masks(vol)
    bg_mask = bg if a.full else bg[:, :, k]
    params = {"nlm": {"h_factor": a.nlm_h},
              "aniso": {"n_iter": a.aniso_iter, "kappa_factor": a.aniso_kappa},
              "median": {"size": a.median_size}}
    results = run_methods(work, a.methods, bg_mask, params)

    if a.save_prefix and a.full:
        for name, res in results.items():
            if name != "original":
                save_nifti(res, zooms, f"{a.save_prefix}_{name}.nii.gz")
    plot_comparison({n: (r[:, :, k] if a.full else r) for n, r in results.items()}, a.out)


if __name__ == "__main__":
    main()