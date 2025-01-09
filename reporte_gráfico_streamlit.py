import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dashboard de Ventas y Compras", page_icon="📊")

@st.cache_data
def cargar_datos():
    df_ventas = pd.read_excel('KEYPROCESS_REPORTE_VENTA_20250102121000.xlsx')
    df_compras = pd.read_excel('KEYPROCESS_REPORTE_COMPRA_20250102121137.xlsx')
    return df_ventas, df_compras

df_ventas, df_compras = cargar_datos()
meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
         7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

# Preparar datos
def preparar_datos(df):
    df = df.rename(columns={'FECHA': 'FECHA_TRANSACCION', 'FECHA DOCUMENTO': 'FECHA_TRANSACCION',
                            'TOTAL': 'MONTO', 'RAZON SOCIAL': 'RAZON SOCIAL', 'FORMA DE PAGO': 'FORMA_DE_PAGO'})
    df['FECHA_TRANSACCION'] = pd.to_datetime(df['FECHA_TRANSACCION'], dayfirst=True)
    df['FORMA_DE_PAGO'] = df['FORMA_DE_PAGO'].fillna("No indica medio").str.strip().str.lower()
    df['FORMA_DE_PAGO'] = df['FORMA_DE_PAGO'].replace({'credito': 'crédito'})
    df['AÑO'] = df['FECHA_TRANSACCION'].dt.year
    df['MES'] = df['FECHA_TRANSACCION'].dt.month.map(meses)
    return df

df_ventas = preparar_datos(df_ventas)
df_compras = preparar_datos(df_compras)

# Sidebar: Filtros dinámicos
st.sidebar.header("Filtros")

# Filtro de rango de fechas
rango_fecha = st.sidebar.date_input("Rango de Fechas", [df_ventas['FECHA_TRANSACCION'].min(), df_ventas['FECHA_TRANSACCION'].max()])

# Filtro de años
años_seleccionados = st.sidebar.multiselect("Años", sorted(df_ventas['AÑO'].unique()), default=None)

# Filtrar datos temporalmente por año
ventas_temp = df_ventas
compras_temp = df_compras
if años_seleccionados:
    ventas_temp = ventas_temp[ventas_temp['AÑO'].isin(años_seleccionados)]
    compras_temp = compras_temp[compras_temp['AÑO'].isin(años_seleccionados)]

# Filtro de meses
meses_seleccionados = st.sidebar.multiselect(
    "Meses",
    sorted(ventas_temp['MES'].unique(), key=lambda x: list(meses.values()).index(x)),
    default=None
)

# Filtro dinámico de clientes y proveedores
clientes_disponibles = ventas_temp['RAZON SOCIAL'].unique()
proveedores_disponibles = compras_temp['RAZON SOCIAL'].unique()

clientes = st.sidebar.multiselect("Clientes", clientes_disponibles, default=None)
proveedores = st.sidebar.multiselect("Proveedores", proveedores_disponibles, default=None)

# Filtro de forma de pago
forma_pago = st.sidebar.multiselect("Forma de Pago", ventas_temp['FORMA_DE_PAGO'].unique(), default=None)

# Función de filtrado
def filtrar_datos(df, tipo):
    df_filtrado = df[
        (df['FECHA_TRANSACCION'] >= pd.to_datetime(rango_fecha[0])) &
        (df['FECHA_TRANSACCION'] <= pd.to_datetime(rango_fecha[1]))
    ]
    if años_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['AÑO'].isin(años_seleccionados)]
    if meses_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['MES'].isin(meses_seleccionados)]
    if forma_pago:
        df_filtrado = df_filtrado[df_filtrado['FORMA_DE_PAGO'].isin(forma_pago)]
    if tipo == 'ventas' and clientes:
        df_filtrado = df_filtrado[df_filtrado['RAZON SOCIAL'].isin(clientes)]
    if tipo == 'compras' and proveedores:
        df_filtrado = df_filtrado[df_filtrado['RAZON SOCIAL'].isin(proveedores)]
    return df_filtrado

ventas_filtradas = filtrar_datos(df_ventas, 'ventas')
compras_filtradas = filtrar_datos(df_compras, 'compras')

# Indicadores de Totales
st.header("Indicadores Totales")
col1, col2 = st.columns(2)
col1.metric("Total Ventas (CLP)", f"{ventas_filtradas['MONTO'].sum():,.0f}")
col2.metric("Total Compras (CLP)", f"{compras_filtradas['MONTO'].sum():,.0f}")

# Sección de gráficos
st.header("📊 Comparación de Ventas y Compras")
ventas_acumuladas = ventas_filtradas.groupby(ventas_filtradas['FECHA_TRANSACCION'].dt.to_period('M'))['MONTO'].sum().reset_index()
ventas_acumuladas['FECHA_TRANSACCION'] = ventas_acumuladas['FECHA_TRANSACCION'].dt.to_timestamp()
ventas_acumuladas['MES'] = ventas_acumuladas['FECHA_TRANSACCION'].dt.month.map(meses)
ventas_acumuladas['AÑO'] = ventas_acumuladas['FECHA_TRANSACCION'].dt.year

# Compras Acumuladas Mensuales
compras_acumuladas = compras_filtradas.groupby(compras_filtradas['FECHA_TRANSACCION'].dt.to_period('M'))['MONTO'].sum().reset_index()
compras_acumuladas['FECHA_TRANSACCION'] = compras_acumuladas['FECHA_TRANSACCION'].dt.to_timestamp()
compras_acumuladas['MES'] = compras_acumuladas['FECHA_TRANSACCION'].dt.month.map(meses)
compras_acumuladas['AÑO'] = compras_acumuladas['FECHA_TRANSACCION'].dt.year
fig_comparacion = px.line(
    ventas_acumuladas, x='FECHA_TRANSACCION', y='MONTO',
    title="Comparación de Ventas y Compras Mensuales Acumuladas",
    labels={'FECHA_TRANSACCION': 'Fecha', 'MONTO': 'Monto Total (CLP)'}
)
fig_comparacion.add_scatter(
    x=compras_acumuladas['FECHA_TRANSACCION'],
    y=compras_acumuladas['MONTO'],
    mode='lines',
    name='Compras Acumuladas',
    line=dict(color='red')
)
fig_comparacion.add_scatter(
    x=ventas_acumuladas['FECHA_TRANSACCION'], 
    y=ventas_acumuladas['MONTO'], 
    mode='lines', 
    name='Ventas Acumuladas',
    line=dict(color='blue')
)
st.plotly_chart(fig_comparacion, use_container_width=True)
col3, col4 = st.columns(2)
fig_acumulado_ventas = px.bar(
    ventas_acumuladas, 
    x='MES', 
    y='MONTO', 
    color='AÑO',
    category_orders={"MES": list(meses.values())},  # Ordenar meses cronológicamente
    labels={'MES': 'Mes', 'MONTO': 'Monto Total (CLP)', 'AÑO': 'Año'},
    title="Ventas Acumuladas Mensuales"
)
st.plotly_chart(fig_acumulado_ventas, use_container_width=True)
# Top 10 Clientes
top_clientes = ventas_filtradas.groupby('RAZON SOCIAL')['MONTO'].sum().nlargest(10).reset_index()
fig_top_clientes = px.bar(top_clientes, x='MONTO', y='RAZON SOCIAL', orientation='h', labels={'MONTO':'MONTO (CLP)',
'RAZON SOCIAL':'Razón Social'}, title="Top 10 Clientes (Ventas)")
col3.plotly_chart(fig_top_clientes, use_container_width=True)
col4.plotly_chart(px.pie(ventas_filtradas, names='FORMA_DE_PAGO', values='MONTO', title="Distribución por Forma de Pago (Ventas)"))

# Distribución por Forma de Pago (Ventas)
#st.plotly_chart(px.pie(ventas_filtradas, names='FORMA_DE_PAGO', values='MONTO', title="Distribución por Forma de Pago (Ventas)"))

# SECCIÓN PROVEEDORES (COMPRAS)
st.header(" Proveedores - Compras")
col5, col6 = st.columns(2)

# Top 10 Proveedores
top_proveedores = compras_filtradas.groupby('RAZON SOCIAL')['MONTO'].sum().nlargest(10).reset_index()
# Crear el gráfico de barras con etiquetas personalizadas
fig_top_proveedores = px.bar(top_proveedores, x='MONTO', y='RAZON SOCIAL', orientation='h', title="Top 10 Proveedores", labels={'MONTO': 'Monto Total (CLP)', 'RAZON SOCIAL': 'Proveedor'})

col5.plotly_chart(fig_top_proveedores, use_container_width=True)
# Distribución por Forma de Pago (Compras)
col6.plotly_chart(px.pie(compras_filtradas, names='FORMA_DE_PAGO', values='MONTO', title="Distribución por Forma de Pago (Compras)"))
fig_acumulado_compras = px.bar(
    compras_acumuladas, 
    x='MES', 
    y='MONTO', 
    color='AÑO',
    category_orders={"MES": list(meses.values())},  # Ordenar meses cronológicamente
    labels={'MES': 'Mes', 'MONTO': 'Monto Total (CLP)', 'AÑO': 'Año'},
    title="Compras Acumuladas Mensuales"
)
st.plotly_chart(fig_acumulado_compras, use_container_width=True)
st.plotly_chart(fig_acumulado_compras, use_container_width=True)


