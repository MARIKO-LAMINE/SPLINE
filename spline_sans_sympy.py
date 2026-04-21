"""
Spline Quadratique SANS SymPy — implémentation numérique pure (NumPy)

Formule (document séance 03/03/26) :
    Si(x) = (1/2)*(z_{i+1}-zi)/(x_{i+1}-xi) * (x-xi)^2 + zi*(x-xi) + yi

La sortie S dépend des z (dérivées aux noeuds), pas des coefficients (a,b,c).
Récurrence : z_{i+1} = 2*(y_{i+1}-yi)/(x_{i+1}-xi) - zi
"""

import numpy as np
import time


def calculer_z(xs: np.ndarray, ys: np.ndarray, z0: float = 0.0) -> np.ndarray:
    """Calcule les dérivées z aux noeuds par récurrence."""
    n = len(xs) - 1  # nombre d'intervalles
    z = np.zeros(n + 1)
    z[0] = z0
    for i in range(n):
        hi = xs[i + 1] - xs[i]
        z[i + 1] = 2.0 * (ys[i + 1] - ys[i]) / hi - z[i]
    return z


def evaluer_spline(x: float, xs: np.ndarray, ys: np.ndarray, z: np.ndarray) -> float:
    """Évalue S(x) en trouvant l'intervalle [xi, xi+1] contenant x."""
    n = len(xs) - 1
    # Trouver l'indice i tel que x ∈ [xi, xi+1]
    i = np.searchsorted(xs, x, side='right') - 1
    i = int(np.clip(i, 0, n - 1))

    hi = xs[i + 1] - xs[i]
    dx = x - xs[i]
    # Si(x) = (z_{i+1}-zi)/(2*hi) * dx^2 + zi*dx + yi
    return (z[i + 1] - z[i]) / (2.0 * hi) * dx**2 + z[i] * dx + ys[i]


def spline_quadratique(xs: np.ndarray, ys: np.ndarray,
                       x_eval: np.ndarray, z0: float = 0.0) -> np.ndarray:
    """
    Point d'entrée principal.

    Paramètres
    ----------
    xs, ys : noeuds d'interpolation (xs triés croissants)
    x_eval : points où évaluer S
    z0     : valeur initiale de la dérivée S'(x0)

    Retourne
    --------
    S_vals : tableau des valeurs S(x) pour chaque x dans x_eval
    """
    z = calculer_z(xs, ys, z0)
    return np.array([evaluer_spline(xi, xs, ys, z) for xi in x_eval])


# ── Démonstration ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Noeuds d'exemple
    xs = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    ys = np.array([0.0, 1.0, 0.0, 1.0, 0.0])

    x_eval = np.linspace(xs[0], xs[-1], 500)

    debut = time.perf_counter()
    S_vals = spline_quadratique(xs, ys, x_eval, z0=0.0)
    fin = time.perf_counter()

    print(f"[SANS SymPy] Durée : {(fin - debut)*1e6:.2f} µs")
    print(f"  Valeurs aux noeuds : {[round(spline_quadratique(xs, ys, np.array([xi]))[0], 8) for xi in xs]}")
