"""Affichage des informations et statistiques d'une image."""
import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib
from utils.metrics import (michelson_contrast, rms_contrast, auto_masks,
                           snr_from_masks, local_std_map)

from utils.metrics import (michelson_contrast, rms_contrast, auto_masks,
                           snr_from_masks, local_std_map, estimate_noise_in_mask)


def roi_mask(shape, roi):
    """ROI = x0 x1 y0 y1 z0 z1 (bornes incluses)."""
    m = np.zeros(shape, bool)
    x0, x1, y0, y1, z0, z1 = roi
    m[x0:x1 + 1, y0:y1 + 1, z0:z1 + 1] = True
    return m


def print_header_info(path, raw):
    """Infos lues dans le header du fichier (avant toute reorientation)."""
    print(f"Fichier        : {path}")
    print(f"Taille (shape) : {raw.shape}")
    print(f"Voxel (zooms)  : {tuple(round(float(z), 4) for z in raw.header.get_zooms())}  "
          f"unites : {raw.header.get_xyzt_units()}")
    print(f"Orientation sur disque      : {''.join(nib.aff2axcodes(raw.affine))}")
    canon = nib.as_closest_canonical(raw)
    print(f"Orientation apres chargement (as_closest_canonical) : {''.join(nib.aff2axcodes(canon.affine))}")
    print(f"Type de donnee : {raw.get_data_dtype()}")


def print_contrasts(vol):
    print(f"\nIntensites : min={vol.min():.3f} max={vol.max():.4g} moyenne={vol.mean():.4g}")
    print(f"Contraste de Michelson : {michelson_contrast(vol):.4f}")
    print(f"Contraste RMS (ecart-type) : {rms_contrast(vol):.4g}")
    p1, p99 = np.percentile(vol, [1, 99])   # min/max sensibles aux valeurs aberrantes
    print(f"Michelson robuste (p1/p99) : {(p99 - p1) / (p99 + p1) if p99 + p1 else 0:.4f}")


def compute_and_print_snr(vol, signal_roi=None, noise_roi=None):
    """SNR = moyenne(signal) / ecart-type(bruit). Retourne le masque de bruit utilise."""
    if signal_roi and noise_roi:
        sm, nm = roi_mask(vol.shape, signal_roi), roi_mask(vol.shape, noise_roi)
        how = "ROIs manuelles"
    else:
        sm, nm, t = auto_masks(vol)
        how = f"masques auto (seuil d'Otsu = {t:.4g})"
    snr, s, n = snr_from_masks(vol, sm, nm)
    print(f"\nSNR [{how}] = signal moyen / ecart-type du bruit = {s:.4g} / {n:.4g} = {snr:.2f}")
    print("  (si le fond est du bruit de Rice, sigma_vrai ~ ecart-type_fond / 0.655 : "
          f"SNR corrige ~ {s / (n / 0.655):.2f})")
    return nm


def print_noise_uniformity(vol, noise_mask):
    """Ecart-type local dans le fond de la coupe centrale. Retourne (carte, coupe)."""
    zc = vol.shape[2] // 2
    lstd = local_std_map(vol[:, :, zc])
    bg2d = noise_mask[:, :, zc]
    if bg2d.any():
        print(f"\nUniformite du bruit (coupe {zc}) : ecart-type local dans le fond : "
              f"moyen={lstd[bg2d].mean():.3f}, min={lstd[bg2d].min():.4g}, max={lstd[bg2d].max():.4g}")
    return lstd, zc


def save_stats_plots(vol, lstd, zc, out):
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
    ax[0].hist(vol.ravel(), bins=256, log=True)
    ax[0].set_title("Histogramme (echelle log)")
    ax[1].imshow(vol[:, :, zc].T, cmap="gray", origin="lower")
    ax[1].set_title(f"coupe {zc}")
    im = ax[2].imshow(lstd.T, cmap="viridis", origin="lower")
    ax[2].set_title("ecart-type local (9x9)")
    plt.colorbar(im, ax=ax[2])
    plt.savefig(out, dpi=130, bbox_inches="tight")
    print("Figure ecrite :", out)

def print_snr_estimated_noise(vol):
    """SNR sans ROI : signal = moyenne du tissu (seuil d'Otsu), bruit = estimation d'Immerkaer dans le tissu."""
    sm, _, t = auto_masks(vol)
    zc = vol.shape[2] // 2
    m2d = sm[:, :, zc]
    if not m2d.any():
        print("\nSNR (bruit estime) : masque de tissu vide")
        return
    signal = float(vol[sm].mean())
    sigma = estimate_noise_in_mask(vol[:, :, zc], m2d)
    print(f"\nSNR [bruit estime, Immerkaer, dans le tissu (Otsu = {t:.4g})] = "
          f"signal moyen / sigma = {signal:.4g} / {sigma:.4g} = {signal / sigma:.2f}")
