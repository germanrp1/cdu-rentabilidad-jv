import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analizador JV - Detalle Costes", layout="wide")

# --- BARRA LATERAL ---
st.sidebar.title("⚙️ Configuración")
modo = st.sidebar.radio("Calcular por:", ["Precio de Compra", "Beneficio Objetivo"])
inv_objetivo = st.sidebar.number_input("Inversión Total Deseada (€):", value=350000)
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
st.title("🚀 Analizador JV: Detalle de Inversión")

with st.expander("🏠 Proyecto y Reforma", expanded=False):
    c1, c2 = st.columns(2)
    m2 = c1.number_input("Metros Totales:", value=120)
    ref_m2 = c2.number_input("Reforma/m2:", value=1000)
    num_viv = c1.number_input("Nº Viviendas:", value=4)
    v_un = c2.number_input("P. Venta/Ud:", value=120000)
    itp = st.slider("ITP (%):", 0, 15, 7) / 100

with st.expander("💸 Desglose de Costes Operativos", expanded=True):
    st.write("Introduce los gastos estimados para detallar la bolsa de costes:")
    col_a, col_b, col_c = st.columns(3)
    c_api = col_a.number_input("Comisión API/Compra:", value=0)
    c_venta = col_b.number_input("Comisión Venta Total:", value=0)
    luz_agua = col_c.number_input("Suministros (Obra):", value=1500)
    
    col_d, col_e, col_f = st.columns(3)
    ibi_comu = col_d.number_input("IBI y Comunidad:", value=2000)
    seguros = col_e.number_input("Seguros y Varios:", value=1200)
    
    # Suma de gastos conocidos
    gastos_conocidos = c_api + c_venta + luz_agua + ibi_comu + seguros
    st.info(f"Suma de gastos detallados: {gastos_conocidos:,} €")

with st.expander("🤝 Reparto y Tramos", expanded=False):
    ap_inv = st.slider("% Aportación Inversor:", 0, 100, 90) / 100
    b_obj = st.number_input("Beneficio Objetivo (Tramo 1):", value=130000)
    r1_inv = st.slider("% Inversor T1:", 0, 100, 55) / 100
    r2_inv = st.slider("% Inversor Bonus:", 0, 100, 40) / 100

# --- LÓGICA DE CÁLCULO ---
escenarios = [esc1, esc2, esc3]
filas = []

for val in escenarios:
    v_total = v_un * num_viv
    r_total = m2 * ref_m2
    
    if modo == "Precio de Compra":
        compra = val
        coste_adquisicion = compra * (1 + itp)
        # El ajuste es lo que falta para llegar a la inversión objetivo
        ajuste_otros = inv_objetivo - coste_adquisicion - r_total - gastos_conocidos
        ben = v_total - inv_objetivo
    else:
        ben = val
        # Si fijamos beneficio y la inversión total es 350k, la venta debe cubrir ambos
        # (Aquí el beneficio se resta de la venta para ver si la inversión de 350k es posible)
        compra = (inv_objetivo - r_total - gastos_conocidos) / (1 + itp) # Simplificado para el ejemplo
        ajuste_otros = inv_objetivo - (compra * (1 + itp)) - r_total - gastos_conocidos

    inv_t = (compra * (1 + itp)) + r_total + gastos_conocidos + ajuste_otros
    cap_inv, cap_ges = inv_t * ap_inv, inv_t * (1 - ap_inv)
    
    # Waterfall
    b1, b2 = min(ben, b_obj), max(0, ben - b_obj)
    g_inv = (b1 * r1_inv) + (b2 * r2_inv)
    g_ges = (b1 * (1 - r1_inv)) + (b2 * (1 - r1_inv))
    
    filas.append({
        "Escenario": f"{val:,} €",
        "Compra": f"{compra:,.0f} €",
        "ITP": f"{(compra*itp):,.0f} €",
        "Reforma": f"{r_total:,.0f} €",
        "Gastos Detallados": f"{gastos_conocidos:,.0f} €",
        "Ajuste Otros": f"{ajuste_otros:,.0f} €",
        "INV. TOTAL": f"{inv_t:,.0f} €",
        "BENEFICIO": f"{ben:,.0f} €",
        "ROI Inv. Anual": f"{(g_inv/cap_inv)*(12/meses)*100:.1f}%" if cap_inv > 0 else "0%"
    })

st.divider()
st.subheader("📊 Desglose de Inversión y Resultados")
st.table(pd.DataFrame(filas))

st.warning(f"Nota: El campo 'Ajuste Otros' se calcula automáticamente para que la Inversión Total sea siempre {inv_objetivo:,} €.")
