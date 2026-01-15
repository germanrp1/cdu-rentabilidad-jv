import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analizador JV - Detalle Completo", layout="wide")

# --- BARRA LATERAL ---
st.sidebar.title("⚙️ Controles")
modo = st.sidebar.radio("Calcular por:", ["Precio de Compra", "Beneficio Objetivo"])
meses = st.sidebar.number_input("Duración (meses):", value=12, min_value=1)

st.sidebar.subheader("📊 Comparativa")
if modo == "Precio de Compra":
    l_esc, v1, v2, v3 = "Compra (€)", 185000, 200000, 215000
else:
    l_esc, v1, v2, v3 = "Beneficio (€)", 130000, 150000, 110000

esc1 = st.sidebar.number_input(f"{l_esc} 1", value=v1)
esc2 = st.sidebar.number_input(f"{l_esc} 2", value=v2)
esc3 = st.sidebar.number_input(f"{l_esc} 3", value=v3)

# --- CUERPO PRINCIPAL ---
st.title("🚀 Analizador JV: Desglose y Comparativa")

with st.expander("🏠 Proyecto, Reforma e Inversión", expanded=True):
    c1, c2 = st.columns(2)
    m2 = c1.number_input("Metros Totales:", value=120)
    ref_m2 = c2.number_input("Reforma/m2:", value=1000)
    num_viv = c1.number_input("Nº Viviendas:", value=4)
    v_un = c2.number_input("P. Venta/Ud:", value=120000)
    itp = st.slider("ITP (%):", 0, 15, 7) / 100
    
    st.divider()
    inv_referencia = st.number_input("Inversión Total de Referencia (Base):", value=350000)
    
    # Cálculo automático de "Otros gastos" basado en la compra de 185k para cuadrar los 350k
    compra_base = 185000
    itp_base = compra_base * itp
    reforma_base = m2 * ref_m2
    # Otros gastos = Inv_Total - Compra - ITP - Reforma
    otros_gastos_defecto = inv_referencia - compra_base - itp_base - reforma_base
    
    otros_gastos = st.number_input("Otros gastos (Ajuste global):", value=float(otros_gastos_defecto))
    st.caption(f"Este valor de 'Otros gastos' se mantendrá FIJO en las 3 comparativas.")

with st.expander("🤝 Estructura de Reparto", expanded=False):
    ap_inv_pct = st.slider("% Aportación Inversor:", 0, 100, 90) / 100
    b_obj = st.number_input("Beneficio Objetivo (Tramo 1):", value=130000)
    r1_inv = st.slider("% Inversor Tramo 1:", 0, 100, 55) / 100
    r2_inv = st.slider("% Inversor Zona Bonus:", 0, 100, 40) / 100

# --- LÓGICA DE CÁLCULO ---
escenarios = [esc1, esc2, esc3]
filas = []

for val in escenarios:
    v_total = v_un * num_viv
    r_total = m2 * ref_m2
    
    if modo == "Precio de Compra":
        compra = val
        ben = v_total - (compra * (1 + itp)) - r_total - otros_gastos
    else:
        ben = val
        # Despejamos compra: Venta - Ben - Reforma - Otros = Compra * (1 + ITP)
        compra = (v_total - ben - r_total - otros_gastos) / (1 + itp)

    # La inversión total ahora varía según el precio de compra
    inv_t = (compra * (1 + itp)) + r_total + otros_gastos
    
    # Capitales aportados
    cap_inv = inv_t * ap_inv_pct
    cap_ges = inv_t * (1 - ap_inv_pct)
    
    # Reparto Waterfall
    b1 = min(ben, b_obj)
    b2 = max(0, ben - b_obj)
    gan_inv = (b1 * r1_inv) + (b2 * r2_inv)
    gan_ges = (b1 * (1 - r1_inv)) + (b2 * (1 - r1_inv))
    
    # ROIs Anualizados
    roi_inv = (gan_inv / cap_inv) * (12/meses) if cap_inv > 0 else 0
    roi_ges = (gan_ges / cap_ges) * (12/meses) if cap_ges > 0 else 0
    
    filas.append({
        "Escenario": f"{val:,} €",
        "Compra": f"{compra:,.0f} €",
        "Inv. Total": f"{inv_t:,.0f} €",
        "Beneficio": f"{ben:,.0f} €",
        "Cap. Inversor": f"{cap_inv:,.0f} €",
        "ROI Inv. Anual": f"{roi_inv*100:.1f}%",
        "Cap. Gestor": f"{cap_ges:,.0f} €",
        "ROI Ges. Anual": f"{roi_ges*100:.1f}%",
        "Total Inversor": f"{(cap_inv + gan_inv):,.0f} €"
    })

st.divider()
st.subheader("📊 Tabla Comparativa Final")
st.table(pd.DataFrame(filas))
        
