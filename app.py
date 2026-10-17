"""MVP web local de MoviManrique45."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st

from src.dashboard.datos import cargar_geojson, cargar_hechos, validar_cierre


st.set_page_config(page_title="MoviManrique45", page_icon="🚦", layout="wide")
RAIZ = Path(__file__).resolve().parent
NOMBRES = {
    "principal_50m": "Dentro del corredor (50 m)",
    "sensibilidad_borde": "Cerca del límite del corredor",
    "revision_territorial": "Ubicación por revisar",
    "resto_manrique": "Otros registros de Manrique",
}


@st.cache_data(show_spinner="Cargando la información del corredor...")
def obtener_datos() -> pd.DataFrame:
    datos = cargar_hechos()
    validar_cierre(datos)
    return datos


@st.cache_data
def obtener_geometrias() -> tuple[dict, dict]:
    return cargar_geojson("carrera45.geojson"), cargar_geojson("zonas_prioritarias.geojson")


@st.cache_data
def obtener_intervenciones() -> dict:
    """Lee la vista derivada del módulo sin alterar datos de origen."""
    ruta = RAIZ / "web" / "data" / "intervenciones.json"
    if not ruta.exists():
        return {"zonas": [], "catalogo_intervenciones": [], "limitaciones_modulo": []}
    return json.loads(ruta.read_text(encoding="utf-8"))


def filtrar(datos: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtre los datos")
    anios = st.sidebar.multiselect("Año", sorted(datos["anio"].unique()), default=sorted(datos["anio"].unique()))
    barrios = st.sidebar.multiselect("Barrio registrado", sorted(datos["barrio"].unique()), default=sorted(datos["barrio"].unique()))
    categorias = st.sidebar.multiselect("Ubicación frente al corredor", list(NOMBRES), default=list(NOMBRES), format_func=lambda x: NOMBRES[x])
    return datos.loc[datos["anio"].isin(anios) & datos["barrio"].isin(barrios) & datos["categoria_analisis"].isin(categorias)].copy()


def tarjetas(datos: pd.DataFrame) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Siniestros seleccionados", f"{len(datos):,}".replace(",", "."))
    c2.metric("Dentro del corredor (50 m)", f"{(datos.categoria_analisis == 'principal_50m').sum():,}".replace(",", "."))
    c3.metric("Casos cerca del límite", f"{(datos.categoria_analisis == 'sensibilidad_borde').sum():,}".replace(",", "."))
    c4.metric("Casos por revisar", f"{(datos.categoria_analisis == 'revision_territorial').sum():,}".replace(",", "."))


def grafico_anual(datos: pd.DataFrame, solo_principal: bool = False):
    base = datos.loc[datos.categoria_analisis.eq("principal_50m")] if solo_principal else datos
    resumen = base.groupby("anio", as_index=False).size().rename(columns={"size": "Registros"})
    return px.bar(resumen, x="anio", y="Registros", text="Registros", color_discrete_sequence=["#007C83" if solo_principal else "#172B4D"])


def grafico_categoria(datos: pd.DataFrame, columna: str, titulo: str):
    resumen = datos.groupby(columna, as_index=False).size().rename(columns={"size": "Registros"}).sort_values("Registros")
    return px.bar(resumen, x="Registros", y=columna, orientation="h", title=titulo, color_discrete_sequence=["#60738A"])


def geovisor(datos: pd.DataFrame, carrera: dict, zonas: dict) -> None:
    mostrar = datos.loc[datos.categoria_analisis.ne("resto_manrique")].copy()
    if mostrar.empty:
        st.info(
            "No hay registros para esta selección. Ajuste los filtros para volver a verlos en el mapa."
        )
        return
    mostrar["categoria_legible"] = mostrar["categoria_analisis"].map(NOMBRES)
    capas = [
        pdk.Layer("GeoJsonLayer", carrera, stroked=True, filled=False, get_line_color=[0, 124, 131], get_line_width=5, pickable=True),
        pdk.Layer("GeoJsonLayer", zonas, stroked=True, filled=True, get_line_color=[109, 76, 145], get_fill_color=[109, 76, 145, 45], get_line_width=2, pickable=True),
        pdk.Layer("ScatterplotLayer", mostrar, get_position="[longitud, latitud]", get_fill_color=[156, 61, 88], get_radius=9, radius_min_pixels=3, pickable=True),
    ]
    view = pdk.ViewState(latitude=float(mostrar.latitud.mean()), longitude=float(mostrar.longitud.mean()), zoom=13.8, pitch=0)
    tooltip = {"text": "Registro {evento_id}\n{categoria_legible}\n{clase_siniestro} | {gravedad_siniestro}"}
    st.pydeck_chart(pdk.Deck(layers=capas, initial_view_state=view, tooltip=tooltip))
    st.caption("El mapa muestra registros históricos cerca del eje. Las 12 zonas identificadas son exploratorias y no prueban riesgo ni causalidad.")


def pagina_intervenciones(intervenciones: dict, zonas_geojson: dict) -> None:
    """Presenta fichas exploratorias; no aprueba ni ejecuta intervenciones."""
    st.subheader("Posibles soluciones en la Carrera 45")
    st.caption("Las 12 zonas ayudan a organizar la revisión de campo. Las medidas son opciones para evaluar, no obras aprobadas.")
    fichas = sorted(
        intervenciones.get("zonas", []),
        key=lambda ficha: ficha["comparacion_exploratoria"]["orden_por_registros_historicos"],
    )
    if not fichas:
        st.warning("No se pudo cargar la información de las zonas. Ejecute scripts/iniciar_demo.ps1 para regenerarla.")
        return

    por_id = {ficha["zona_id"]: ficha for ficha in fichas}
    zona_id = st.selectbox(
        "Zona identificada",
        list(por_id),
        format_func=lambda valor: f"{valor} · {por_id[valor]['diagnostico_historico']['registros_historicos']} registros",
    )
    ficha = por_id[zona_id]
    historico = ficha["diagnostico_historico"]
    evidencia = ficha["evidencia_geoespacial"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Registros históricos", f"{historico['registros_historicos']:,}".replace(",", "."))
    c2.metric("Dentro del corredor (50 m)", f"{historico['corredor_estricto_50m']:,}".replace(",", "."))
    c3.metric("Estado de revisión", ficha["estado_evaluacion"])
    st.info(ficha["justificacion"])

    seleccionada = {
        "type": "FeatureCollection",
        "features": [feature for feature in zonas_geojson.get("features", []) if str(feature.get("properties", {}).get("zona_id")) == zona_id],
    }
    if seleccionada["features"]:
        capa = pdk.Layer("GeoJsonLayer", seleccionada, stroked=True, filled=True, get_line_color=[37, 99, 235], get_fill_color=[37, 99, 235, 90], get_line_width=5, pickable=True)
        centro = ficha["ubicacion"]["centroide_representativo_wgs84"]
        st.pydeck_chart(pdk.Deck(layers=[capa], initial_view_state=pdk.ViewState(latitude=centro["latitud"], longitude=centro["longitud"], zoom=16, pitch=0)))

    izquierda, derecha = st.columns(2)
    izquierda.markdown("#### ¿Qué encontramos?")
    izquierda.dataframe(pd.DataFrame(historico["por_gravedad"]), use_container_width=True, hide_index=True)
    izquierda.dataframe(pd.DataFrame(historico["por_tipo"]), use_container_width=True, hide_index=True)
    derecha.markdown("#### Relación con el eje vial")
    segmentos = evidencia["segmentos_eje_intersectados_objectid"]
    derecha.write("Tramos del eje que pasan por esta zona:", ", ".join(map(str, segmentos)) if segmentos else "sin intersección geométrica con el eje exportado")
    derecha.caption(evidencia["mensaje_segmento"])
    derecha.markdown("#### Qué revisar en campo")
    for condicion in ficha["condiciones_por_verificar"]:
        derecha.write(f"- {condicion}")

    catalogo = {medida["id"]: medida for medida in intervenciones["catalogo_intervenciones"]}
    st.markdown("#### Posibles soluciones")
    for medida_id in ficha["intervenciones_candidatas"]:
        medida = catalogo[medida_id]
        with st.expander(medida["nombre"]):
            st.write(medida["descripcion"])
            st.caption(f"Qué se espera mejorar: {medida['beneficio_hipotesis']}")
            st.caption(f"Qué habría que verificar: {medida['condiciones_necesarias']}")
            st.caption(f"Quién debe evaluarlo: {medida['entidad_evaluadora']}")
    st.warning(f"Costo por definir: {ficha['costos_preliminares']['estado']}. {ficha['costos_preliminares']['nota']}")
    st.caption("Qué falta por revisar: " + " ".join(ficha["limitaciones"]))


def main() -> None:
    st.markdown("<style>.stApp{background:#F1F5F9}.stButton>button{border-radius:8px}.stMetric{background:#FFFFFF;border:1px solid #CBD5E1;border-radius:12px;padding:12px}</style>", unsafe_allow_html=True)
    datos = obtener_datos()
    try:
        carrera, zonas = obtener_geometrias()
    except FileNotFoundError:
        carrera = zonas = {"type": "FeatureCollection", "features": []}
        st.warning("No se pudo cargar el mapa de referencia; se muestran los resultados en tabla.")
    st.title("MoviManrique45")
    st.caption("Información histórica para entender los siniestros viales cerca de la Carrera 45, en la Comuna 3 - Manrique (2019–2025).")
    pagina = st.radio("Sección", ["¿Qué encontramos?", "Carrera 45", "Geovisor", "Posibles soluciones", "Qué falta por revisar"], horizontal=True, label_visibility="collapsed")
    seleccion = filtrar(datos)
    tarjetas(seleccion)

    if pagina == "¿Qué encontramos?":
        a, b = st.columns(2)
        a.plotly_chart(grafico_anual(seleccion), use_container_width=True)
        b.plotly_chart(grafico_categoria(seleccion, "gravedad_siniestro", "Gravedad registrada"), use_container_width=True)
        st.plotly_chart(grafico_categoria(seleccion, "clase_siniestro", "Tipo de siniestro"), use_container_width=True)
    elif pagina == "Carrera 45":
        principal = seleccion.loc[seleccion.categoria_analisis.eq("principal_50m")]
        st.info("El indicador principal reúne los 604 registros dentro del corredor de 50 m. Los 40 casos cerca del límite se muestran aparte.")
        a, b = st.columns(2)
        a.plotly_chart(grafico_anual(seleccion, solo_principal=True), use_container_width=True)
        b.metric("Distancia típica al eje", f"{principal.distancia_carrera45_m.median():.2f} m" if len(principal) else "No disponible")
        c, d = st.columns(2)
        c.plotly_chart(grafico_categoria(principal, "gravedad_siniestro", "Gravedad registrada cerca del eje"), use_container_width=True)
        d.plotly_chart(grafico_categoria(principal, "clase_siniestro", "Tipo de siniestro cerca del eje"), use_container_width=True)
    elif pagina == "Geovisor":
        geovisor(seleccion, carrera, zonas)
        columnas = ["evento_id", "anio", "barrio", "clase_siniestro", "gravedad_siniestro", "categoria_analisis", "zona_id", "distancia_carrera45_m"]
        st.dataframe(seleccion[columnas], use_container_width=True, hide_index=True)
    elif pagina == "Posibles soluciones":
        pagina_intervenciones(obtener_intervenciones(), zonas)
    else:
        st.subheader("Cómo se construyó el análisis")
        st.write("Antes de mostrar los resultados, la aplicación comprueba los conteos y los identificadores validados del corredor. Así se mantiene la trazabilidad entre los datos y el mapa.")
        st.dataframe(seleccion.groupby("categoria_analisis", as_index=False).size().rename(columns={"size": "registros"}), use_container_width=True, hide_index=True)
        st.markdown("**Qué falta por revisar:** los datos describen registros históricos. Estar cerca del eje no prueba causalidad. Las 12 zonas son exploratorias, no tasas de riesgo. La ausencia de una categoría en este dataset no permite inferir fallecimientos.")


if __name__ == "__main__":
    main()
