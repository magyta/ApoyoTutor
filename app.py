# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""

# main.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

st.set_page_config(page_title="Tutoría Académica - Reporte Dinámico", layout="wide")
def generar_distribucion_notas(df1):
    # 1. Configuración del estilo visual (apto para publicación Q1)
    sns.set_theme(style="white")
    plt.figure(figsize=(12, 8))

    # 2. Creación del histograma con facetas por periodo
# Usamos displot para crear una cuadrícula de gráficos automáticamente
    g = sns.displot(
        data=df1,
        x="Nota1",
        col="Id_Periodo",       # Crea un gráfico por cada periodo
        col_wrap=2,          # Máximo 3 gráficos por fila
        kde=True,            # Añade la curva de densidad suavizada
        color="#2c3e50",     # Color profesional (azul oscuro grisáceo)
        bins=15,             # Ajusta el número de barras
        edgecolor="white"
    )

    # 3. Personalización de ejes y títulos
    g.set_axis_labels("Calificación (Nota 1)", "Frecuencia de Estudiantes")
    g.set_titles("Periodo: {col_name}")
    g.tight_layout()

# Añadir una línea vertical en el umbral de aprobación (7.0) en cada faceta
    for ax in g.axes.flat:
        ax.axvline(7, color='red', linestyle='--', alpha=0.7, label='Umbral 7.0')

    plt.show()


# 1. Carga optimizada de datos
@st.cache_data
def cargar_datos():
    # Asegúrate de que el nombre del archivo sea exacto
    df = pd.read_excel("Consulta1.xlsx", engine='openpyxl')
    
    # Limpieza de nombres de columnas (quita espacios extras)
    df.columns = df.columns.str.strip()
    df['rendimiento'] = np.where(df['Nota1'] > 7, 1, 2) # 1 es alto, 2 es bajo
    # Convierto los ids en entero
    df['Id_Periodo'] = df['Id_Periodo'].astype(int)
    df['Id_Nivel'] = df['Id_Nivel'].astype(int)
    df['Id_Materia'] = df['Id_Materia'].astype(int)
    df['Codigo_Estudiante'] = df['Codigo_Estudiante'].astype(int)
    # IMPORTANTE: Ordenar el DataFrame globalmente por sus IDs
    # Esto asegura que cuando saquemos los valores únicos, ya vengan en orden.
    # Ajusta los nombres de las columnas ID según tu Excel (ej. id_periodo, id_nivel)
    columnas_orden = []
    if 'Id_Periodo' in df.columns: columnas_orden.append('Id_Periodo')
    if 'Id_Nivel' in df.columns: columnas_orden.append('Id_Nivel')
    if 'Id_Materia' in df.columns: columnas_orden.append('Id_Materia')
    if 'Paralelo' in df.columns: columnas_orden.append('Paralelo')
    
    if columnas_orden:
        df = df.sort_values(by=columnas_orden)
    
    return df


try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()
#####

def obtener_puntos_criticos(df1, dimension):
    """
    Calcula el porcentaje de bajo rendimiento agrupado por periodo 
    y una dimensión específica (materia o nivel).
    
    """
    pd.options.display.precision = 2
    if dimension ==1:
        columnas = ['Id_Periodo','Descripcion_Periodo','Id_Nivel','Descripcion_Nivel']
    else: 
        columnas = ['Id_Periodo','Descripcion_Periodo','Id_Materia','Descripcion_Materia']

    df1['es_bajo'] = df1['Nota1'] < 7
    
    analisis = df1.groupby(columnas)['es_bajo'].mean() * 100
    analisis = analisis.reset_index().rename(columns={'es_bajo':'Porcentaje_Bajo_Rendimiento'})
    
    # Encontrar el máximo por periodo
    idx_max = analisis.groupby(['Id_Periodo'])['Porcentaje_Bajo_Rendimiento'].idxmax()
    return analisis.loc[idx_max]



#####
def obtener_total_estudiantes_matriculados(df_1):
    """
    Recibe un DataFrame de pandas y devuelve el número total de filas.
    """
    df_ep = (
    df_1.groupby(['Id_Periodo', 'Codigo_Estudiante'])
      .agg(
          AVE=('Nota1', 'mean'), 
          LOW_AVE=('rendimiento', 'max') # BAJO RENDIMIENTO
      )
      .reset_index()
      )
    # .shape devuelve una tupla (filas, columnas), el índice [0] son las filas
    total = df_ep.shape[0]
    return total

def obtener_total_estudiantes_bajo_rendimiento(df_1):
    """
    Recibe un DataFrame de pandas y devuelve el número total de filas.
    """
    df_ep = (
    df_1.groupby(['Id_Periodo', 'Codigo_Estudiante'])
      .agg(
          AVE=('Nota1', 'mean'), 
          LOW_AVE=('rendimiento', 'max') # BAJO RENDIMIENTO
      )
      .reset_index()
      )
    
    tabla_resumen = (
    df_ep.groupby('Id_Periodo')
         .apply(lambda x: pd.Series({
             'NS': x['Codigo_Estudiante'].nunique(),
             'NS_2': ((x['LOW_AVE'] == 2)).sum(),
             'NS_1': ((x['LOW_AVE'] == 1)).sum()
         }))
         .reset_index()
         )

    a = tabla_resumen['NS_2'].sum()
    return a

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de búsqueda")

# Filtros que se actualizan entre sí
#periodo_list = sorted(df['Descripcion_Periodo'].unique().tolist())
#periodo_sel = st.sidebar.selectbox("1. Seleccione Periodo", ["Todos"] + periodo_list)
# 1. PERIODO (Ordenado por ID)
# Al usar dict.fromkeys conservamos el orden en que aparecen en el DF ya ordenado
periodos = list(dict.fromkeys(df['Descripcion_Periodo'])) 
periodo_sel = st.sidebar.selectbox("1. Seleccione Periodo", ["Todos"] + periodos)

# Filtro por periodo
df_temp = df.copy()
if periodo_sel != "Todos":
    df_temp = df_temp[df_temp['Descripcion_Periodo'] == periodo_sel]

# 2. NIVEL (Ordenado por ID)
niveles = list(dict.fromkeys(df_temp['Descripcion_Nivel']))
nivel_sel = st.sidebar.selectbox("2. Seleccione Nivel", ["Todos"] + niveles)

if nivel_sel != "Todos":
    df_temp = df_temp[df_temp['Descripcion_Nivel'] == nivel_sel]

# 3. ASIGNATURA (Ordenada por ID)
asignaturas = list(dict.fromkeys(df_temp['Descripcion_Materia']))
asignatura_sel = st.sidebar.selectbox("3. Seleccione Asignatura", ["Todos"] + asignaturas)

if asignatura_sel != "Todos":
    df_temp = df_temp[df_temp['Descripcion_Materia'] == asignatura_sel]

# 4. PARALELO (Ordenado por ID)
paralelos = list(dict.fromkeys(df_temp['Paralelo']))
paralelo_sel = st.sidebar.selectbox("4. Seleccione Paralelo", ["Todos"] + paralelos)

if paralelo_sel != "Todos":
    df_temp = df_temp[df_temp['Paralelo'] == paralelo_sel]

umbral = st.sidebar.slider("Umbral Bajo Rendimiento", 0.0, 10.0, 7.0)
# Fin de los filtros 
# --- LÓGICA DE VISUALIZACIÓN DINÁMICA ---
st.title("📋 Reporte de Estudiantes de Bajo Rendimiento")

# Filtrar por bajo rendimiento
bajo_rend = df_temp[df_temp['Nota1'] < umbral]

# DETERMINAR QUÉ MOSTRAR SEGÚN EL NIVEL DE FILTRO
# 1. Filtro por periodo y todos los niveles
if periodo_sel != "Todos" and nivel_sel == "Todos":
    st.subheader(f"Resumen de Bajo Rendimiento por Periodo: {periodo_sel}")
    #resumen = bajo_rend.groupby('Descripcion_Nivel')['Codigo_Estudiante'].count().reset_index()
    #fig = px.bar(resumen, x='Descripcion_Nivel', y='Codigo_Estudiante', color='Descripcion_Nivel', title="Alumnos en Riesgo por Nivel")
    #st.plotly_chart(fig, use_container_width=True)
  
    
    # 1. Agrupamos y sumamos, pero incluimos el id_nivel para poder ordenar
    resumen = bajo_rend.groupby(['Id_Nivel','Descripcion_Nivel'])['Codigo_Estudiante'].count().reset_index()
    
    # 2. Ordenamos el DataFrame del resumen por el ID numérico
    resumen = resumen.sort_values(by='Id_Nivel')
    
    # 3. Creamos el gráfico indicando el orden de las categorías
    #orden_manual = ["PRIMER NIVEL", "SEGUNDO NIVEL", "TERCER NIVEL", "CUARTO NIVEL", "QUINTO NIVEL", 
     #           "SEXTO NIVEL", "SEPTIMO NIVEL", "OCTAVO NIVEL", "NOVENO NIVEL", "DECIMO NIVEL"]
    fig = px.bar(
        resumen, 
        x='Descripcion_Nivel', 
        y='Codigo_Estudiante', 
        title="Estudiantes en Riesgo por Nivel",
        color='Descripcion_Nivel',
        # Esta línea es la clave: fuerza a Plotly a respetar el orden del DataFrame
        category_orders={"Id_Nivel": resumen['Descripcion_Nivel'].tolist()} 
    )
   

#fig = px.bar(resumen, x='nivel', y='codigo_student', 
 #            category_orders={"nivel": orden_manual})
    
    st.plotly_chart(fig, use_container_width=True)

# 2. Filtro por periodo, nivel y todas las asignaturas
elif nivel_sel != "Todos" and asignatura_sel == "Todos":
    st.subheader(f"Resumen por Asignatura - Nivel: {nivel_sel}")
    resumen = bajo_rend.groupby('Descripcion_Materia')['Codigo_Estudiante'].count().reset_index()
    fig = px.bar(resumen, x='Descripcion_Materia', y='Codigo_Estudiante', color='Descripcion_Materia', title="Alumnos en Riesgo por Asignatura")
    st.plotly_chart(fig, use_container_width=True)

# 3. Filtro por periodo, nivel, asignatura y todos los paralelos
elif asignatura_sel != "Todos":
    st.subheader(f"Detalle de Estudiantes - {asignatura_sel}")
    # Mostrar tabla detallada ordenada
    columnas_ver = ['Descripcion_Periodo', 'Descripcion_Nivel', 'Descripcion_Materia', 'Paralelo', 'Codigo_Estudiante', 'Nota1']
    bajo_rend_ordenado = bajo_rend[columnas_ver].sort_values(by=['Paralelo', 'Nota1'])
    st.dataframe(bajo_rend_ordenado, use_container_width=True)

# 4. Filtro por periodo, nivel, asignatura y paralelo
elif paralelo_sel != "Todos":

    st.subheader(f"Paralelo: {paralelo_sel}")
    # Gráfico por Paralelos
    resumen = bajo_rend.groupby('Paralelo')['Codigo_Estudiante'].count().reset_index()
    st.plotly_chart(px.bar(resumen, x='Paralelo', y='Codigo_Estudiante', title="Estudiantes en Riesgo por Paralelo"))
# 5. Ninguna de las otras opciones
else:
    # --- VISTA FINAL: LISTA DE ESTUDIANTES ---
     
    
    st.markdown(f"Análisis para **{asignatura_sel}** - Paralelo **{paralelo_sel}**")

    # Métricas rápidas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Estudiantes Matriculados", obtener_total_estudiantes_matriculados(df_temp))
    col2.metric("En Riesgo", obtener_total_estudiantes_bajo_rendimiento(df_temp), delta=obtener_total_estudiantes_bajo_rendimiento(df_temp), delta_color="inverse")
    col3.metric("Promedio Grupal", round(df_temp['Nota1'].mean(), 2))

    # Layout de gráficos
    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        
        critico_nivel = obtener_puntos_criticos(df_temp, 1)
        critico_materia = obtener_puntos_criticos(df_temp, 2)
        critico_nivel1 = critico_nivel[['Descripcion_Periodo', 'Descripcion_Nivel','Porcentaje_Bajo_Rendimiento']]
        critico_materia1 =critico_materia[['Descripcion_Periodo', 'Descripcion_Materia','Porcentaje_Bajo_Rendimiento']]
        st.subheader("Niveles con mayor bajo rendimiento por periodo")
        critico_nivel1
        st.subheader("Materias con mayor bajo rendimiento por periodo")  
        critico_materia1
    with col_der:
         st.subheader("Distribución del Rendimiento Académico")
        
        fig_hist = px.histogram(
        df_temp, 
        x="Nota1", 
        color="Descripcion_Periodo", 
        marginal="rug", # Añade una pequeña densidad debajo
        title="Frecuencia de Calificaciones por Periodo",
        barmode="overlay" # Superpone los periodos para comparar
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    
     
    
    # BOTÓN DE DESCARGA
    columnas_deseadas = [
    'Descripcion_Periodo', 
    'Descripcion_Nivel', 
    'Id_Materia', 
    'Paralelo', 
    'Codigo_Estudiante', 
    'Nota1'
    ]

    # 2. Filtramos el DataFrame (asegúrate de que los nombres coincidan con tu Excel original)
    # Si tus columnas tienen nombres distintos, solo cámbialos en la lista de arriba.
    # st.write("Columnas detectadas en el archivo:", bajo_rendimiento.columns.tolist())
    reporte_final = bajo_rend[columnas_deseadas]

    # 3. Lógica para exportar a Excel
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        reporte_final.to_excel(writer, index=False, sheet_name='Reporte_Notas')

    buffer.seek(0)

    # 4. Botón de descarga
    st.download_button(
        label="📥 Descargar Reporte de Excel",
        data=buffer,
        file_name=f"reporte_{asignatura_sel}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
