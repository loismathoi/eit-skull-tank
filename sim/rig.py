import matplotlib.pyplot as plt
import numpy as np

import pyeit.mesh as mesh


# S/m
SIGMA_SCALP = 0.29
SIGMA_BRAIN = 0.33
SIGMA_SKULL = SIGMA_BRAIN / 60


# normalized to tank inner radius
R_SKULL_OUT = 0.75
R_SKULL_IN = 0.7 

N_EL = 16
H0 = 0.02

mesh_obj = mesh.multi_circle(
    r=1.0,
    background=SIGMA_SCALP / SIGMA_BRAIN,
    n_el=N_EL,
    h0=H0,
    r_layer=[[R_SKULL_IN, R_SKULL_OUT]],
    perm_per_layer=[SIGMA_SKULL / SIGMA_BRAIN],
    ppl=int(np.ceil(2 * np.pi * R_SKULL_OUT / H0)),
)

r_center = np.linalg.norm(mesh_obj.elem_centers[:, :2], axis=1)
mesh_obj.perm[r_center < R_SKULL_IN] = 1.0


if __name__ == "__main__":
    pts = mesh_obj.node
    tri = mesh_obj.element
    el_pos = mesh_obj.el_pos
    mesh_obj.print_stats()

    fig, ax = plt.subplots(figsize=(6, 6))
    im = ax.tripcolor(pts[:, 0], pts[:, 1], tri, mesh_obj.perm, edgecolors="k", linewidth=0.2)
    ax.plot(pts[el_pos, 0], pts[el_pos, 1], "ro")
    fig.colorbar(im, ax=ax, label="relative conductivity")
    ax.axis("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    plt.show()
