"""Fonctions de mesure ecrites a la main (pas de bibliotheque pour le contraste)."""
import numpy as np
from scipy import ndimage as ndi


def michelson_contrast(img):
    """C_M = (Imax - Imin) / (Imax + Imin)"""
    imax, imin = float(img.max()), float(img.min())
    return (imax - imin) / (imax + imin) if (imax + imin) != 0 else 0.0


def rms_contrast(img):
    """Contraste RMS = ecart-type des intensites : sqrt( moyenne( (I - Imoy)^2 ) )"""
    return float(np.sqrt(np.mean((img - img.mean()) ** 2)))


def otsu_threshold(img, nbins=256):
    """Seuil d'Otsu (implemente a la main) pour separer fond / tissu."""
    hist, edges = np.histogram(img.ravel(), bins=nbins)
    centers = (edges[:-1] + edges[1:]) / 2
    w0 = np.cumsum(hist)
    w1 = w0[-1] - w0
    m0 = np.cumsum(hist * centers) / np.maximum(w0, 1)
    m1 = (np.sum(hist * centers) - np.cumsum(hist * centers)) / np.maximum(w1, 1)
    between = w0 * w1 * (m0 - m1) ** 2
    return centers[np.argmax(between)]


def auto_masks(vol, erode=3):
    """Masques automatiques : signal (tissu, erode) et bruit (fond, erode)."""
    t = otsu_threshold(vol)
    fg = vol > t
    bg = ~fg
    # image 2D (une seule coupe) : sans cela, l'erosion 3D efface tout le masque
    border = 1 if vol.shape[2] == 1 else 0
    fg = ndi.binary_erosion(fg, iterations=erode, border_value=border)
    bg = ndi.binary_erosion(bg, iterations=erode, border_value=border)
    return fg, bg, t


def snr_from_masks(vol, signal_mask, noise_mask):
    s = vol[signal_mask].mean()
    n = vol[noise_mask].std()
    return float(s / n) if n > 0 else float("inf"), float(s), float(n)


def local_std_map(img2d, size=9):
    """Ecart-type local (fenetre size x size) pour juger l'uniformite du bruit."""
    m = ndi.uniform_filter(img2d, size)
    m2 = ndi.uniform_filter(img2d ** 2, size)
    return np.sqrt(np.maximum(m2 - m ** 2, 0))


def estimate_noise_sigma(x):
    """Estimation rapide de l'ecart-type du bruit (methode de Immerkaer, 1996) :
    on convolue avec un masque qui annule les structures lisses, il reste surtout du bruit.
    Pour un volume 3D : moyenne sur ~10 coupes axiales."""
    mask = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], dtype=np.float64)

    def one(img):
        h, w = img.shape
        conv = ndi.convolve(img.astype(np.float64), mask, mode="reflect")[1:-1, 1:-1]
        return np.sqrt(np.pi / 2) * np.abs(conv).sum() / (6.0 * (h - 2) * (w - 2))

    if x.ndim == 2:
        return float(one(x))
    idx = np.linspace(0, x.shape[2] - 1, min(10, x.shape[2])).astype(int)
    return float(np.mean([one(x[:, :, i]) for i in idx]))

def estimate_noise_in_mask(img2d, mask2d):
    """Ecart-type du bruit (methode de Immerkaer) calcule seulement dans le tissu (mask2d).
    Le masque evite que le fond a zero fasse baisser l'estimation."""
    k = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], dtype=np.float64)
    conv = np.abs(ndi.convolve(img2d.astype(np.float64), k, mode="reflect"))
    return float(np.sqrt(np.pi / 2) * conv[mask2d].mean() / 6.0)