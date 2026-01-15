import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Analizador JV", layout="wide")

st.title("🚀 Analizador de Inversión y Joint Venture")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    modo = st.radio("Cálculo:", ["Beneficio", "Compra Máxima"])
    meses = st.number_input("Duración (meses):", value=12, min_value=1)
    
    st.divider()
    st.subheader("📊 Escenarios")
    if modo == "Beneficio":
        v1, v2, v3 = 185000, 200000, 215000
        l_esc = "Precio Compra"
    else:
        v1, v2, v3 = 130000, 150000, 110000
        l_esc = "Ben. Objetivo"

    esc1 = st.number_input(f"{l_esc} 1", value=v1)
    esc2 = st.number_input(f"{l_esc} 2", value=v2)
    esc3 = st.number_input(f"{l_esc} 3", value=v3)

# --- BLOQUES DESPLEGABLES ---
with st.expander("🏠 Datos del Proyecto", expanded=False):
    c1, c2 = st.columns(2)
    m2 = c1.number_input("Metros Totales:", value=120)
    reforma_m2 = c2.number_input("Reforma/m2:", value=1000)
    
    c3, c4 = st.columns(2)
    num_viv = c3.number_input("Nº Viviendas:", value=4)
    venta_un = c4.number_input("P. Venta/Ud:", value=120000)
    
    itp_pct = st.slider("ITP (%):", 0, 15, 7) / 100

with st.expander("🤝 Estructura JV", expanded=False):
    ap_inv_pct = st.slider("% Aportación Inversor:", 0, 100, 90) / 100
    otros_gastos = st.number_input("Otros Gastos (Bolsa):", value=32050)

with st.expander("💰 Reparto de Beneficios", expanded=False):
    ben_obj = st.number_input("Límite Tramo 1 (€):", value=130000)
    
    st.write("**Tramo 1 (Hasta Límite)**")
    rep1_inv = st.slider("% Inversor T1:", 0, 100, 55) / 100
    
    st.write("**Tramo 2 (Zona Bonus)**")
    rep2_inv = st.slider("% Inversor Bonus:", 0, 100, 40) / 100

# --- CÁLCULOS ---
escenarios = [esc1, esc2, esc3]
data_final = []

for val in escenarios:
    v_total = venta_un * num_viv
    r_total = m2 * reforma_m2
    
    if modo == "Beneficio":
        compra = val
        ben = v_total - (compra * (1 + itp_pct)) - r_total - otros_gastos
    else:
        ben = val
        compra = (v_total - ben - r_total - otros_gastos) / (1 + itp_pct)
    
    inv_t = (compra * (1 + itp_pct)) + r_total + otros_gastos
    c_inv, c_ges = inv_t * ap_inv_pct, inv_t * (1 - ap_inv_pct)
    
    b1, b2 = min(ben, ben_obj), max(0, ben - ben_obj)
    g_inv = (b1 * rep1_inv) + (b2 * rep2_inv)
    g_ges = (b1 * (1 - rep1_inv)) + (b2 * (1 - rep2_inv))
    
    r_inv = (g_inv / c_inv) * (12/meses) if c_inv > 0 else 0
    r_ges = (g_ges / c_ges) * (12/meses) if c_ges > 0 else 0
    
    data_final.append({
        "Escenario": f"{val:,} €",
        "Compra": f"{compra:,.0f} €",
        "Beneficio": f"{ben:,.0f} €",
        "ROI Inv. Anual": f"{r_inv*100:.1f}%",
        "ROI Ges. Anual": f"{r_ges*100:.1f}%"
    })

st.divider()
st.table(pd.DataFrame(data_final))
st.success("App actualizada. Revisa los desplegables.")
    
