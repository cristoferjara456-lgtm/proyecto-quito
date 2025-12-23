import streamlit as st
import folium
from streamlit_folium import st_folium
import osmnx as ox
import networkx as nx

st.set_page_config(page_title="Quito Maps Pro", layout="wide")

# 1. BASE DE DATOS COMPLETA (Verificada)
LUGARES = {
    "Museo de la Ciudad": [-0.2238, -78.5138],
    "Alberto Mena Caamaño (Museo de Cera)": [-0.2205, -78.5118],
    "Casa del Alabado Pre‑Columbian Art": [-0.2215, -78.5152],
    "Museo Camilo Egas": [-0.2185, -78.5085],
    "Museo Casa de Sucre": [-0.2219, -78.5111],
    "Museum Of Maria Augusta Urrutia": [-0.2212, -78.5115],
    "Museo Franciscano Fray Pedro Gocial": [-0.2210, -78.5155],
    "Museo del Pasillo": [-0.2225, -78.5130],
    "Museo de la Moneda": [-0.2208, -78.5110],
    "Museo de Arte Colonial": [-0.2195, -78.5105],
    "Manuela Sáenz Museum": [-0.2230, -78.5125],
    "Centro Cultural Metropolitano": [-0.2204, -78.5116],
    "Contemporary Art Center (CAC)": [-0.2165, -78.5042],
    "Museo Antiguo Banco Central": [-0.2218, -78.5120],
    "Plaza de la Independencia (Grande)": [-0.2202, -78.5123],
    "Plaza de San Francisco": [-0.2210, -78.5147],
    "Plaza de Santo Domingo": [-0.2235, -78.5120],
    "Plaza del Teatro (Plaza Sucre)": [-0.2188, -78.5100],
    "Plaza de San Blas": [-0.2168, -78.5065],
    "Plaza de Santa Clara": [-0.2245, -78.5140],
    "Plaza de San Agustín": [-0.2208, -78.5100],
    "Plaza de La Merced": [-0.2195, -78.5135],
    "Plaza del Carmen Alto": [-0.2235, -78.5145],
    "Plaza del Hospital San Juan de Dios": [-0.2240, -78.5135],
    "Calle La Ronda": [-0.2248, -78.5128],
    "Basílica del Voto Nacional": [-0.2146, -78.5074]
}

@st.cache_resource
def obtener_grafo():
    # Descarga la red vial para cálculos de ruta
    return ox.graph_from_address("Plaza de la Independencia, Quito", dist=2500, network_type='all')

G = obtener_grafo()

# ESTADOS DE SESIÓN
if 'punto_a' not in st.session_state: st.session_state.punto_a = None
if 'punto_b' not in st.session_state: st.session_state.punto_b = None

st.title("📍 Guía Maestra: Centro Histórico de Quito")

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("🔍 Buscador")
    opciones = ["-- Tocar en Mapa --"] + sorted(LUGARES.keys())
    
    # Buscadores sincronizados
    inicio = st.selectbox("Punto de Inicio:", opciones, key="busq_inicio")
    destino = st.selectbox("Punto de Destino:", opciones, key="busq_destino")
    
    # Actualizar puntos si se usa el buscador
    if inicio != "-- Tocar en Mapa --":
        st.session_state.punto_a = LUGARES[inicio]
    if destino != "-- Tocar en Mapa --":
        st.session_state.punto_b = LUGARES[destino]

    if st.button("🗑️ Reiniciar Mapa"):
        st.session_state.punto_a = None
        st.session_state.punto_b = None
        st.rerun()

# CREAR MAPA BASE
m = folium.Map(location=[-0.2215, -78.5120], zoom_start=16)

# Marcadores de todos los lugares (Puntos discretos para no saturar)
for nom, coord in LUGARES.items():
    folium.CircleMarker(coord, radius=3, color="#555", fill=True, popup=nom).add_to(m)

# MARCADORES GRANDES (Estilo Google Maps)
if st.session_state.punto_a:
    folium.Marker(
        st.session_state.punto_a, 
        icon=folium.Icon(color="blue", icon="info-sign", icon_size=(45, 45)),
        tooltip="Punto de Salida"
    ).add_to(m)

if st.session_state.punto_b:
    folium.Marker(
        st.session_state.punto_b, 
        icon=folium.Icon(color="red", icon="flag", icon_size=(45, 45)),
        tooltip="Destino"
    ).add_to(m)

# CÁLCULO DE RUTA REAL
if st.session_state.punto_a and st.session_state.punto_b:
    try:
        n1 = ox.nearest_nodes(G, st.session_state.punto_a[1], st.session_state.punto_a[0])
        n2 = ox.nearest_nodes(G, st.session_state.punto_b[1], st.session_state.punto_b[0])
        path = nx.shortest_path(G, n1, n2, weight='length')
        dist = nx.shortest_path_length(G, n1, n2, weight='length')
        
        # Línea de ruta azul Google
        puntos_ruta = [[G.nodes[n]['y'], G.nodes[n]['x']] for n in path]
        folium.PolyLine(puntos_ruta, color="#1a73e8", weight=7, opacity=0.85).add_to(m)
        
        with col1:
            st.success(f"**Distancia:** {dist/1000:.2f} km")
            st.info(f"**Tiempo:** {int((dist/1000)/4.5*60)} min")
    except:
        st.error("Error al trazar la ruta entre estos puntos.")

with col2:
    # Renderizado del mapa interactivo
    salida = st_folium(m, width="100%", height=750, key="quito_maps_final")
    
    # Captura de clics si no se usó el buscador
    if salida.get("last_clicked"):
        clic = [salida["last_clicked"]['lat'], salida["last_clicked"]['lng']]
        if st.session_state.punto_a is None:
            st.session_state.punto_a = clic
            st.rerun()
        elif st.session_state.punto_b is None and clic != st.session_state.punto_a:
            st.session_state.punto_b = clic
            st.rerun()
