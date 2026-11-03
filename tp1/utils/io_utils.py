"""Chargement des images (NIfTI, PGM/TIF/JPG, VFF, FDF) et conversion en NIfTI."""
import os
import re
import glob
import numpy as np
import nibabel as nib


def load_nifti(path, canonical=True):
    """Charge un NIfTI. Retourne (data float32, zooms 3 valeurs, img_nib).
    canonical=True : reoriente en RAS+ (axe 0 = gauche->droite, 1 = post->ant, 2 = inf->sup)."""
    img = nib.load(path)
    if canonical:
        img = nib.as_closest_canonical(img)
    data = np.asarray(img.get_fdata(dtype=np.float32))
    zooms = list(img.header.get_zooms())[:3]
    while len(zooms) < 3:
        zooms.append(1.0)
    while data.ndim < 3:          # 2D -> (X, Y, 1)
        data = data[..., np.newaxis]
    return data, zooms, img


def reduce_4d(data, mode):
    """4D -> 3D par moyenne ou maximum sur la 4e dimension (3D : inchange)."""
    if data.ndim < 4:
        return data
    return data.mean(axis=3) if mode == "mean" else data.max(axis=3)


def get_volume(data, vol=None, mode="index"):
    """Ramene une image 4D a 3D : un volume precis (index) ou une reduction (mean/max)."""
    if data.ndim < 4:
        return data
    if mode == "mean":
        return data.mean(axis=3)
    if mode == "max":
        return data.max(axis=3)
    return data[..., 0 if vol is None else int(vol)]


# ---------------------------------------------------------------- conversions
def read_vff(path, dtype=None, endian=None):
    """Lit un fichier .vff (Sun raster) : en-tete texte, termine par un saut de page (\\f), puis donnees brutes."""
    raw = open(path, "rb").read()
    end = raw.index(b"\f")
    header_txt = raw[:end].decode("latin-1")
    hdr = {}
    for item in header_txt.replace("\n", "").split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            hdr[k.strip()] = v.strip()
    size = [int(s) for s in hdr["size"].split()]
    bits = int(hdr.get("bits", 8))
    spacing = [float(s) for s in hdr.get("spacing", "1 1 1").split()]
    data_start = end + 1
    if raw[data_start:data_start + 1] == b"\n":
        data_start += 1
    if dtype is None:
        dtype = {8: "u1", 16: "i2", 32: "f4"}[bits]
    byteorder = {"big": ">", "little": "<", None: ">"}[endian]  # .vff : big-endian par defaut
    dt = np.dtype(byteorder + dtype) if np.dtype(dtype).itemsize > 1 else np.dtype(dtype)
    n = int(np.prod(size))
    arr = np.frombuffer(raw, dtype=dt, count=n, offset=data_start)
    arr = arr.reshape(size[::-1]).transpose(2, 1, 0)   # x varie le plus vite -> (X, Y, Z)
    return arr.astype(np.float32), spacing, hdr


def read_fdf(path, endian=None):
    """Lit un .fdf (Varian/Agilent) : en-tete ASCII, donnees float32 a la fin du fichier.
    endian : 'little', 'big' ou None (detection : on garde l'ordre qui donne des nombres valides)."""
    raw = open(path, "rb").read()
    txt = raw[:raw.find(b"\x0c") if b"\x0c" in raw[:5000] else 3000].decode("latin-1")
    m = re.search(r"matrix\s*\[\]\s*=\s*\{([^}]*)\}", txt)
    matrix = [int(float(v)) for v in m.group(1).split(",")]
    bits = int(re.search(r"bits\s*=\s*(\d+)", txt).group(1)) if re.search(r"bits\s*=\s*(\d+)", txt) else 32
    roi = re.search(r"roi\s*\[\]\s*=\s*\{([^}]*)\}", txt)
    roi = [float(v) for v in roi.group(1).split(",")] if roi else None  # cm
    npx = int(np.prod(matrix))
    base = "f4" if bits == 32 else "i2"
    size = np.dtype(base).itemsize
    orders = {"little": ["<"], "big": [">"], None: ["<", ">"]}[endian]
    arr = None
    for o in orders:
        cand = np.frombuffer(raw, dtype=np.dtype(o + base), count=npx, offset=len(raw) - npx * size)
        cand = cand.astype(np.float32)
        if np.isfinite(cand).all() and np.abs(cand).max() < 1e9:
            arr = cand
            break
    if arr is None:
        raise ValueError("valeurs invalides en little et en big endian : " + path)
    arr = arr.reshape(matrix[::-1]).T            # (X, Y) ou (X, Y, Z)
    return arr, matrix, roi


def fdf_folder_to_array(folder, endian=None):
    """Assemble les slice###image###echo###.fdf d'un dossier en (X, Y, Z, echo)."""
    files = sorted(glob.glob(os.path.join(folder, "slice*image*echo*.fdf")))
    if not files:
        raise FileNotFoundError("aucun .fdf dans " + folder)
    pat = re.compile(r"slice(\d+)image(\d+)echo(\d+)")
    items = {}
    for f in files:
        s, i, e = [int(v) for v in pat.search(os.path.basename(f)).groups()]
        items[(s, e)] = f
    slices = sorted({k[0] for k in items})
    echos = sorted({k[1] for k in items})
    first, matrix, roi = read_fdf(items[(slices[0], echos[0])], endian)
    vol = np.zeros(first.shape[:2] + (len(slices), len(echos)), np.float32)
    for si, s in enumerate(slices):
        for ei, e in enumerate(echos):
            vol[:, :, si, ei] = read_fdf(items[(s, e)], endian)[0]
    if roi and len(roi) >= 3:
        zooms = [roi[0] * 10 / matrix[0], roi[1] * 10 / matrix[1], roi[2] * 10]  # cm -> mm
    else:
        zooms = [1.0, 1.0, 1.0]
    return vol, zooms


def read_2d_image(path):
    from PIL import Image
    im = Image.open(path)
    if im.mode not in ("L", "I;16", "I", "F"):
        im = im.convert("L")
    return np.asarray(im, dtype=np.float32).T   # (X, Y) pour rester coherent avec NIfTI


def save_nifti(data, zooms, out_path):
    affine = np.diag(list(zooms[:3]) + [1.0])
    nib.save(nib.Nifti1Image(data.astype(np.float32), affine), out_path)