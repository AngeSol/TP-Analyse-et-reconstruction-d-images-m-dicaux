"""Construction du viewer interactif (matplotlib + sliders)."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

VIEWS = {"sagittal": 0, "coronal": 1, "axial": 2}   # axe parcouru par le slider (image en RAS)


def extract_slice(vol, view, k):
    """Coupe 2D deja orientee "a l'endroit" (image en RAS)."""
    if view == "sagittal":
        return vol[k, :, :].T          # horizontal = Y (post->ant), vertical = Z
    if view == "coronal":
        return vol[:, k, :].T          # horizontal = X (G->D), vertical = Z
    return vol[:, :, k].T              # axial : horizontal = X, vertical = Y


def aspect_of(view, zooms):
    """aspect = taille du pixel vertical / taille du pixel horizontal (en mm)."""
    zx, zy, zz = zooms
    return {"sagittal": zz / zy, "coronal": zz / zx, "axial": zy / zx}[view]


def launch_viewer(data, zooms, view="all", title=""):
    """data : 3D ou 4D. Si 4D, un slider supplementaire choisit le volume."""
    n_vol = data.shape[3] if data.ndim == 4 else 1
    state = {"vol": 0}

    def current():
        return data[..., state["vol"]] if data.ndim == 4 else data

    v0 = current()
    vmin, vmax = np.percentile(v0, 1), np.percentile(v0, 99.5)
    views = list(VIEWS) if view == "all" else [view]

    fig, axes = plt.subplots(1, len(views), figsize=(5 * len(views), 6.5), squeeze=False)
    axes = axes[0]
    plt.subplots_adjust(bottom=0.25 if n_vol > 1 else 0.15)
    ims, sliders = {}, {}
    for i, name in enumerate(views):
        ax = axes[i]
        n = v0.shape[VIEWS[name]]
        k0 = n // 2
        ims[name] = ax.imshow(extract_slice(v0, name, k0), cmap="gray", origin="lower",
                              aspect=aspect_of(name, zooms), vmin=vmin, vmax=vmax)
        ax.set_title(f"{name} ({k0 + 1}/{n})")
        ax.axis("off")
        sax = fig.add_axes([ax.get_position().x0, 0.08 if n_vol > 1 else 0.04,
                            ax.get_position().width, 0.03])
        sliders[name] = Slider(sax, "", 0, max(n - 1, 1), valinit=k0, valstep=1)

        def update(val, name=name, ax=ax, n=n):
            k = int(val)
            ims[name].set_data(extract_slice(current(), name, k))
            ax.set_title(f"{name} ({k + 1}/{n})")
            fig.canvas.draw_idle()
        sliders[name].on_changed(update)

    if n_vol > 1:
        vax = fig.add_axes([0.25, 0.02, 0.5, 0.03])
        vs = Slider(vax, "volume", 0, n_vol - 1, valinit=0, valstep=1)

        def update_vol(val):
            state["vol"] = int(val)
            for name in views:
                ims[name].set_data(extract_slice(current(), name, int(sliders[name].val)))
            fig.canvas.draw_idle()
        vs.on_changed(update_vol)
        sliders["_vol"] = vs   # garder une reference, sinon le slider est ramasse par le garbage collector

    fig.suptitle(title)
    return fig
