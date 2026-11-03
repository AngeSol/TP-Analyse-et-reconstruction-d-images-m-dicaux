"""Projections d'intensite minimale / maximale."""
import matplotlib.pyplot as plt


def projection(vol, axis, mode, start=None, end=None):
    """Min ou max le long d'un axe, sur la plage de coupes [start:end]."""
    sl = [slice(None)] * 3
    sl[axis] = slice(start, end)
    sub = vol[tuple(sl)]
    return sub.max(axis=axis) if mode == "max" else sub.min(axis=axis)


def show_projection(proj, axis, mode, zooms, start, end, out=None):
    remaining = [i for i in range(3) if i != axis]       # (horizontal, vertical)
    aspect = zooms[remaining[1]] / zooms[remaining[0]]
    plt.figure(figsize=(6, 6))
    plt.imshow(proj.T, cmap="gray", origin="lower", aspect=aspect)
    plt.title(f"{'MIP' if mode == 'max' else 'mIP'} axe {axis} ({start}:{end})")
    plt.axis("off")
    if out:
        plt.savefig(out, dpi=150, bbox_inches="tight")
        print("Ecrit", out)
    else:
        plt.show()
