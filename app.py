"""
Interface Streamlit — Spline Quadratique
Avec vs Sans SymPy (séance 03/03/26)
"""

import streamlit as st
import numpy as np
import time
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from spline_sans_sympy import spline_quadratique as spline_np
from spline_avec_sympy import spline_quadratique_sympy as spline_sp

# ─── Configuration ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spline Quadratique",
    page_icon="📐",
    layout="wide",
)

st.title("📐 Spline Quadratique — Interpolation par morceaux")

# ─── Sidebar : saisie des nœuds ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Paramètres")

    st.subheader("Nœuds d'interpolation")
    st.markdown("Entrez les valeurs séparées par des virgules.")

    xs_input = st.text_input("x₀, x₁, ..., xₙ", value="0, 1, 2, 3, 4")
    ys_input = st.text_input("y₀, y₁, ..., yₙ", value="0, 1, 0, 1, 0")

    z0 = st.number_input("Dérivée initiale z₀ = S'(x₀)", value=0.0, step=0.5)

    n_pts = st.slider("Points d'évaluation", 100, 2000, 500, 100)

    st.markdown("---")
    st.markdown(
        "**Formule (document)** :\n\n"
        r"$$S_i(x) = \frac{z_{i+1}-z_i}{2h_i}(x-x_i)^2 + z_i(x-x_i) + y_i$$"
    )
    st.markdown(
        "**Récurrence** :\n\n"
        r"$$z_{i+1} = \frac{2(y_{i+1}-y_i)}{h_i} - z_i$$"
    )

# ─── Parsing des entrées ─────────────────────────────────────────────────────
try:
    xs = [float(v.strip()) for v in xs_input.split(",")]
    ys = [float(v.strip()) for v in ys_input.split(",")]
    assert len(xs) == len(ys) and len(xs) >= 2
    assert xs == sorted(xs), "Les xi doivent être triés !"
except Exception as e:
    st.error(f"Erreur dans les nœuds : {e}")
    st.stop()

xs_arr = np.array(xs)
ys_arr = np.array(ys)
x_eval = np.linspace(xs[0], xs[-1], n_pts)

# ─── Calculs avec mesure du temps ────────────────────────────────────────────
REPS = 5

# Sans SymPy
temps_np_all = []
for _ in range(REPS):
    t0 = time.perf_counter()
    S_np = spline_np(xs_arr, ys_arr, x_eval, z0)
    temps_np_all.append(time.perf_counter() - t0)

# Avec SymPy
temps_sp_all = []
for _ in range(REPS):
    t0 = time.perf_counter()
    S_sp, morceaux, z_vals = spline_sp(xs, ys, x_eval, z0_val=z0)
    temps_sp_all.append(time.perf_counter() - t0)

med_np = np.median(temps_np_all) * 1e3   # ms
med_sp = np.median(temps_sp_all) * 1e3

# ─── Métriques ───────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Sans SymPy", f"{med_np:.3f} ms", help="Médiane sur 5 runs")
col2.metric("Avec SymPy", f"{med_sp:.3f} ms", help="Médiane sur 5 runs")
col3.metric("Rapport", f"{med_sp/med_np:.1f}×", delta=f"SymPy plus lent", delta_color="inverse")
col4.metric("Erreur max", f"{np.max(np.abs(S_np - S_sp)):.2e}", help="|S_np - S_sp|")

st.markdown("---")

# ─── Onglets ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Courbe S(x)", "⏱ Comparaison temps", "🔢 Valeurs z"])

# Tab 1 : Courbe
with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_eval, y=S_np, mode='lines',
                             name='Sans SymPy (NumPy)',
                             line=dict(color='royalblue', width=2.5)))
    fig.add_trace(go.Scatter(x=x_eval, y=S_sp, mode='lines',
                             name='Avec SymPy',
                             line=dict(color='tomato', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=xs, y=ys, mode='markers+text',
                             name='Nœuds',
                             text=[f'({xi},{yi})' for xi, yi in zip(xs, ys)],
                             textposition='top center',
                             marker=dict(color='black', size=9)))
    fig.update_layout(
        title="Spline Quadratique S(x)",
        xaxis_title="x",
        yaxis_title="S(x)",
        legend=dict(x=0.01, y=0.99),
        height=480,
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 2 : Durées
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        fig2 = go.Figure(go.Bar(
            x=['Sans SymPy\n(NumPy)', 'Avec SymPy'],
            y=[med_np, med_sp],
            marker_color=['royalblue', 'tomato'],
            text=[f'{med_np:.3f} ms', f'{med_sp:.3f} ms'],
            textposition='outside',
        ))
        fig2.update_layout(
            title="Durée médiane (ms)",
            yaxis_title="Temps (ms)",
            height=400,
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown("### Détail des runs")
        import pandas as pd
        df = pd.DataFrame({
            "Run": range(1, REPS + 1),
            "Sans SymPy (ms)": [t * 1e3 for t in temps_np_all],
            "Avec SymPy (ms)": [t * 1e3 for t in temps_sp_all],
        })
        st.dataframe(df.style.format("{:.4f}", subset=["Sans SymPy (ms)", "Avec SymPy (ms)"]),
                     use_container_width=True)
        st.info(
            f"SymPy est **{med_sp/med_np:.1f}× plus lent** : il construit "
            "des expressions symboliques et les simplifie avant l'évaluation, "
            "contrairement à NumPy qui opère directement sur des flottants."
        )

# Tab 3 : Valeurs z
with tab3:
    st.markdown("### Dérivées aux nœuds : $z_i = S'(x_i)$")
    st.markdown("Calculées par récurrence : $z_{i+1} = \\dfrac{2(y_{i+1}-y_i)}{x_{i+1}-x_i} - z_i$")

    import pandas as pd
    z_float = [float(z) for z in z_vals]
    df_z = pd.DataFrame({"i": range(len(xs)), "xᵢ": xs, "yᵢ": ys, "zᵢ = S'(xᵢ)": z_float})
    st.dataframe(df_z, use_container_width=True, hide_index=True)

    st.markdown("### Expressions symboliques Si(x) — SymPy")
    import sympy as ssp
    x_sym = ssp.Symbol('x')
    for i, (Si, xi, xi1) in enumerate(morceaux):
        st.latex(f"S_{{{i}}}(x) = {ssp.latex(Si)} \\quad x \\in [{xi},\\ {xi1}]")
