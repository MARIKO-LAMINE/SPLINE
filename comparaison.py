"""
Comparaison des durées de calcul : Spline Quadratique avec vs sans SymPy.
Affiche aussi un graphe des deux courbes (doivent coïncider).
"""

import numpy as np
import time
import matplotlib.pyplot as plt

from spline_sans_sympy import spline_quadratique as spline_np
from spline_avec_sympy import spline_quadratique_sympy as spline_sp


def benchmark(xs, ys, x_eval, z0=0.0, repetitions=5):
    """Mesure la durée médiane sur plusieurs répétitions."""

    # --- Sans SymPy ---
    temps_np = []
    for _ in range(repetitions):
        t0 = time.perf_counter()
        S_np = spline_np(np.array(xs, dtype=float), np.array(ys, dtype=float), x_eval, z0)
        temps_np.append(time.perf_counter() - t0)

    # --- Avec SymPy ---
    temps_sp = []
    for _ in range(repetitions):
        t0 = time.perf_counter()
        S_sp, _, _ = spline_sp(xs, ys, x_eval, z0_val=int(z0))
        temps_sp.append(time.perf_counter() - t0)

    return S_np, S_sp, temps_np, temps_sp


def afficher_resultats(xs, ys, x_eval, S_np, S_sp, temps_np, temps_sp):
    med_np = np.median(temps_np) * 1e3   # ms
    med_sp = np.median(temps_sp) * 1e3

    print("=" * 55)
    print("  COMPARAISON SPLINE QUADRATIQUE")
    print("=" * 55)
    print(f"  Points d'évaluation : {len(x_eval)}")
    print(f"  Noeuds              : {len(xs)}")
    print("-" * 55)
    print(f"  Sans SymPy (NumPy)  : {med_np:.4f} ms  (médiane)")
    print(f"  Avec SymPy          : {med_sp:.4f} ms  (médiane)")
    print(f"  Rapport SymPy/NumPy : {med_sp/med_np:.1f}x plus lent")
    print("-" * 55)
    erreur_max = np.max(np.abs(S_np - S_sp))
    print(f"  Erreur max |S_np - S_sp| : {erreur_max:.2e}")
    print("=" * 55)

    # ── Graphes ──────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Courbes d'interpolation
    ax = axes[0]
    ax.plot(x_eval, S_np, 'b-',  lw=2,   label='Sans SymPy (NumPy)')
    ax.plot(x_eval, S_sp, 'r--', lw=1.5, label='Avec SymPy')
    ax.scatter(xs, ys, color='k', zorder=5, label='Noeuds')
    ax.set_title('Spline Quadratique S(x)')
    ax.set_xlabel('x')
    ax.set_ylabel('S(x)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Comparaison des durées (barres)
    ax2 = axes[1]
    labels = ['Sans SymPy\n(NumPy)', 'Avec SymPy']
    valeurs = [med_np, med_sp]
    couleurs = ['steelblue', 'tomato']
    barres = ax2.bar(labels, valeurs, color=couleurs, width=0.4)
    for barre, val in zip(barres, valeurs):
        ax2.text(barre.get_x() + barre.get_width() / 2,
                 barre.get_height() * 1.02,
                 f'{val:.3f} ms', ha='center', va='bottom', fontsize=11)
    ax2.set_title('Durée de calcul (médiane)')
    ax2.set_ylabel('Temps (ms)')
    ax2.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig('comparaison_spline.png', dpi=150)
    print("  Graphe sauvegardé : comparaison_spline.png")
    plt.show()


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Noeuds d'interpolation
    xs = [0, 1, 2, 3, 4]
    ys = [0, 1, 0, 1, 0]

    x_eval = np.linspace(xs[0], xs[-1], 1000)

    S_np, S_sp, temps_np, temps_sp = benchmark(xs, ys, x_eval, z0=0.0, repetitions=7)
    afficher_resultats(xs, ys, x_eval, S_np, S_sp, temps_np, temps_sp)
