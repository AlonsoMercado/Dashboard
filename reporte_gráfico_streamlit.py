import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dashboard de Ventas y Compras", page_icon="📊")

@st.cache_data
def cargar_datos():
    df_ventas = pd.read_excel('KEYPROCESS_REPORTE_VENTA_20241216152610.xlsx')
    df_compras = pd.read_excel('KEYPROCESS_REPORTE_COMPRA_20241216153042.xlsx')
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

# Sidebar: filtros
st.sidebar.header("Filtros")
rango_fecha = st.sidebar.date_input("Rango de Fechas", 
    [df_ventas['FECHA_TRANSACCION'].min(), df_ventas['FECHA_TRANSACCION'].max()]
)
años_seleccionados = st.sidebar.multiselect("Años", sorted(df_ventas['AÑO'].unique()), default=None)
meses_seleccionados = st.sidebar.multiselect("Meses", sorted(df_ventas['MES'].unique()), default=None)
forma_pago = st.sidebar.multiselect("Forma de Pago", df_ventas['FORMA_DE_PAGO'].unique(), default=None)

# Función de filtrado
def filtrar_datos(df):
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
    return df_filtrado

# Filtrar datos
ventas_filtradas = filtrar_datos(df_ventas)
compras_filtradas = filtrar_datos(df_compras)

# SECCIÓN CLIENTES (VENTAS)
st.header(" Clientes - Ventas")
col1, col2 = st.columns(2)

# Top 10 Clientes
top_clientes = ventas_filtradas.groupby('RAZON SOCIAL')['MONTO'].sum().nlargest(10).reset_index()
fig_top_clientes = px.bar(top_clientes, x='MONTO', y='RAZON SOCIAL', orientation='h', title="Top 10 Clientes (Ventas)")
col1.plotly_chart(fig_top_clientes, use_container_width=True)

# Ventas Acumuladas Mensuales
ventas_acumuladas = ventas_filtradas.groupby(ventas_filtradas['FECHA_TRANSACCION'].dt.to_period('M'))['MONTO'].sum().reset_index()
ventas_acumuladas['FECHA_TRANSACCION'] = ventas_acumuladas['FECHA_TRANSACCION'].dt.to_timestamp()
fig_acumulado_ventas = px.line(ventas_acumuladas, x='FECHA_TRANSACCION', y='MONTO', title="Ventas Acumuladas Mensuales")

col2.plotly_chart(fig_acumulado_ventas, use_container_width=True)

# Distribución por Forma de Pago (Ventas)
st.plotly_chart(px.pie(ventas_filtradas, names='FORMA_DE_PAGO', values='MONTO', title="Distribución por Forma de Pago (Ventas)"))

# SECCIÓN PROVEEDORES (COMPRAS)
st.header(" Proveedores - Compras")
col3, col4 = st.columns(2)

# Top 10 Proveedores
top_proveedores = compras_filtradas.groupby('RAZON SOCIAL')['MONTO'].sum().nlargest(10).reset_index()
# Crear el gráfico de barras con etiquetas personalizadas
fig_top_proveedores = px.bar(
    top_proveedores, 
    x='MONTO', 
    y='RAZÓN SOCIAL', 
    orientation='h', 
    title="Top 10 Proveedores",
    labels={
        'MONTO': 'Monto Total (CLP)',  # Etiqueta personalizada para el eje X
        'RAZON SOCIAL': 'Proveedor'  # Etiqueta personalizada para el eje Y 
        })

col3.plotly_chart(fig_top_proveedores, use_container_width=True)

# Compras Acumuladas Mensuales
compras_acumuladas = compras_filtradas.groupby(compras_filtradas['FECHA_TRANSACCION'].dt.to_period('M'))['MONTO'].sum().reset_index()
compras_acumuladas['FECHA_TRANSACCION'] = compras_acumuladas['FECHA_TRANSACCION'].dt.to_timestamp()
fig_acumulado_compras = px.line(
    compras_acumuladas, x='FECHA_TRANSACCION', y='MONTO',
    labels={'x': 'Fecha Transacción', 'y': 'Monto'},
    title="Compras Acumuladas Mensuales"
)
fig_acumulado_compras.add_scatter(
    x=compras_acumuladas['FECHA_TRANSACCION'], 
    y=compras_acumuladas['MONTO'], 
    mode='lines', 
    name='Compras Acumuladas',
    line=dict(color='red')
)
fig_acumulado_compras.add_scatter(
    x=ventas_acumuladas['FECHA_TRANSACCION'], 
    y=ventas_acumuladas['MONTO'], 
    mode='lines', 
    name='Ventas Acumuladas',
    line=dict(color='blue')
)
st.plotly_chart(fig_acumulado_compras, use_container_width=True)

# Distribución por Forma de Pago (Compras)
col4.plotly_chart(px.pie(compras_filtradas, names='FORMA_DE_PAGO', values='MONTO', title="Distribución por Forma de Pago (Compras)"))



