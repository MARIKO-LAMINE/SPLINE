"""
Génère 3 fichiers PDF :
  1. documentation.pdf       — théorie mathématique complète
  2. algorithmes.pdf         — pseudo-code + code Python des 2 versions
  3. guide_presentation.pdf  — guide pour présenter le travail
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Preformatted, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = A4
MARGE = 2 * cm
SORTIE = r"C:\Users\HP\OneDrive\Bureau\MARIKO\DOCS_SPLINE"

# ─── Styles communs ───────────────────────────────────────────────────────────
def creer_styles():
    base = getSampleStyleSheet()

    titre_doc = ParagraphStyle('TitreDoc', parent=base['Title'],
                               fontSize=22, textColor=colors.HexColor('#1a237e'),
                               spaceAfter=6, alignment=TA_CENTER)
    sous_titre = ParagraphStyle('SousTitre', parent=base['Normal'],
                                fontSize=13, textColor=colors.HexColor('#3949ab'),
                                spaceAfter=18, alignment=TA_CENTER)
    h1 = ParagraphStyle('H1', parent=base['Heading1'],
                        fontSize=14, textColor=colors.HexColor('#1565c0'),
                        spaceBefore=14, spaceAfter=6,
                        borderPad=4, leading=18)
    h2 = ParagraphStyle('H2', parent=base['Heading2'],
                        fontSize=12, textColor=colors.HexColor('#0277bd'),
                        spaceBefore=10, spaceAfter=4)
    corps = ParagraphStyle('Corps', parent=base['Normal'],
                           fontSize=10.5, leading=16, alignment=TA_JUSTIFY,
                           spaceAfter=6)
    formule = ParagraphStyle('Formule', parent=base['Normal'],
                             fontSize=11, leading=18,
                             leftIndent=40, textColor=colors.HexColor('#212121'),
                             spaceAfter=6, fontName='Courier')
    code_style = ParagraphStyle('Code', parent=base['Code'],
                                fontSize=9, leading=13,
                                backColor=colors.HexColor('#f5f5f5'),
                                leftIndent=10, rightIndent=10,
                                borderColor=colors.HexColor('#cccccc'),
                                borderWidth=0.5, borderPad=6,
                                fontName='Courier')
    legende = ParagraphStyle('Legende', parent=base['Normal'],
                             fontSize=9, textColor=colors.grey,
                             alignment=TA_CENTER, spaceAfter=8)
    return dict(titre_doc=titre_doc, sous_titre=sous_titre,
                h1=h1, h2=h2, corps=corps, formule=formule,
                code_style=code_style, legende=legende, base=base)


def sep(styles):
    return HRFlowable(width='100%', thickness=0.5,
                      color=colors.HexColor('#90caf9'), spaceAfter=8)


def sp(n=8):
    return Spacer(1, n)


# ══════════════════════════════════════════════════════════════════════════════
# PDF 1 — DOCUMENTATION
# ══════════════════════════════════════════════════════════════════════════════

_DOC_NP_Z = '''\
# Etape 1 : calcul des z par recurrence (NumPy)
z = np.zeros(n + 1)
z[0] = z0                          # condition initiale (libre)
for i in range(n):
    hi     = xs[i+1] - xs[i]       # longueur de l'intervalle
    z[i+1] = 2*(ys[i+1]-ys[i])/hi - z[i]   # recurrence
'''

_DOC_NP_EVAL = '''\
# Etape 2 : evaluation de S(x) (NumPy)
i  = searchsorted(xs, x) - 1       # trouver l'intervalle
hi = xs[i+1] - xs[i]
dx = x - xs[i]
S  = (z[i+1]-z[i])/(2*hi)*dx**2 + z[i]*dx + ys[i]
'''

_DOC_SP_Z = '''\
# Etape 1 : calcul des z par recurrence (SymPy)
z = [Rational(z0)]                 # valeur exacte (fraction)
for i in range(n):
    hi = Rational(xs[i+1] - xs[i])
    dy = Rational(ys[i+1] - ys[i])
    z.append(simplify(2*dy/hi - z[-1]))  # exact, sans arrondi
'''

_DOC_SP_BUILD = '''\
# Etape 2 : construction des morceaux symboliques (SymPy)
for i in range(n):
    hi  = Rational(xs[i+1] - xs[i])
    dx  = x_sym - Rational(xs[i])  # (x - xi) symbolique
    yi  = Rational(ys[i])
    Si  = (z[i+1]-z[i])/(2*hi)*dx**2 + z[i]*dx + yi
    Si  = expand(Si)               # developpement algebrique
    # -> expression symbolique : ex.  -2*x**2 + 4*x
'''

_DOC_SP_EVAL = '''\
# Etape 3 : lambdification puis evaluation (SymPy)
fonctions = [lambdify(x_sym, Si, 'numpy') for Si, _,_ in morceaux]
# fonctions[i] est maintenant une fonction Python rapide
valeur = fonctions[i](x)           # evaluation numerique
'''


def gen_documentation():
    doc = SimpleDocTemplate(
        os.path.join(SORTIE, 'documentation.pdf'), pagesize=A4,
        leftMargin=MARGE, rightMargin=MARGE,
        topMargin=MARGE, bottomMargin=MARGE,
        title='Documentation — Spline Quadratique'
    )
    S = creer_styles()
    elems = []

    # ── Couverture ────────────────────────────────────────────────────────────
    elems += [
        sp(55),
        Paragraph("SPLINE QUADRATIQUE", S['titre_doc']),
        Paragraph("Documentation — Deux Implémentations Python", S['sous_titre']),
        sep(S), sp(4),
        Paragraph("Sans SymPy (NumPy)  vs  Avec SymPy", S['legende']),
        sp(20),
    ]

    # ── Introduction ──────────────────────────────────────────────────────────
    elems += [
        Paragraph("Introduction", S['h1']), sep(S),
        Paragraph(
            "Ce document explique et compare deux manières d'implémenter "
            "la spline quadratique en Python, à partir de la formulation "
            "vue en cours (séance 03/03/26).", S['corps']),
        Paragraph(
            "Les deux versions résolvent le même problème : "
            "étant donnés n+1 nœuds (x_i, y_i), construire une fonction S "
            "continue et dérivable, de degré 2 sur chaque intervalle, "
            "qui passe par tous les nœuds.", S['corps']),
        Paragraph(
            "La différence fondamentale est le type de calcul :", S['corps']),
    ]
    data_intro = [
        ['', 'Sans SymPy (NumPy)', 'Avec SymPy'],
        ['Fichier', 'spline_sans_sympy.py', 'spline_avec_sympy.py'],
        ['Type de calcul', 'Numérique (float64)', 'Symbolique exact'],
        ['Résultat z_i', 'Nombre flottant approché', 'Fraction exacte (Rational)'],
        ['Expression S_i(x)', 'Implicite (calculée à la volée)', 'Objet SymPy (affichable en LaTeX)'],
        ['Vitesse', 'Très rapide (< 1 ms)', 'Lente (50–200 ms)'],
    ]
    t = Table(data_intro, colWidths=[4*cm, 6.5*cm, 6.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37474f')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#eceff1')),
        ('FONTNAME',   (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.HexColor('#e3f2fd'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#b0bec5')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 22),
    ]))
    elems += [t, sp(14), PageBreak()]

    # ── PARTIE 1 : SANS SYMPY ─────────────────────────────────────────────────
    elems += [
        Paragraph("PARTIE 1 — Implémentation Sans SymPy (NumPy)", S['titre_doc']),
        Paragraph("Fichier : spline_sans_sympy.py", S['legende']),
        sep(S), sp(6),
    ]

    # 1.1 Principe
    elems += [
        Paragraph("1.1  Principe général", S['h1']), sep(S),
        Paragraph(
            "Cette version travaille exclusivement avec des nombres flottants "
            "(float64). Elle ne construit pas d'expression algébrique : "
            "elle calcule directement la valeur numérique de S(x) à partir "
            "des tableaux xs, ys et des dérivées z.", S['corps']),
        Paragraph(
            "Le code se décompose en deux fonctions indépendantes :", S['corps']),
        Paragraph("  • calculer_z()  —  calcule les z_i par récurrence", S['corps']),
        Paragraph("  • evaluer_spline()  —  évalue S(x) en un point donné", S['corps']),
        sp(8),
    ]

    # 1.2 Calcul des z
    elems += [
        Paragraph("1.2  Calcul des dérivées z par récurrence", S['h1']), sep(S),
        Paragraph(
            "On pose z_i = S'(x_i). La récurrence issue de la continuité "
            "de S' donne :", S['corps']),
        Paragraph(
            "  z_{i+1}  =  2·(y_{i+1} - y_i) / h_i  -  z_i",
            S['formule']),
        Paragraph(
            "Le premier z_0 est libre (condition initiale, ex. z_0 = 0). "
            "Chaque z suivant se déduit du précédent en une seule opération "
            "arithmétique. La boucle s'exécute en O(n).", S['corps']),
        Preformatted(_DOC_NP_Z, S['code_style']),
        Paragraph(
            "Remarque : les z calculés ici sont des flottants. "
            "Pour xs = [0,1,2,3,4], ys = [0,1,0,1,0], z0 = 0, "
            "on obtient z = [0.0, 2.0, -4.0, 6.0, -8.0].", S['corps']),
        sp(10),
    ]

    # 1.3 Evaluation
    elems += [
        Paragraph("1.3  Évaluation de S(x)", S['h1']), sep(S),
        Paragraph(
            "Pour évaluer S en un point x quelconque, on identifie d'abord "
            "l'intervalle [x_i, x_{i+1}] contenant x via np.searchsorted "
            "(recherche binaire, O(log n)), puis on applique directement "
            "la formule du morceau :", S['corps']),
        Paragraph(
            "  S_i(x)  =  [(z_{i+1} - z_i) / (2·h_i)]·(x - x_i)²  "
            "+  z_i·(x - x_i)  +  y_i",
            S['formule']),
        Preformatted(_DOC_NP_EVAL, S['code_style']),
        Paragraph(
            "Les coefficients a_i, b_i, c_i ne sont jamais stockés "
            "séparément : ils sont calculés implicitement à chaque appel. "
            "C'est pourquoi on dit que S dépend des z, pas de (a, b, c).",
            S['corps']),
        sp(10),
    ]

    # 1.4 Avantages / limites
    elems += [
        Paragraph("1.4  Avantages et limites", S['h1']), sep(S),
    ]
    data_np = [
        ['Avantages', 'Limites'],
        ['Très rapide (opérations vectorielles NumPy)',
         'Résultats flottants : arrondi possible'],
        ['Mémoire minimale (pas de stockage symbolique)',
         'Impossible d\'afficher S_i(x) sous forme algébrique'],
        ['Adapté aux grandes données (millions de points)',
         'Pas de vérification symbolique des conditions H2/H3'],
    ]
    t2 = Table(data_np, colWidths=[8.5*cm, 8.5*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e3f2fd'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#90caf9')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 30),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elems += [t2, sp(10), PageBreak()]

    # ── PARTIE 2 : AVEC SYMPY ─────────────────────────────────────────────────
    elems += [
        Paragraph("PARTIE 2 — Implémentation Avec SymPy", S['titre_doc']),
        Paragraph("Fichier : spline_avec_sympy.py", S['legende']),
        sep(S), sp(6),
    ]

    # 2.1 Principe
    elems += [
        Paragraph("2.1  Principe général", S['h1']), sep(S),
        Paragraph(
            "Cette version utilise SymPy, la bibliothèque de calcul formel "
            "de Python. Au lieu de calculer des flottants, elle construit des "
            "expressions algébriques exactes pour chaque morceau S_i(x).", S['corps']),
        Paragraph(
            "Le code se décompose en trois étapes :", S['corps']),
        Paragraph("  1. Calcul des z comme fractions exactes (Rational)", S['corps']),
        Paragraph("  2. Construction des expressions symboliques S_i(x)", S['corps']),
        Paragraph("  3. Lambdification pour l'évaluation numérique rapide", S['corps']),
        sp(8),
    ]

    # 2.2 Calcul z symbolique
    elems += [
        Paragraph("2.2  Calcul des z en mode symbolique", S['h1']), sep(S),
        Paragraph(
            "La même récurrence est appliquée, mais avec sp.Rational() "
            "au lieu de float. Cela garantit un résultat exact sans arrondi. "
            "Par exemple, 1/3 reste 1/3 et non 0.3333333...", S['corps']),
        Preformatted(_DOC_SP_Z, S['code_style']),
        Paragraph(
            "Pour xs = [0,1,2,3,4], ys = [0,1,0,1,0], z0 = 0, "
            "SymPy donne z = [0, 2, -4, 6, -8] comme entiers exacts.",
            S['corps']),
        sp(10),
    ]

    # 2.3 Construction des morceaux
    elems += [
        Paragraph("2.3  Construction des morceaux symboliques", S['h1']), sep(S),
        Paragraph(
            "Pour chaque intervalle [x_i, x_{i+1}], on construit l'expression "
            "symbolique de S_i(x) en substituant les z_i dans la formule. "
            "sp.expand() développe et simplifie l'expression.", S['corps']),
        Preformatted(_DOC_SP_BUILD, S['code_style']),
        Paragraph(
            "Résultat : chaque morceau S_i est un objet SymPy qu'on peut "
            "afficher, dériver, intégrer ou exporter en LaTeX.", S['corps']),
        sp(10),
    ]

    # 2.4 Lambdification
    elems += [
        Paragraph("2.4  Lambdification et évaluation", S['h1']), sep(S),
        Paragraph(
            "Les expressions SymPy sont lentes à évaluer directement. "
            "On utilise sp.lambdify() pour les convertir en fonctions "
            "Python/NumPy rapides. Cette étape est effectuée une seule fois "
            "au moment de la construction.", S['corps']),
        Preformatted(_DOC_SP_EVAL, S['code_style']),
        Paragraph(
            "Après lambdification, l'évaluation est aussi rapide que NumPy. "
            "Le coût de SymPy se situe uniquement dans la phase de "
            "construction (étapes 2.2 et 2.3).", S['corps']),
        sp(10),
    ]

    # 2.5 Avantages / limites
    elems += [
        Paragraph("2.5  Avantages et limites", S['h1']), sep(S),
    ]
    data_sp = [
        ['Avantages', 'Limites'],
        ['Résultats exacts : pas d\'arrondi flottant',
         'Lent à construire (50–200 ms pour 5 nœuds)'],
        ['Affichage algébrique et LaTeX des S_i(x)',
         'Mémoire plus importante (objets symboliques)'],
        ['Vérification symbolique possible (subs, simplify)',
         'Non adapté aux très grands jeux de données'],
        ['Pédagogique : montre les expressions exactes',
         'Complexité du code supérieure'],
    ]
    t3 = Table(data_sp, colWidths=[8.5*cm, 8.5*cm])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6a1b9a')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f3e5f5'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ce93d8')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 30),
    ]))
    elems += [t3, sp(10), PageBreak()]

    # ── PARTIE 3 : COMPARAISON DIRECTE ───────────────────────────────────────
    elems += [
        Paragraph("PARTIE 3 — Comparaison Directe des Deux Versions", S['titre_doc']),
        sep(S), sp(6),
    ]

    # 3.1 Tableau côte à côte
    elems += [
        Paragraph("3.1  Même formule, deux approches", S['h1']), sep(S),
        Paragraph(
            "Les deux implémentations appliquent exactement la même formule "
            "mathématique. Ce qui change, c'est la nature des objets manipulés "
            "et le moment où le calcul numérique est effectué :", S['corps']),
    ]
    data_cmp = [
        ['Étape', 'Sans SymPy', 'Avec SymPy'],
        ['Entrée z_0',
         'float  (ex. 0.0)',
         'sp.Rational  (ex. 0)'],
        ['Récurrence z_i',
         'tableau numpy.float64',
         'liste de sp.Rational exacts'],
        ['Morceau S_i',
         'calculé à la volée à chaque S(x)',
         'expression SymPy stockée'],
        ['Évaluation S(x)',
         'formule directe en float',
         'lambdify puis appel numpy'],
        ['Vérification',
         'comparer S(x_i) == y_i (float)',
         'substituer x=x_i dans S_i (exact)'],
    ]
    t4 = Table(data_cmp, colWidths=[4.5*cm, 6*cm, 6.5*cm])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37474f')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#eceff1')),
        ('FONTNAME',   (0, 1), (0, -1), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (1, 1), (-1, -1), [colors.HexColor('#e8eaf6'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9fa8da')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 26),
    ]))
    elems += [t4, sp(10)]

    # 3.2 Durée
    elems += [
        Paragraph("3.2  Durée de calcul (benchmark)", S['h1']), sep(S),
        Paragraph(
            "La comparaison des durées (médiane sur 7 runs, 1000 points "
            "d'évaluation, 5 nœuds) montre que SymPy est nettement plus "
            "lent, en raison de la construction symbolique :", S['corps']),
    ]
    data_t = [
        ['Implémentation', 'Phase construction', 'Phase évaluation', 'Total typique'],
        ['Sans SymPy', 'O(n)  float', 'O(m·log n)  float', '< 1 ms'],
        ['Avec SymPy', 'O(n)  symbolique + lambdify', 'O(m·log n)  numpy', '50 – 200 ms'],
    ]
    t5 = Table(data_t, colWidths=[4*cm, 5*cm, 4.5*cm, 3.5*cm])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#bf360c')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fbe9e7'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ffab91')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 24),
    ]))
    elems += [t5, sp(10)]

    # 3.3 Quand utiliser lequel
    elems += [
        Paragraph("3.3  Quelle version choisir ?", S['h1']), sep(S),
        Paragraph(
            "Utiliser Sans SymPy (NumPy) quand :", S['h2']),
        Paragraph("  • les données sont volumineuses (n >> 10)", S['corps']),
        Paragraph("  • la vitesse est prioritaire (calcul en temps réel)", S['corps']),
        Paragraph("  • on n'a pas besoin de voir les expressions algébriques", S['corps']),
        Paragraph(
            "Utiliser Avec SymPy quand :", S['h2']),
        Paragraph("  • on veut afficher ou vérifier les expressions S_i(x) exactes", S['corps']),
        Paragraph("  • on travaille en contexte pédagogique ou de démonstration", S['corps']),
        Paragraph("  • on veut exporter les formules en LaTeX", S['corps']),
        sp(12),
        Paragraph(
            "Les deux versions produisent des résultats identiques (erreur "
            "numérique < 1e-12 due aux arrondis flottants). "
            "L'interface Streamlit (app.py) permet de visualiser et comparer "
            "les deux en temps réel.", S['corps']),
    ]

    doc.build(elems)
    print("  [OK] documentation.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# PDF 2 — ALGORITHMES
# ══════════════════════════════════════════════════════════════════════════════
CODE_SANS_SYMPY = '''\
import numpy as np

def calculer_z(xs, ys, z0=0.0):
    """Calcule les derivees z aux noeuds par recurrence."""
    n = len(xs) - 1
    z = np.zeros(n + 1)
    z[0] = z0
    for i in range(n):
        hi = xs[i+1] - xs[i]
        z[i+1] = 2.0 * (ys[i+1] - ys[i]) / hi - z[i]
    return z

def evaluer_spline(x, xs, ys, z):
    """Evalue S(x) sur l\'intervalle [xi, xi+1] contenant x."""
    n = len(xs) - 1
    i = int(np.clip(np.searchsorted(xs, x, side=\'right\') - 1, 0, n-1))
    hi = xs[i+1] - xs[i]
    dx = x - xs[i]
    return (z[i+1] - z[i]) / (2.0 * hi) * dx**2 + z[i] * dx + ys[i]

def spline_quadratique(xs, ys, x_eval, z0=0.0):
    """Point d\'entree : calcule S sur tous les points de x_eval."""
    z = calculer_z(xs, ys, z0)
    return np.array([evaluer_spline(xi, xs, ys, z) for xi in x_eval])
'''

CODE_AVEC_SYMPY = '''\
import sympy as sp
import numpy as np

def construire_spline(xs_vals, ys_vals, z0_val=0):
    """Construit les morceaux Si(x) comme expressions SymPy."""
    x = sp.Symbol(\'x\')
    n = len(xs_vals) - 1

    # Calcul des z par recurrence (exact, symbolique)
    z = [sp.Rational(z0_val)]
    for i in range(n):
        hi = sp.Rational(xs_vals[i+1] - xs_vals[i])
        dy = sp.Rational(ys_vals[i+1] - ys_vals[i])
        z.append(sp.simplify(2 * dy / hi - z[-1]))

    # Construction des morceaux
    morceaux = []
    for i in range(n):
        hi = sp.Rational(xs_vals[i+1] - xs_vals[i])
        dx = x - sp.Rational(xs_vals[i])
        Si = (z[i+1] - z[i]) / (2*hi) * dx**2 + z[i]*dx + sp.Rational(ys_vals[i])
        morceaux.append((sp.expand(Si), xs_vals[i], xs_vals[i+1]))

    return x, morceaux, z

def spline_quadratique_sympy(xs_vals, ys_vals, x_eval, z0_val=0):
    """Evalue S sur x_eval apres construction symbolique."""
    x_sym, morceaux, z_vals = construire_spline(xs_vals, ys_vals, z0_val)
    fonctions = [sp.lambdify(x_sym, Si, \'numpy\') for Si, _, _ in morceaux]
    xs_arr = np.array(xs_vals)

    S_vals = np.zeros(len(x_eval))
    for k, xk in enumerate(x_eval):
        i = int(np.clip(np.searchsorted(xs_arr, xk, side=\'right\') - 1,
                        0, len(morceaux)-1))
        S_vals[k] = fonctions[i](xk)
    return S_vals, morceaux, z_vals
'''

PSEUDO_CODE = '''\
ALGORITHME  SplineQuadratique(xs, ys, x_eval, z0)
─────────────────────────────────────────────────────
ENTRÉES :
  xs[0..n]   : abscisses des noeuds (croissantes)
  ys[0..n]   : ordonnées des noeuds
  x_eval     : points où évaluer S
  z0         : dérivée initiale S'(x0)  [libre]

ÉTAPE 1 — Calcul des z par récurrence
  z[0] ← z0
  POUR i = 0 à n-1 :
      hi ← xs[i+1] - xs[i]
      z[i+1] ← 2*(ys[i+1] - ys[i]) / hi  -  z[i]

ÉTAPE 2 — Évaluation de S(x) pour chaque x dans x_eval
  POUR chaque x dans x_eval :
      Trouver i tel que x ∈ [xs[i], xs[i+1]]
      dx ← x - xs[i]
      hi ← xs[i+1] - xs[i]
      S(x) ← (z[i+1]-z[i])/(2*hi) * dx²  +  z[i]*dx  +  ys[i]

RETOURNER tableau des S(x)
─────────────────────────────────────────────────────
'''


def gen_algorithmes():
    doc = SimpleDocTemplate(
        os.path.join(SORTIE, 'algorithmes.pdf'), pagesize=A4,
        leftMargin=MARGE, rightMargin=MARGE,
        topMargin=MARGE, bottomMargin=MARGE,
        title='Algorithmes — Spline Quadratique'
    )
    S = creer_styles()
    elems = []

    # Couverture
    elems += [
        sp(50),
        Paragraph("ALGORITHMES", S['titre_doc']),
        Paragraph("Spline Quadratique — Avec et Sans SymPy", S['sous_titre']),
        sep(S),
        Paragraph("Interpolation Polynomiale par Morceaux", S['legende']),
        sp(30),
    ]

    # Pseudo-code
    elems += [
        Paragraph("1. Pseudo-code Général", S['h1']), sep(S),
        Paragraph(
            "Les deux implémentations suivent le même algorithme. "
            "La différence réside dans le type de calcul : "
            "numérique (float64) pour NumPy, symbolique (exact) pour SymPy.", S['corps']),
        sp(6),
        Preformatted(PSEUDO_CODE, S['code_style']),
        sp(10),
    ]

    # Complexité
    elems += [
        Paragraph("2. Analyse de Complexité", S['h1']), sep(S),
    ]
    data_c = [
        ['Opération', 'Sans SymPy', 'Avec SymPy'],
        ['Calcul des z (récurrence)', 'O(n)  —  flottants', 'O(n)  —  symbolique exact'],
        ['Construction des morceaux', 'Implicite', 'O(n)  —  sp.expand()'],
        ['Lambdification', '—', 'O(n)  —  une fois'],
        ['Évaluation S(x) en 1 point', 'O(log n) + O(1)', 'O(log n) + O(1)'],
        ['Évaluation sur m points', 'O(m·log n)', 'O(n + m·log n)'],
    ]
    t = Table(data_c, colWidths=[6*cm, 5*cm, 6*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 10),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e3f2fd'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#90caf9')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 22),
    ]))
    elems += [t, sp(10), PageBreak()]

    # Code sans SymPy
    elems += [
        Paragraph("3. Implémentation Sans SymPy (NumPy)", S['h1']), sep(S),
        Paragraph("Fichier : spline_sans_sympy.py", S['legende']),
        Paragraph(
            "Calcul purement numérique. Les z et S(x) sont calculés "
            "directement avec des flottants 64 bits (numpy.float64). "
            "Très rapide, adapté aux grandes données.", S['corps']),
        sp(6),
        Preformatted(CODE_SANS_SYMPY, S['code_style']),
        sp(14),
    ]

    # Code avec SymPy
    elems += [
        Paragraph("4. Implémentation Avec SymPy", S['h1']), sep(S),
        Paragraph("Fichier : spline_avec_sympy.py", S['legende']),
        Paragraph(
            "Calcul symbolique exact. SymPy construit les expressions "
            "algébriques de chaque morceau S_i(x), les simplifie, "
            "puis les lambdifie pour l'évaluation numérique. "
            "Utile pour vérification et pédagogie.", S['corps']),
        sp(6),
        Preformatted(CODE_AVEC_SYMPY, S['code_style']),
        sp(14),
    ]

    # Tableau comparatif
    elems += [
        Paragraph("5. Comparaison Détaillée", S['h1']), sep(S),
    ]
    data_comp = [
        ['Critère', 'Sans SymPy (NumPy)', 'Avec SymPy'],
        ['Type de calcul', 'Numérique (float64)', 'Symbolique exact'],
        ['Résultat z_i', 'Flottant approché', 'Fraction exacte (Rational)'],
        ['Expression S_i(x)', 'Non construite', 'Polynôme SymPy expansé'],
        ['Vitesse typique', '< 1 ms (500 pts)', '50–200 ms (500 pts)'],
        ['Arrondi numérique', 'Possible', 'Aucun (calcul exact)'],
        ['Vérification algebrique', 'Non', 'Oui (subs, simplify)'],
        ['Affichage LaTeX', 'Non', 'Oui (sp.latex(Si))'],
        ['Usage recommandé', 'Production, calcul intensif', 'Enseignement, vérification'],
    ]
    t2 = Table(data_comp, colWidths=[5.5*cm, 5.5*cm, 6*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a148c')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f3e5f5'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ce93d8')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 22),
    ]))
    elems.append(t2)

    doc.build(elems)
    print("  [OK] algorithmes.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# PDF 3 — GUIDE DE PRÉSENTATION
# ══════════════════════════════════════════════════════════════════════════════
def gen_guide_presentation():
    doc = SimpleDocTemplate(
        os.path.join(SORTIE, 'guide_presentation.pdf'), pagesize=A4,
        leftMargin=MARGE, rightMargin=MARGE,
        topMargin=MARGE, bottomMargin=MARGE,
        title='Guide de Présentation — Spline Quadratique'
    )
    S = creer_styles()
    elems = []

    # Couverture
    elems += [
        sp(50),
        Paragraph("GUIDE DE PRÉSENTATION", S['titre_doc']),
        Paragraph("Spline Quadratique — Avec vs Sans SymPy", S['sous_titre']),
        sep(S),
        Paragraph("À l'usage du présentateur", S['legende']),
        sp(30),
    ]

    # Plan
    elems += [
        Paragraph("Plan de la Présentation", S['h1']), sep(S),
    ]
    plan = [
        ['Partie', 'Contenu', 'Durée estimée'],
        ['1', 'Contexte et motivation (Lagrange → Spline)', '3 min'],
        ['2', 'Définition et hypothèses de la spline quadratique', '4 min'],
        ['3', 'Formulation en z — récurrence', '4 min'],
        ['4', 'Démonstration du code (sans SymPy)', '5 min'],
        ['5', 'Démonstration du code (avec SymPy)', '4 min'],
        ['6', 'Comparaison des durées — résultats', '3 min'],
        ['7', 'Conclusion et questions', '2 min'],
    ]
    t = Table(plan, colWidths=[2*cm, 11*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e65100')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fff3e0'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ffcc80')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 22),
    ]))
    elems += [t, sp(14)]

    # Partie 1
    elems += [
        Paragraph("Partie 1 — Contexte et Motivation", S['h1']), sep(S),
        Paragraph("Message clé à transmettre :", S['h2']),
        Paragraph(
            "Le polynôme de Lagrange global oscille (Runge) pour de nombreux nœuds. "
            "Les splines résolvent ce problème en travaillant par morceaux avec "
            "des polynômes de faible degré.", S['corps']),
        Paragraph("Points à aborder :", S['h2']),
        Paragraph("  • Rappeler la formule L_i(x) et la propriété δ_ik", S['corps']),
        Paragraph("  • Montrer un exemple d'oscillation de Runge (si possible)", S['corps']),
        Paragraph("  • Annoncer l'approche par morceaux (spline)", S['corps']),
        sp(10),
    ]

    # Partie 2
    elems += [
        Paragraph("Partie 2 — Définition et Hypothèses", S['h1']), sep(S),
        Paragraph("Message clé à transmettre :", S['h2']),
        Paragraph(
            "La spline quadratique est définie par 3 conditions : interpolation, "
            "continuité de S, continuité de S'. Ces 3 conditions donnent 3n-1 "
            "équations pour 3n inconnues → 1 degré de liberté z_0.", S['corps']),
        Paragraph("Points à aborder :", S['h2']),
        Paragraph("  • Écrire S_i(x) = a_i·x² + b_i·x + c_i sur chaque intervalle", S['corps']),
        Paragraph("  • Présenter le tableau des 3 hypothèses avec les nombres d'équations", S['corps']),
        Paragraph("  • Insister sur le fait que z_0 est libre (condition initiale)", S['corps']),
        sp(10),
    ]

    # Partie 3
    elems += [
        Paragraph("Partie 3 — Formulation en z et Récurrence", S['h1']), sep(S),
        Paragraph("Message clé à transmettre :", S['h2']),
        Paragraph(
            "On n'a pas besoin de calculer a_i, b_i, c_i séparément. "
            "Tout se ramène aux z_i (dérivées aux nœuds), calculés par une "
            "simple récurrence en O(n).", S['corps']),
        Paragraph("Formules à écrire au tableau :", S['h2']),
        Paragraph("  z_{i+1} = 2·(y_{i+1} - y_i) / h_i  -  z_i", S['formule']),
        Paragraph(
            "  S_i(x) = [(z_{i+1}-z_i)/(2·h_i)]·(x-x_i)²  +  z_i·(x-x_i)  +  y_i",
            S['formule']),
        Paragraph(
            "Faire un exemple numérique rapide avec 3 nœuds pour montrer "
            "le calcul des z à la main.", S['corps']),
        sp(10),
    ]

    # Partie 4 & 5
    elems += [
        Paragraph("Parties 4 & 5 — Démonstration du Code", S['h1']), sep(S),
        Paragraph("Sans SymPy :", S['h2']),
        Paragraph("  • Ouvrir spline_sans_sympy.py", S['corps']),
        Paragraph("  • Montrer calculer_z() : boucle simple, récurrence directe", S['corps']),
        Paragraph("  • Montrer evaluer_spline() : searchsorted pour trouver i", S['corps']),
        Paragraph("  • Exécuter et afficher les valeurs aux nœuds (doivent = y_i)", S['corps']),
        sp(6),
        Paragraph("Avec SymPy :", S['h2']),
        Paragraph("  • Ouvrir spline_avec_sympy.py", S['corps']),
        Paragraph("  • Montrer les z_vals : fractions exactes (ex. 2, -4, 6...)", S['corps']),
        Paragraph("  • Montrer les expressions Si(x) en LaTeX via sp.latex()", S['corps']),
        Paragraph("  • Vérifier que les deux codes donnent les mêmes résultats", S['corps']),
        sp(10),
    ]

    # Partie 6
    elems += [
        Paragraph("Partie 6 — Comparaison des Durées", S['h1']), sep(S),
        Paragraph("Message clé à transmettre :", S['h2']),
        Paragraph(
            "SymPy est significativement plus lent car il effectue du calcul "
            "symbolique (construction + simplification des expressions). "
            "NumPy travaille directement sur des flottants.", S['corps']),
        Paragraph("Résultats typiques (500 points d'évaluation) :", S['h2']),
    ]
    data_res = [
        ['Implémentation', 'Durée typique', 'Remarque'],
        ['Sans SymPy (NumPy)', '< 1 ms', 'Calcul flottant direct'],
        ['Avec SymPy', '50 – 200 ms', 'Construction + lambdification'],
        ['Rapport', '50× – 200×', 'SymPy plus lent'],
    ]
    t2 = Table(data_res, colWidths=[5.5*cm, 4.5*cm, 7*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b5e20')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e8f5e9'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a5d6a7')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 22),
    ]))
    elems += [t2, sp(10)]

    # Partie 7
    elems += [
        Paragraph("Partie 7 — Conclusion", S['h1']), sep(S),
        Paragraph("Points de conclusion à retenir :", S['h2']),
        Paragraph(
            "  1. La spline quadratique résout le problème d'oscillation de Lagrange "
            "en travaillant par morceaux.", S['corps']),
        Paragraph(
            "  2. La formulation en z simplifie la construction : "
            "une récurrence O(n) suffit.", S['corps']),
        Paragraph(
            "  3. NumPy = vitesse ; SymPy = exactitude et vérification symbolique.", S['corps']),
        sp(10),
        Paragraph("Questions fréquentes à anticiper :", S['h2']),
        Paragraph(
            "  Q : Pourquoi z_0 est-il libre ?  →  Parce qu'on a 3n-1 équations "
            "pour 3n inconnues.", S['corps']),
        Paragraph(
            "  Q : Que se passe-t-il si z_0 change ?  →  Toute la spline change "
            "(les z_i suivent par récurrence).", S['corps']),
        Paragraph(
            "  Q : Peut-on avoir une spline cubique ?  →  Oui, en ajoutant la "
            "continuité de S'' (condition supplémentaire).", S['corps']),
    ]

    doc.build(elems)
    print("  [OK] guide_presentation.pdf")


# ══════════════════════════════════════════════════════════════════════════════
# PDF 4 — GUIDE D'UTILISATION DE L'INTERFACE STREAMLIT
# ══════════════════════════════════════════════════════════════════════════════
def gen_guide_interface():
    doc = SimpleDocTemplate(
        os.path.join(SORTIE, 'guide_interface.pdf'), pagesize=A4,
        leftMargin=MARGE, rightMargin=MARGE,
        topMargin=MARGE, bottomMargin=MARGE,
        title="Guide d'utilisation — Interface Streamlit"
    )
    S = creer_styles()
    elems = []

    # ── Couverture ────────────────────────────────────────────────────────────
    elems += [
        sp(55),
        Paragraph("GUIDE D'UTILISATION", S['titre_doc']),
        Paragraph("Interface Streamlit — Spline Quadratique", S['sous_titre']),
        sep(S), sp(4),
        Paragraph("Comment manipuler l'interface pas à pas", S['legende']),
        sp(20),
    ]

    # ── Lancement ─────────────────────────────────────────────────────────────
    elems += [
        Paragraph("1. Lancer l'interface", S['h1']), sep(S),
        Paragraph(
            "Ouvrir un terminal dans le dossier du projet, puis exécuter :",
            S['corps']),
        Preformatted(
            "python -m streamlit run app.py",
            S['code_style']),
        Paragraph(
            "L'interface s'ouvre automatiquement dans le navigateur à "
            "l'adresse http://localhost:8501. "
            "Si ce n'est pas le cas, copier-coller cette adresse manuellement.",
            S['corps']),
        sp(10),
    ]

    # ── Vue générale ──────────────────────────────────────────────────────────
    elems += [
        Paragraph("2. Vue générale de l'interface", S['h1']), sep(S),
        Paragraph(
            "L'interface est divisée en deux zones principales :", S['corps']),
    ]
    data_zones = [
        ['Zone', 'Emplacement', 'Rôle'],
        ['Barre latérale (Sidebar)', 'Gauche de l\'écran', 'Saisir les paramètres du problème'],
        ['Zone principale', 'Centre / droite', 'Afficher les résultats et graphiques'],
    ]
    t = Table(data_zones, colWidths=[5*cm, 5*cm, 7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37474f')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#eceff1'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#b0bec5')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 24),
    ]))
    elems += [t, sp(12)]

    # ── Sidebar ───────────────────────────────────────────────────────────────
    elems += [
        Paragraph("3. Barre latérale — Saisie des paramètres", S['h1']), sep(S),
    ]

    # 3.1 Nœuds x
    elems += [
        Paragraph("3.1  Champ « x₀, x₁, ..., xₙ »", S['h2']),
        Paragraph(
            "Entrer les abscisses des nœuds séparées par des virgules. "
            "Ces valeurs doivent être triées en ordre croissant.",
            S['corps']),
        Preformatted(
            "Exemple :  0, 1, 2, 3, 4\n"
            "Exemple :  0, 0.5, 1.5, 3, 5, 7",
            S['code_style']),
        Paragraph(
            "Attention : si les valeurs ne sont pas croissantes, "
            "l'interface affichera un message d'erreur en rouge.",
            S['corps']),
        sp(8),
    ]

    # 3.2 Nœuds y
    elems += [
        Paragraph("3.2  Champ « y₀, y₁, ..., yₙ »", S['h2']),
        Paragraph(
            "Entrer les ordonnées correspondant aux abscisses, "
            "dans le même ordre et avec le même nombre de valeurs.",
            S['corps']),
        Preformatted(
            "Exemple :  0, 1, 0, 1, 0\n"
            "Exemple :  1, 2.5, 0, -1, 3, 1",
            S['code_style']),
        Paragraph(
            "Si le nombre de x et de y est différent, "
            "l'interface affichera une erreur.",
            S['corps']),
        sp(8),
    ]

    # 3.3 z0
    elems += [
        Paragraph("3.3  Champ « Dérivée initiale z₀ = S'(x₀) »", S['h2']),
        Paragraph(
            "Ce paramètre fixe la pente de la spline au premier nœud x₀. "
            "C'est le seul degré de liberté du problème : toutes les autres "
            "dérivées z_i sont calculées automatiquement par récurrence.",
            S['corps']),
        Paragraph(
            "Valeur par défaut : 0.0 (spline plate au départ). "
            "Utiliser les boutons +/- ou taper directement une valeur. "
            "Modifier z₀ change immédiatement la forme de toute la courbe.",
            S['corps']),
        sp(8),
    ]

    # 3.4 Points
    elems += [
        Paragraph("3.4  Curseur « Points d'évaluation »", S['h2']),
        Paragraph(
            "Contrôle le nombre de points x où S(x) est calculée "
            "(entre 100 et 2000). Plus ce nombre est grand, plus la courbe "
            "est lisse, mais le calcul prend légèrement plus de temps.",
            S['corps']),
        Paragraph(
            "Valeur recommandée : 500 pour un bon équilibre qualité/vitesse.",
            S['corps']),
        sp(10),
    ]

    # ── Métriques ─────────────────────────────────────────────────────────────
    elems += [
        Paragraph("4. Métriques affichées en haut", S['h1']), sep(S),
    ]
    data_met = [
        ['Métrique', 'Signification'],
        ['Sans SymPy', 'Durée médiane du calcul numérique (NumPy), en millisecondes'],
        ['Avec SymPy', 'Durée médiane du calcul symbolique (SymPy), en millisecondes'],
        ['Rapport', 'Combien de fois SymPy est plus lent que NumPy (ex. 80×)'],
        ['Erreur max', 'Différence maximale entre les deux courbes |S_np - S_sp|'],
    ]
    t2 = Table(data_met, colWidths=[4*cm, 13*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (0, -1), 'CENTER'),
        ('ALIGN',      (1, 1), (-1, -1), 'LEFT'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e3f2fd'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#90caf9')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 26),
    ]))
    elems += [t2, sp(12), PageBreak()]

    # ── Onglets ───────────────────────────────────────────────────────────────
    elems += [
        Paragraph("5. Les trois onglets de résultats", S['h1']), sep(S),
    ]

    # Onglet 1
    elems += [
        Paragraph("Onglet 1 — Courbe S(x)", S['h2']),
        Paragraph(
            "Affiche le graphique interactif de la spline calculée par les "
            "deux méthodes superposées :", S['corps']),
        Paragraph(
            "  • Ligne bleue pleine  →  Sans SymPy (NumPy)", S['corps']),
        Paragraph(
            "  • Ligne rouge pointillée  →  Avec SymPy", S['corps']),
        Paragraph(
            "  • Points noirs  →  les nœuds (x_i, y_i) saisis", S['corps']),
        Paragraph(
            "Les deux courbes doivent se superposer parfaitement "
            "(erreur < 1e-12). Si elles divergent, vérifier les entrées.",
            S['corps']),
        Paragraph(
            "Interactions disponibles sur le graphique :", S['corps']),
        Paragraph("  • Zoom : cliquer-glisser sur une zone", S['corps']),
        Paragraph("  • Déplacement : maintenir Shift + cliquer-glisser", S['corps']),
        Paragraph("  • Réinitialiser : double-cliquer sur le graphique", S['corps']),
        Paragraph("  • Masquer une courbe : cliquer sur son nom dans la légende", S['corps']),
        sp(10),
    ]

    # Onglet 2
    elems += [
        Paragraph("Onglet 2 — Comparaison temps", S['h2']),
        Paragraph(
            "Affiche deux informations sur les durées de calcul :", S['corps']),
        Paragraph(
            "  • Graphique en barres : durée médiane de chaque méthode en ms",
            S['corps']),
        Paragraph(
            "  • Tableau détaillé : durée de chacun des 5 runs individuels",
            S['corps']),
        Paragraph(
            "Le message d'information en bas explique pourquoi SymPy est "
            "plus lent (construction symbolique vs calcul flottant direct).",
            S['corps']),
        Paragraph(
            "Astuce : augmenter les « Points d'évaluation » dans la sidebar "
            "pour voir l'écart de performance s'accentuer.", S['corps']),
        sp(10),
    ]

    # Onglet 3
    elems += [
        Paragraph("Onglet 3 — Valeurs z", S['h2']),
        Paragraph(
            "Affiche deux sections :", S['corps']),
        Paragraph(
            "  • Tableau des z_i : pour chaque nœud x_i, la valeur de la "
            "dérivée S'(x_i) calculée par récurrence.", S['corps']),
        Paragraph(
            "  • Expressions symboliques S_i(x) : chaque morceau de la "
            "spline écrit sous forme algébrique développée (via SymPy), "
            "avec l'intervalle correspondant.", S['corps']),
        Paragraph(
            "Ces expressions permettent de vérifier manuellement que "
            "S_i(x_i) = y_i et que les morceaux se raccordent correctement.",
            S['corps']),
        sp(12),
    ]

    # ── Exemples d'utilisation ────────────────────────────────────────────────
    elems += [
        Paragraph("6. Exemples d'utilisation", S['h1']), sep(S),
    ]
    data_ex = [
        ['Cas', 'x', 'y', 'z₀', 'Observation attendue'],
        ['Exemple de base',
         '0, 1, 2, 3, 4',
         '0, 1, 0, 1, 0',
         '0',
         'Courbe oscillante passant par tous les points'],
        ['Nœuds linéaires',
         '0, 1, 2, 3',
         '0, 1, 2, 3',
         '1',
         'Spline proche d\'une droite (z₀=1 = pente)'],
        ['Nœuds irréguliers',
         '0, 0.5, 2, 3.5, 5',
         '1, 3, 0, 2, 1',
         '0',
         'Intervalles de largeur différente'],
        ['Changer z₀',
         '0, 1, 2, 3, 4',
         '0, 1, 0, 1, 0',
         '2 puis -2',
         'Forme de la courbe change entièrement'],
    ]
    t3 = Table(data_ex, colWidths=[3.5*cm, 3*cm, 3*cm, 1.5*cm, 6*cm])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, -1), 8.5),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e8f5e9'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a5d6a7')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 28),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elems += [t3, sp(12)]

    # ── Erreurs fréquentes ────────────────────────────────────────────────────
    elems += [
        Paragraph("7. Messages d'erreur fréquents", S['h1']), sep(S),
    ]
    data_err = [
        ['Message d\'erreur', 'Cause', 'Solution'],
        ['Erreur dans les nœuds',
         'Nombre de x ≠ nombre de y',
         'Vérifier que les deux champs ont le même nombre de valeurs'],
        ['Les xi doivent être triés !',
         'Les x ne sont pas en ordre croissant',
         'Trier les x de la plus petite à la plus grande valeur'],
        ['Erreur dans les nœuds (générique)',
         'Valeur non numérique saisie (ex. lettre)',
         'Ne saisir que des nombres séparés par des virgules'],
        ['Courbes qui divergent',
         'Rare : précision numérique',
         'Erreur max affichée en haut, normale si < 1e-10'],
    ]
    t4 = Table(data_err, colWidths=[4.5*cm, 5*cm, 7.5*cm])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#b71c1c')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffebee'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ef9a9a')),
        ('ROWHEIGHT', (0, 0), (-1, -1), 30),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    elems.append(t4)

    doc.build(elems)
    print("  [OK] guide_interface.pdf")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Génération des PDFs...")
    gen_documentation()
    gen_algorithmes()
    gen_guide_presentation()
    gen_guide_interface()
    print("\nFichiers créés :")
    print("  documentation.pdf")
    print("  algorithmes.pdf")
    print("  guide_presentation.pdf")
    print("  guide_interface.pdf")
