"""
Spline Quadratique AVEC SymPy — implémentation symbolique

Même formule que sans SymPy :
    Si(x) = (1/2)*(z_{i+1}-zi)/(x_{i+1}-xi) * (x-xi)^2 + zi*(x-xi) + yi

SymPy est utilisé pour :
  - Construire les expressions symboliques Si(x)
  - Lambdifier pour l'évaluation numérique
  - (optionnel) vérifier les conditions de continuité symboliquement
"""

import sympy as sp
import numpy as np
import time


def construire_spline_symbolique(xs_vals, ys_vals, z0_val=0):
    """
    Construit la liste des morceaux Si(x) sous forme d'expressions SymPy.

    Retourne
    --------
    x_sym   : symbole SymPy pour x
    morceaux : liste de (Si_expr, xi, xi+1)  — un par intervalle
    z_vals  : valeurs symboliques des dérivées aux noeuds
    """
    x_sym = sp.Symbol('x')
    n = len(xs_vals) - 1

    # --- Calcul des z par récurrence (symbolique exact) ---
    z_vals = [sp.Rational(z0_val)]  # z0 comme rationnel exact si entier
    for i in range(n):
        hi = sp.Rational(xs_vals[i + 1] - xs_vals[i])
        dy = sp.Rational(ys_vals[i + 1] - ys_vals[i])
        zi_plus1 = 2 * dy / hi - z_vals[i]
        z_vals.append(sp.simplify(zi_plus1))

    # --- Construction des morceaux ---
    morceaux = []
    for i in range(n):
        hi = sp.Rational(xs_vals[i + 1] - xs_vals[i])
        dx = x_sym - sp.Rational(xs_vals[i])
        yi = sp.Rational(ys_vals[i])

        Si = (z_vals[i + 1] - z_vals[i]) / (2 * hi) * dx**2 + z_vals[i] * dx + yi
        Si = sp.expand(Si)
        morceaux.append((Si, xs_vals[i], xs_vals[i + 1]))

    return x_sym, morceaux, z_vals


def evaluer_spline_sympy(x_val, x_sym, morceaux):
    """Évalue S(x_val) en sélectionnant le bon morceau."""
    n = len(morceaux)
    for i, (Si, xi, xi1) in enumerate(morceaux):
        if xi <= x_val <= xi1 or i == n - 1:
            return float(Si.subs(x_sym, x_val))
    return float('nan')


def spline_quadratique_sympy(xs_vals, ys_vals, x_eval, z0_val=0):
    """
    Point d'entrée principal (version SymPy).

    Paramètres
    ----------
    xs_vals, ys_vals : listes/arrays de noeuds
    x_eval           : points d'évaluation
    z0_val           : dérivée initiale S'(x0)

    Retourne
    --------
    S_vals : valeurs S(x) pour chaque x dans x_eval
    """
    x_sym, morceaux, z_vals = construire_spline_symbolique(xs_vals, ys_vals, z0_val)

    # Lambdifier chaque morceau pour accélérer l'évaluation
    fonctions = [sp.lambdify(x_sym, Si, 'numpy') for Si, _, _ in morceaux]
    xs_arr = np.array(xs_vals)

    S_vals = np.zeros(len(x_eval))
    for k, xk in enumerate(x_eval):
        i = np.searchsorted(xs_arr, xk, side='right') - 1
        i = int(np.clip(i, 0, len(morceaux) - 1))
        S_vals[k] = fonctions[i](xk)

    return S_vals, morceaux, z_vals


# ── Démonstration ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    xs = [0, 1, 2, 3, 4]
    ys = [0, 1, 0, 1, 0]

    x_eval = np.linspace(xs[0], xs[-1], 500)

    debut = time.perf_counter()
    S_vals, morceaux, z_vals = spline_quadratique_sympy(xs, ys, x_eval, z0_val=0)
    fin = time.perf_counter()

    print(f"[AVEC SymPy] Durée : {(fin - debut)*1e3:.2f} ms")
    print(f"  z (dérivées aux noeuds) : {[str(z) for z in z_vals]}")
    print("  Expressions Si(x) par morceau :")
    x_sym = sp.Symbol('x')
    for i, (Si, xi, xi1) in enumerate(morceaux):
        print(f"    S{i}(x) = {Si}   sur [{xi}, {xi1}]")
