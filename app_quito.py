import streamlit as st
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# --- 1. Configuración de la página de Streamlit ---
st.set_page_config(page_title="Guía del Centro Histórico de Quito", layout="wide")
st.title("🗺️ Navega por el Centro Histórico: Museos y Sitios")
st.sidebar.header("Elige tu Ruta")

# 2. Base de datos completa de tus Nodos (Museos y Sitios con coordenadas Lat/Lon)
puntos_interes = {
    "CAC (Atras Mejia)": (-0.2154, -78.5068),
    "Colegio Mejia": (-0.2158, -78.5080),
    "Basilica": (-0.2179, -78.5072),
    "Plaza del Teatro": (-0.2195, -78.5077),
    "Palacio de Carondelet": (-0.2199, -78.5121),
    "Plaza Grande / Catedral": (-0.2201, -78.5111),
    "Casa de Sucre": (-0.2215, -78.5089),
    "La Compania": (-0.2215, -78.5122),
    "San Francisco": (-0.2216, -78.5156),
    "Casa del Alabado": (-0.2223, -78.5165),
    "Museo de la Ciudad": (-0.2228, -78.5132),
    "Carmen Alto": (-0.2232, -78.5125),
    "Santo Domingo": (-0.2234, -78.5096),
    "La Ronda": (-0.2239, -78.5118),
    "El Panecillo": (-0.2289, -78.5186)
}

# --- 3. Widgets de la Interfaz (Menús desplegables para origen y destino) ---
# Se muestran en la barra lateral izquierda
origen_nombre = st.sidebar.selectbox("Desde:", list(puntos_interes.keys()))
destino_nombre = st.sidebar.selectbox("Hasta:", list(puntos_interes.keys()))

# Botón para activar el cálculo
if st.sidebar.button("🚗 Buscar Ruta"):
    if origen_nombre == destino_nombre:
        st.warning("El origen y el destino no pueden ser el mismo. Por favor, elige diferentes.")
    else:
        # Mensaje de carga mientras se procesa
        with st.spinner("Cargando mapa y calculando ruta... esto puede tardar unos segundos."):
            # 4. Descargar el grafo del Centro Histórico (igual que en el mapa anterior)
            # Usamos un punto central y una distancia para asegurar una cobertura amplia
            centro_lat, centro_lon = -0.2201, -78.5121 # Plaza Grande
            distancia = 1200 # Metros a la redonda
            G = ox.graph_from_point((centro_lat, centro_lon), dist=distancia, network_type='walk')
            
            # 5. Encontrar los nodos más cercanos en la red vial para origen y destino
            # Las coordenadas de tus puntos son (Lat, Lon), pero ox.nearest_nodes espera (Lon, Lat)
            orig_lon, orig_lat = puntos_interes[origen_nombre][1], puntos_interes[origen_nombre][0]
            dest_lon, dest_lat = puntos_interes[destino_nombre][1], puntos_interes[destino_nombre][0]

            nodo_origen = ox.nearest_nodes(G, orig_lon, orig_lat)
            nodo_destino = ox.nearest_nodes(G, dest_lon, dest_lat)

            # 6. Calcular la ruta más corta usando el Algoritmo de Dijkstra
            # 'weight='length'' significa que busca la ruta con menor distancia física
            try:
                ruta_corta = nx.shortest_path(G, nodo_origen, nodo_destino, weight='length')
                
                # 7. Visualizar la ruta en el mapa
                fig, ax = ox.plot_graph_route(
                    G, ruta_corta, 
                    route_color='cyan',    # La ruta se verá en cian
                    route_linewidth=4, 
                    node_size=0,           # No mostrar los nodos de las calles
                    bgcolor='black',       # Fondo negro
                    edge_color='#555555',  # Calles en gris oscuro para que la ruta resalte
                    show=False, 
                    close=False,
                    figsize=(15, 15)
                )

                # 8. Superponer tus puntos de interés (para que el usuario los vea todos)
                for nombre, coords in puntos_interes.items():
                    lat, lon = coords
                    ax.scatter(lon, lat, c='#00ffff', s=60, zorder=5, edgecolor='white', linewidth=1)
                    # Resaltar el origen y destino con un color diferente
                    if nombre == origen_nombre:
                        ax.text(lon + 0.0001, lat + 0.0001, f"📍 {nombre} (Origen)", color='lightgreen', fontsize=9, fontweight='bold', zorder=7)
                    elif nombre == destino_nombre:
                        ax.text(lon + 0.0001, lat + 0.0001, f"🏁 {nombre} (Destino)", color='red', fontsize=9, fontweight='bold', zorder=7)
                    else:
                        ax.text(lon + 0.0001, lat + 0.0001, nombre, color='#ffff00', fontsize=8, fontweight='bold', zorder=6)


                st.write(f"### Ruta encontrada de: {origen_nombre} a {destino_nombre}")
                st.pyplot(fig) # Muestra la imagen generada por Matplotlib en la app
                st.success("¡Desplázate por el mapa de arriba para ver la ruta!")

            except nx.NetworkXNoPath:
                st.error("No se pudo encontrar una ruta entre los puntos seleccionados. Puede que estén en islas de red separadas.")
            except Exception as e:
                st.error(f"Ocurrió un error inesperado al calcular la ruta: {e}")
else:
    st.info("Selecciona un punto de inicio y un destino en la barra izquierda, luego haz clic en 'Buscar Ruta'.")

st.markdown("---")
st.markdown("Desarrollado con Python, OSMnx y Streamlit.")