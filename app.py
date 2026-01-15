import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analizador JV", layout="wide")

st.title("🚀 Analizador de Inversión y Joint Venture")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    modo = st.radio("Cálculo basado en:", ["Precio de Compra", "Beneficio Objetivo"])
    meses = st.number_input("Duración (meses):", value=12, min_value=1)
    
    st.divider()
    st.subheader("📊 Datos para Comparativa")
    if modo == "Precio de Compra":
        l_esc = "Compra (€)"
        v1, v2, v3 = 185000, 200000, 215000
    else:
        l_esc = "Beneficio (€)"
        v1, v2, v3 = 130000, 150000, 110000

    # Aquí es donde metes los 3 datos con los que juegas
    esc1 = st.number_input(f"{l_esc} 1", value=v1)
    esc2 = st.number_input(f"{l_esc} 2", value=v2)
    esc3 = st.number_input(f"{l_esc} 3", value=v3)

# --- BLOQUES DESPLEGABLES (CUERPO PRINCIPAL) ---
with st.expander("🏠 Datos del Proyecto", expanded=False):
    col1, col2 = st.columns(2)
    m2 = col1.number_input("Metros Totales:", value=120)
    reforma_m2 = col2.number_input("Reforma/m2:", value=1000)
    
    col3, col4 = st.columns(2)
    num_viv = col3.number_input("Nº Viviendas:", value=4)
    venta_un = col4.number_input("P. Venta/Ud:", value=120000)
    
    itp_pct = st.slider("ITP (%):", 0, 15, 7) / 100

with st.expander("🤝 Estructura JV", expanded=False):
    ap_inv_pct = st.slider("% Aportación Inversor:", 0, 100, 90) / 100
    otros_gastos = st.number_input("Otros Gastos (Bolsa):", value=32050)

with st.expander("💰 Reparto de Beneficios", expanded=False):
    ben_obj = st.number_input("Límite Tramo 1 (Beneficio Objetivo):", value=130000)
    rep1_inv = st.slider("% Inversor Tramo 1:", 0, 100, 55) / 100
    rep2_inv = st.slider("% Inversor Zona Bonus:", 0, 100, 40) / 100

# --- LÓGICA DE CÁLCULO ---
escenarios = [esc1, esc2, esc3]
tabla_data = []

r_total = m2 * reforma_m2
v_total = venta_un * num_viv

for val in escenarios:
    if modo == "Precio de Compra":
        compra = val
        ben = v_total - (compra * (1 + itp_pct)) - r_total - otros_gastos
    else:
        ben = val
        compra = (v_total - ben - r_total - otros_gastos) / (1 + itp_pct)
    
    inv_t = (compra * (1 + itp_pct)) + r_total + otros_gastos
    c_inv = inv_t * ap_inv_pct
    c_ges = inv_t * (1 - ap_inv_pct)
    
    # Waterfall
    b1 = min(ben, ben_obj)
    b2 = max(0, ben - ben_obj)
    g_inv = (b1 * rep1_inv) + (b2 * rep2_inv)
    g_ges = (b1 * (1 - rep1_inv)) + (b2 * (1 - rep2_inv))
    
    # ROI Anualizado
    roi_inv = (g_inv / c_inv) * (12/meses) if c_inv > 0 else 0
    roi_ges = (g_ges / c_ges) * (12/meses) if c_ges > 0 else 0
    
    tabla_data.append({
        "Escenario": f"{val:,} €",
        "Compra": f"{compra:,.0f} €",
        "Beneficio": f"{ben:,.0f} €",
        "ROI Inv. Anual": f"{roi_inv*100:.1f}%",
        "ROI Ges. Anual": f"{roi_ges*100:.1f}%",
        "Cobro Inv.": f"{(c_inv + g_inv):,.0f} €",
        "Cobro Ges.": f"{(c_ges + g_ges):,.0f} €"
    })

# --- MOSTRAR RESULTADOS ---
st.divider()
st.subheader("📊 Resultados Comparativos")
st.table(pd.DataFrame(tabla_data))
    mmm
