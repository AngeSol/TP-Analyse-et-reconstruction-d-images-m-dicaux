"""Methodes de debruitage et comparaison."""
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from skimage.restoration import denoise_nl_means, denoise_bilateral
from utils.metrics import estimate_noise_sigma


def nlmeans(x, patch_size=5, patch_distance=6, h_factor=0.8):
    """Non-local means. h proportionnel au sigma estime du bruit."""
    sigma = estimate_noise_sigma(x)
    return denoise_nl_means(x, patch_size=patch_size, patch_distance=patch_distance,
                            h=h_factor * sigma, sigma=sigma, fast_mode=True)


def perona_malik(x, n_iter=15, kappa_factor=1.5, gamma=0.1):
    """Diffusion anisotrope (Perona-Malik, conductance exponentielle) en 2D/3D, vectorisee.
    kappa = kappa_factor * sigma estime : seuil de gradient au-dessus duquel on protege les contours.
    gamma <= 1/(2*ndim) pour la stabilite."""
    u = x.astype(np.float32).copy()
    kappa = kappa_factor * estimate_noise_sigma(x)
    for _ in range(n_iter):
        total = np.zeros_like(u)
        for ax in range(u.ndim):
            fwd = np.diff(u, axis=ax, append=np.take(u, [-1], axis=ax))
            bwd = np.diff(u, axis=ax, prepend=np.take(u, [0], axis=ax))
            total += np.exp(-(fwd / kappa) ** 2) * fwd - np.exp(-(bwd / kappa) ** 2) * bwd
        u += gamma * total
    return u


def median(x, size=3):
    return ndi.median_filter(x, size=size)


def gaussian(x, sigma=1.0):
    return ndi.gaussian_filter(x, sigma)


def bilateral(x, sigma_color=None, sigma_spatial=2):
    """Bilateral (coupe par coupe si 3D)."""
    if sigma_color is None:
        sigma_color = estimate_noise_sigma(x)
    if x.ndim == 2:
        return denoise_bilateral(x, sigma_color=sigma_color, sigma_spatial=sigma_spatial)
    return np.stack([denoise_bilateral(x[..., k], sigma_color=sigma_color, sigma_spatial=sigma_spatial)
                     for k in range(x.shape[2])], axis=2)


METHODS = {"nlm": nlmeans, "aniso": perona_malik, "median": median,
           "gauss": gaussian, "bilateral": bilateral}


def run_methods(work, methods, bg_mask, params=None):
    """Applique chaque methode a `work` (2D ou 3D). bg_mask : masque de fond de meme forme que `work`.
    params : {nom_methode: {parametre: valeur}} (optionnel).
    Retourne {nom: resultat} et affiche l'ecart-type du fond avant/apres."""
    results = {"original": work}
    for m in methods:
        t0 = time.time()
        res = METHODS[m](work, **(params or {}).get(m, {}))
        results[m] = res
        before, after = _bg_std(work, bg_mask), _bg_std(res, bg_mask)
        print(f"{m:10s} {time.time() - t0:6.1f}s  ecart-type du fond : {before:.5f} -> {after:.5f}")
    return results


def _bg_std(img, bg_mask):
    """Ecart-type des voxels du fond."""
    return float(img[bg_mask].std()) if bg_mask.any() else float("nan")


def plot_comparison(images2d, out):
    """images2d : {nom: image 2D}. Ligne 1 : images, ligne 2 : residus (original - filtre)."""
    ref = images2d["original"]
    fig, ax = plt.subplots(2, len(images2d), figsize=(4 * len(images2d), 8.5), squeeze=False)
    for i, (name, img) in enumerate(images2d.items()):
        ax[0, i].imshow(img.T, cmap="gray", origin="lower", vmin=0, vmax=np.percentile(ref, 99.5))
        ax[0, i].set_title(name)
        ax[0, i].axis("off")
        ax[1, i].imshow((ref - img).T, cmap="gray", origin="lower", vmin=-0.05, vmax=0.05)
        ax[1, i].set_title("residu (orig - " + name + ")")
        ax[1, i].axis("off")
    plt.savefig(out, dpi=130, bbox_inches="tight")
    print("Figure ecrite :", out)