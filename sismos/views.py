import base64
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import geopandas as gpd
from django.shortcuts import render

# Cargar el dataset y procesar las fechas de forma global
df = pd.read_csv('data/earthquakes_1900_2026.csv', usecols=['time', 'latitude', 'longitude', 'depth', 'mag', 'place', 'mag_category', 'type'])
df['time'] = pd.to_datetime(df['time'], format='ISO8601', errors='coerce')
df['year'] = df['time'].dt.year # Extraer el año globalmente para agilizar el gráfico 2

def index(request):
    return render(request, "sismos/index.html")

# Listas (Tablas HTML)

# Mayores Sismos Globales (Se eliminan los NaT antes de filtrar para evitar "Fecha Desconocida")
def listado1(request):
    top_df = df.dropna(subset=['time']).nlargest(10, 'mag').copy()
    top_df['time'] = top_df['time'].dt.strftime('%Y-%m-%d %H:%M')
    top_df['depth'] = top_df['depth'].round(1)
    
    explicacion = "Top 10 sismos de mayor magnitud registrados históricamente a nivel global, excluyendo registros con fechas incompletas."
    return render(request, "sismos/listado.html", {"datos": top_df.to_dict('records'), "explicacion": explicacion, "titulo": "Mayores Sismos Históricos"})

# Mayores Sismos en Chile
def listado2(request):
    chile_df = df[df['place'].str.contains('Chile', case=False, na=False)].dropna(subset=['time'])
    top_chile = chile_df.nlargest(10, 'mag').copy()
    top_chile['time'] = top_chile['time'].dt.strftime('%Y-%m-%d %H:%M')
    top_chile['depth'] = top_chile['depth'].round(1)
    
    explicacion = "Los 10 eventos sísmicos de mayor magnitud registrados en territorio chileno, evidenciando la alta liberación de energía en la zona de subducción de la Placa de Nazca."
    return render(request, "sismos/listado.html", {"datos": top_chile.to_dict('records'), "explicacion": explicacion, "titulo": "Sismos de Mayor Magnitud en Chile"})

# Mayores Eventos Antrópicos (Explosiones)
def listado3(request):
    eventos_naturales = ['earthquake', 'Ice Quake', 'volcanic eruption', 'landSlide', 'Rock Slide']
    antropicos_df = df[~df['type'].isin(eventos_naturales)].dropna(subset=['time'])
    top_antropicos = antropicos_df.nlargest(10, 'mag').copy()
    top_antropicos['time'] = top_antropicos['time'].dt.strftime('%Y-%m-%d %H:%M')
    top_antropicos['depth'] = top_antropicos['depth'].round(1)
    
    explicacion = "Detalle de los 10 principales eventos sísmicos de origen artificial (pruebas nucleares y explosiones mineras), caracterizados por ocurrir a niveles muy superficiales."
    return render(request, "sismos/listado.html", {"datos": top_antropicos.to_dict('records'), "explicacion": explicacion, "titulo": "Mayores Eventos Antrópicos"})

# Vistas graficos

# Grafico 1: Cantidad de eventos sismicos artificiales
def grafico1(request):
    eventos_naturales = ['earthquake', 'Ice Quake', 'volcanic eruption', 'landSlide', 'Rock Slide']
    df_antropico = df[~df['type'].isin(eventos_naturales)]
    top_tipos = df_antropico['type'].value_counts().head(5)

    fig, eje = plt.subplots(figsize=(10, 5.5), dpi=120)
    # Paleta Okabe-Ito distingue las categorías mediante colores diferentes y accesibles al daltonismo
    colores = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#D55E00'][:len(top_tipos)]
    barras = eje.barh(top_tipos.index.astype(str), top_tipos.values, color=colores, height=0.68)
    eje.set_title("Principales Eventos Sísmicos Artificiales (1900-2026)", fontsize=15, fontweight='bold', loc='left', pad=16)
    eje.set_xlabel("Cantidad Registrada", fontsize=11, labelpad=8)
    eje.set_ylabel("Tipo de Evento", fontsize=11, labelpad=8)
    eje.bar_label(barras, padding=5, fontsize=10, fmt='%.0f')
    eje.set_xlim(0, top_tipos.max() * 1.15 if len(top_tipos) and top_tipos.max() > 0 else 1)
    eje.invert_yaxis()
    eje.grid(axis='x', linestyle='--', linewidth=0.7, alpha=0.5)
    eje.set_axisbelow(True)
    eje.spines[['top', 'right', 'left']].set_visible(False)
    eje.tick_params(axis='y', length=0, labelsize=10)
    eje.tick_params(axis='x', labelsize=9)
    fig.tight_layout()

    grafico = _guardar_grafico(fig)
    explicacion = "Gráfico de barras horizontales que muestra los 5 principales tipos de eventos sísmicos de origen antrópico o humano (no naturales)."
    return render(request, "sismos/grafico.html", {"grafico": grafico, "explicacion": explicacion, "titulo": "Eventos Antrópicos"})

# Grafico 2: Cantidad de sismos fuertes vs leves a lo largo de los años
def grafico2(request):
    df_g2 = df.dropna(subset=['year', 'mag']).copy()
    df_g2['rango_mag'] = np.where(df_g2['mag'] < 5.0, 'Menor a 5.0', 'Mayor o igual a 5.0')
    evolucion = df_g2.groupby(['year', 'rango_mag']).size().unstack(fill_value=0)

    fig, eje = plt.subplots(figsize=(10, 5.5), dpi=120)
    if 'Menor a 5.0' in evolucion.columns:
        eje.plot(evolucion.index, evolucion['Menor a 5.0'], label='Magnitud < 5.0', color='#0072B2', linewidth=2.5, linestyle='-', zorder=2)
    if 'Mayor o igual a 5.0' in evolucion.columns:
        eje.plot(evolucion.index, evolucion['Mayor o igual a 5.0'], label='Magnitud ≥ 5.0', color='#D62728', linewidth=2.5, linestyle='--', zorder=3)

    eje.set_title("Sismos Fuertes vs Leves (1900-2026)", fontsize=15, fontweight='bold', loc='left', pad=16)
    eje.set_xlabel("Año", fontsize=11, labelpad=8)
    eje.set_ylabel("Cantidad Registrada", fontsize=11, labelpad=8)
    eje.legend(frameon=False, fontsize=10, loc='upper left')
    eje.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.5)
    eje.set_axisbelow(True)
    eje.spines[['top', 'right', 'left']].set_visible(False)
    eje.tick_params(axis='y', length=0, labelsize=9)
    eje.tick_params(axis='x', labelsize=9)
    eje.xaxis.set_major_locator(plt.MaxNLocator(nbins=8, integer=True))
    fig.tight_layout()

    grafico = _guardar_grafico(fig)
    explicacion = "Gráfico de líneas que compara la evolución anual de los sismos con magnitud inferior a 5.0 y los de magnitud igual o superior a 5.0. El aumento de las detecciones puede relacionarse con mejoras en las redes de monitoreo sísmico."
    return render(request, "sismos/grafico.html", {"grafico": grafico, "explicacion": explicacion, "titulo": "Sismos Fuertes vs Leves"})

# Grafico 3: Distribucion global de sismos (longitud, latitud)
def grafico3(request):
    datos = df.dropna(subset=['latitude', 'longitude', 'mag'])
    muestra = datos.sample(n=min(125000, len(datos)), random_state=42)

    # Grafico 1: Versión sin mapa (Solo dispersión)
    # Dimension de (10, 5) que es exactamente relación 2:1
    fig1, eje1 = plt.subplots(figsize=(10, 5), dpi=120)
    scatter1 = eje1.scatter(muestra['longitude'], muestra['latitude'], c=muestra['mag'], cmap='turbo', norm=plt.Normalize(vmin=muestra['mag'].quantile(0.01), vmax=muestra['mag'].quantile(0.97)), s=3, alpha=0.7, edgecolors='none', rasterized=True)
    
    eje1.set_title("Distribución Global de Sismos (1900-2026)", fontsize=15, fontweight='bold', loc='left', pad=16)
    eje1.set_xlabel("Longitud (°)", fontsize=11, labelpad=8)
    eje1.set_ylabel("Latitud (°)", fontsize=11, labelpad=8)
    eje1.set_xlim(-180, 180)
    eje1.set_ylim(-90, 90)
    eje1.set_xticks(np.arange(-180, 181, 60))
    eje1.set_yticks(np.arange(-90, 91, 30))
    
    eje1.set_aspect('equal')
    
    eje1.grid(axis='both', linestyle='--', linewidth=0.7, alpha=0.5)
    eje1.set_axisbelow(True)
    eje1.spines[['top', 'right', 'bottom', 'left']].set_visible(True)
    eje1.tick_params(axis='both', labelsize=9)
    colorbar1 = fig1.colorbar(scatter1, ax=eje1, pad=0.03, fraction=0.035)
    colorbar1.set_label("Magnitud", fontsize=11, labelpad=8)
    colorbar1.ax.tick_params(labelsize=9)
    fig1.tight_layout(rect=[0, 0, 0.96, 1])

    grafico_sin_mapa = _guardar_grafico(fig1)

    # Grafico 2: Versión con Mapa Base (Geopandas)
    # Misma dimension (10, 5)
    fig2, eje2 = plt.subplots(figsize=(10, 5), dpi=120)
    
    url_paises = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    mapa_mundo = gpd.read_file(url_paises)
    mapa_mundo.plot(ax=eje2, color='dimgray', edgecolor='white', linewidth=0.5, zorder=0)

    scatter2 = eje2.scatter(muestra['longitude'], muestra['latitude'], c=muestra['mag'], cmap='turbo', norm=plt.Normalize(vmin=muestra['mag'].quantile(0.01), vmax=muestra['mag'].quantile(0.97)), s=3, alpha=0.7, edgecolors='none', rasterized=True, zorder=1)
    
    eje2.set_title("Distribución Global de Sismos (1900-2026)", fontsize=15, fontweight='bold', loc='left', pad=16)
    eje2.set_xlabel("Longitud (°)", fontsize=11, labelpad=8)
    eje2.set_ylabel("Latitud (°)", fontsize=11, labelpad=8)
    eje2.set_xlim(-180, 180)
    eje2.set_ylim(-90, 90)
    eje2.set_xticks(np.arange(-180, 181, 60))
    eje2.set_yticks(np.arange(-90, 91, 30))
    
    # Forzar proporcion del mapa
    eje2.set_aspect('equal')

    eje2.grid(axis='both', linestyle='--', linewidth=0.7, alpha=0.5)
    eje2.set_axisbelow(True)
    eje2.tick_params(axis='both', labelsize=9)
    colorbar2 = fig2.colorbar(scatter2, ax=eje2, pad=0.03, fraction=0.035)
    colorbar2.set_label("Magnitud", fontsize=11, labelpad=8)
    colorbar2.ax.tick_params(labelsize=9)
    fig2.tight_layout(rect=[0, 0, 0.96, 1])

    grafico_con_mapa = _guardar_grafico(fig2)

    explicacion = "Gráfico de dispersión que muestra una muestra de hasta 125.000 eventos sísmicos. La posición representa las coordenadas geográficas y el color indica la magnitud registrada. Se puede alternar la vista del mapa para observar los límites de las placas."
    
    return render(request, "sismos/grafico.html", {
        "grafico": grafico_sin_mapa, 
        "grafico_mapa": grafico_con_mapa,
        "es_grafico_interactivo": True,
        "explicacion": explicacion, 
        "titulo": "Distribución Global de Sismos"
    })

# Guardar graficos como texto base64
def _guardar_grafico(figura):
    buffer = BytesIO()
    figura.savefig(buffer, format="png", dpi=120)
    plt.close(figura)
    buffer.seek(0)
    grafico = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return grafico