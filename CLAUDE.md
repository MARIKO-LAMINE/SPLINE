# Spline Quadratique — Projet Numérique

## Contexte
Séance 03/03/26 — Interpolation polynomiale par morceaux (Spline Quadratique).

## Objectif
Implémenter la spline quadratique **avec SymPy** et **sans SymPy**, puis comparer les durées de calcul.

## Formulation mathématique (d'après le document)

### Lagrange (rappel)
- Li(x) = ∏(j=0,j≠i)^n (x - xj)/(xi - xj)
- P(x) = Σ yj·Lj(x)

### Spline Quadratique S
S est définie par morceaux sur [x0, xn], avec S et S' continues.

Sur chaque intervalle [xi, xi+1] :
```
Si(x) = ai(x - xi)² + bi(x - xi) + ci
```

**Coefficients en fonction de z (dérivées aux noeuds)** :
- ci = yi  (interpolation: S(xi) = yi)
- bi = zi  (où zi = Si'(xi), dérivée en xi)
- ai = (1/2) · (z_{i+1} - zi) / (x_{i+1} - xi)

**Récurrence sur z** (issue de la continuité de S') :
```
z_{i+1} = 2·(y_{i+1} - yi)/(x_{i+1} - xi) - zi
```

**Formule finale (sortie dépend de z, pas de a,b,c explicitement)** :
```
Si(x) = (1/2)·(z_{i+1} - zi)/(x_{i+1} - xi)·(x - xi)² + zi·(x - xi) + yi
```

## Structure des fichiers
- `spline_sans_sympy.py` — implémentation pure Python/NumPy
- `spline_avec_sympy.py`  — implémentation avec SymPy (calcul symbolique)
- `comparaison.py`        — benchmark et graphes comparatifs

## Hypothèses
1. **Interpolation** : S(xi) = yi, i = 0,...,n → (n+1) équations
2. **S continue** : Si(xi+1) = S_{i+1}(xi+1), i = 0,...,n-2 → (n-1) équations
3. **S' continue** : Si'(xi+1) = S'_{i+1}(xi+1), i = 0,...,n-2 → (n-1) équations

Total : 3n inconnues (ai, bi, ci pour i=0..n-1), avec z0 libre (condition initiale).
