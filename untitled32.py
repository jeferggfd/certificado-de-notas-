import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard interactivo de notas", page_icon="📊", layout="wide")

# --- CARGA DE DATOS OPTIMIZADA ---
@st.cache_data
def cargar_datos():
  # Lee el archivo CSV separado por punto y coma
  return pd.read_csv("estudiantes_notas.csv", sep=";")

df = cargar_datos()

# ==========================================
# 1. BARRA LATERAL (SIDEBAR) - DATOS Y FILTROS
# ==========================================
st.sidebar.title("Datos y filtros")
st.sidebar.text("Carga el archivo de estudiantes")

# Componente para cargar archivo CSV personalizado (opcional)
archivo_subido = st.sidebar.file_uploader(
    "estudias...notas.csv", type=["csv"]
)
if archivo_subido is not None:
  df = pd.read_csv(archivo_subido, sep=";")

st.sidebar.markdown("---")

# Filtro 1: Sexo (Multiselect)
sexos_disponibles = df["sexo"].unique()
sexos_seleccionados = st.sidebar.multiselect(
    "Sexo", options=sexos_disponibles, default=list(sexos_disponibles)
)

# Filtro 2: Sección (Selectbox)
secciones = ["Todas"] + list(df["seccion"].unique())
seccion_seleccionada = st.sidebar.selectbox("Sección", options=secciones)

# Filtro 3: Rango del promedio (Slider de intervalo)
rango_promedio = st.sidebar.slider(
    "Rango del promedio", min_value=1.0, max_value=7.0, value=(1.0, 7.0)
)

# Filtro 4: Asistencia mínima (Number input)
asistencia_minima = st.sidebar.number_input(
    "Asistencia mínima (%)", min_value=0, max_value=100, value=0
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Los filtros se combinan. Quitar ambos sexos deja la selección vacía."
)

# ==========================================
# APLICACIÓN DE FILTROS AL DATAFRAME
# ==========================================
# Filtrar por sexo
filtrado = df[df["sexo"].isin(sexos_seleccionados)]

# Filtrar por sección si no es "Todas"
if seccion_seleccionada != "Todas":
  filtrado = filtrado[filtrado["seccion"] == seccion_seleccionada]

# Filtrar por rango de promedio
filtrado = filtrado[
    (filtrado["promedio"] >= rango_promedio[0])
    & (filtrado["promedio"] <= rango_promedio[1])
]

# Filtrar por asistencia mínima
filtrado = filtrado[filtrado["asistencia"] >= asistencia_minima]


# ==========================================
# 2. ÁREA PRINCIPAL (MAIN)
# ==========================================
st.title("Dashboard interactivo de notas")
st.markdown(
    "Explora los resultados de un curso combinando filtros. Promedio: 50%"
    " de cada evaluación. Aprobación del ejercicio: promedio mayor o igual a"
    " 4,0. Datos ficticios."
)
st.markdown(
    f"*Filtros activos:* Sexo: {', '.join(sexos_seleccionados) if sexos_seleccionados else 'Ninguno'} | Sección: {seccion_seleccionada} | Promedio: {rango_promedio[0]} a {rango_promedio[1]} | Asistencia mínima: {asistencia_minima}%"
)

st.markdown("---")

# --- TARJETAS DE MÉTRICAS (KPIs) ---
col1, col2, col3 = st.columns(3)

total_estudiantes = len(filtrado)
promedio_general = (
    filtrado["promedio"].mean() if total_estudiantes > 0 else 0.0
)
# Calculamos porcentaje de aprobación (promedio >= 4.0)
aprobados = (
    len(filtrado[filtrado["promedio"] >= 4.0]) if total_estudiantes > 0 else 0
)
porcentaje_aprobacion = (
    (aprobados / total_estudiantes) * 100 if total_estudiantes > 0 else 0.0
)

col1.metric("Estudiantes seleccionados", f"{total_estudiantes}")
col2.metric("Promedio general", f"{promedio_general:.2f}")
col3.metric("Aprobación", f"{porcentaje_aprobacion:.2f} %")

st.markdown("---")

# --- VISUALIZACIÓN Y OPCIONES DE GRÁFICO ---
st.subheader("Visualización de notas")

# Selector de tipo de gráfico
tipo_grafico = st.radio(
    "Gráfico",
    options=["Notas por estudiante", "Promedio por sección"],
    horizontal=True,
)

# Casilla de verificación para mostrar/ocultar tabla
mostrar_tabla = st.checkbox("Mostrar tabla", value=True)

# Validación si el filtro no arroja datos
if filtrado.empty:
  st.warning(
      "No hay estudiantes que cumplan con los filtros seleccionados. Ajusta"
      " los criterios en la barra lateral."
  )
else:
  # Creamos dos columnas en el área principal si el usuario quiere ver la tabla al lado del gráfico
  if mostrar_tabla:
    col_grafico, col_tabla = st.columns([1.2, 1])
  else:
    col_grafico = st.container()

  with col_grafico:
    fig, ax = plt.subplots(figsize=(7, 4))

    if tipo_grafico == "Notas por estudiante":
      # Gráfico de barras de notas individuales
      ax.bar(filtrado["estudiante"], filtrado["promedio"], color="#1f77b4")
      ax.set_ylabel("Promedio de notas")
      ax.set_xlabel("Estudiante")
      plt.xticks(rotation=45, ha="right")
      # Línea horizontal de aprobación (Nota 4.0)
      ax.axhline(
          y=4.0, color="red", linestyle="--", label="Aprobación: 4,0"
      )
      ax.legend(loc="upper right", fontsize=8)
      ax.set_title("Promedio por estudiante")

    else:
      # Gráfico de barras agrupado por sección
      prom_seccion = filtrado.groupby("seccion")["promedio"].mean()
      ax.bar(prom_seccion.index, prom_seccion.values, color="#ff7f0e")
      ax.set_ylabel("Promedio de sección")
      ax.set_xlabel("Sección")
      ax.axhline(
          y=4.0, color="red", linestyle="--", label="Aprobación: 4,0"
      )
      ax.legend(loc="upper right", fontsize=8)
      ax.set_title("Promedio por sección")

    ax.grid(axis="y", linestyle="--", alpha=0.6)
    st.pyplot(fig)

  if mostrar_tabla:
    with col_tabla:
      st.subheader("Estudiantes seleccionados")
      # Mostramos la tabla interactiva de Pandas
      st.dataframe(filtrado, use_container_width=True)

# --- BOTÓN DE DESCARGA DE DATOS FILTRADOS ---
st.markdown("---")
csv_data = filtrado.to_csv(index=False, sep=";").encode("utf-8")
st.download_button(
    label="📥 Descargar selección CSV",
    data=csv_data,
    file_name="estudiantes_filtrados.csv",
    mime="text/csv",
)

st.caption(
    f"Mostrando {total_estudiantes} de {len(df)} estudiantes. La asistencia"
    " solo se usa como filtro; la aprobación depende del promedio."
)
