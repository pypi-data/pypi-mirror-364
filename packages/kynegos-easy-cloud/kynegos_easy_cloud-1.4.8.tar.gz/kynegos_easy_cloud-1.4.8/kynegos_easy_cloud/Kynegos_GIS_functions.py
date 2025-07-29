import geopandas as gpd
import os
import pandas as pd


def test_geometry(gdf):
    """
    Verifica y analiza las geometrías de un GeoDataFrame dado. Realiza las siguientes comprobaciones:
    
    1. Geometrías inválidas.
    2. Geometrías con áreas extremadamente pequeñas.
    3. Geometrías auto-intersectantes.
    4. Tipos de geometrías en el GeoDataFrame.
    5. Cantidad de MultiPolygons.
    6. Coordenadas mínimas y máximas (extensión de las geometrías).
    
    Args:
        gdf (geopandas.GeoDataFrame): El GeoDataFrame que contiene las geometrías a verificar.
        
    Returns:
        None: Imprime los resultados de las verificaciones directamente.
    """
    
    # Verificar geometrías inválidas
    gdf_invalid = gdf[~gdf.is_valid]
    print(f"Geometrías inválidas: {len(gdf_invalid)}")
    
    # Verificar geometrías con áreas extremadamente pequeñas
    small_geometries = gdf[gdf['geometry'].area < 1e-10]
    print(f"Geometrías con áreas pequeñas: {len(small_geometries)}")
    
    # Verificar geometrías auto-intersectantes
    auto_intersecting = gdf[gdf['geometry'].apply(lambda geom: geom.is_valid and geom.is_simple is False)]
    print(f"Geometrías auto-intersectantes: {len(auto_intersecting)}")
    
    # Verificar los tipos de geometrías
    geometry_types = gdf['geometry'].geom_type.value_counts()
    print(f"Tipos de geometrías en el GeoDataFrame:\n{geometry_types}")
    
    # Verificar la cantidad de multipolígonos
    multipolygons = gdf[gdf['geometry'].geom_type == 'MultiPolygon']
    print(f"Cantidad de MultiPolygons: {len(multipolygons)}")
    
    # Revisar coordenadas mínimas y máximas (extensión)
    bounds = gdf.total_bounds
    print(f"Extensión de las coordenadas: {bounds}")

def explode_geometry_collection(geom):
    """
    Descompone una GeometryCollection en sus componentes si contiene geometrías de tipo 'Polygon' o 'MultiPolygon'.
    Si no es una GeometryCollection, devuelve la geometría tal cual.
    
    Args:
        geom (shapely.geometry): La geometría a verificar.
        
    Returns:
        list or shapely.geometry: Lista de polígonos/multipolígonos o la geometría original.
    """
    if geom.geom_type == 'GeometryCollection':
        # Nos quedamos solo con las partes que sean polígonos o multipolígonos
        return [part for part in geom if part.geom_type in ['Polygon', 'MultiPolygon']]
    else:
        return [geom]


def process_gdf_for_bigquery(gdf, projected_crs_epsg=25830, swap_xy = False):
    """
    Procesa un GeoDataFrame para hacerlo apto para subir a BigQuery.
    Esta función maneja transformaciones de CRS, asegurando que las geometrías estén en EPSG:4326.
    También valida y corrige las geometrías para evitar errores al subir.

    Args:
        - gdf (geopandas.GeoDataFrame): El GeoDataFrame de entrada a procesar.
        - projected_crs_epsg (int): El código EPSG a asignar si las coordenadas están en metros (por defecto es 3857).

    Returns:
        - geopandas.GeoDataFrame: El GeoDataFrame procesado listo para BigQuery. 

    """
    from shapely.validation import make_valid
    from shapely.ops import orient
    from shapely.ops import transform
    import geopandas as gpd
    from shapely.geometry import Point, LineString, Polygon, MultiPolygon, MultiLineString, MultiPoint, GeometryCollection

    # Función para intercambiar X e Y
    def swap_coordinates(geom):
        if geom is None:
            return None
        return transform(lambda x, y, z=None: (y, x) if z is None else (y, x, z), geom)

    def swap_coordinates(geom):
        if geom.is_empty:
            return geom
        elif geom.geom_type == 'Point':
            return Point(geom.y, geom.x)
        elif geom.geom_type == 'LineString':
            return LineString([(y, x) for x, y in geom.coords])
        elif geom.geom_type == 'Polygon':
            return Polygon([(y, x) for x, y in geom.exterior.coords])
        elif geom.geom_type.startswith('Multi'):  # Para manejar Multi geometrías
            return geom.__class__([swap_coordinates(part) for part in geom.geoms])
        elif geom.geom_type == 'GeometryCollection':
            return GeometryCollection([swap_coordinates(part) for part in geom.geoms])
        else:
            raise ValueError(f"Tipo de geometría {geom.geom_type} no soportado")

    gdf = gdf[gdf['geometry'].notnull()]
    # Filtrar geometrías inválidas o vacías

    gdf = gdf[
        ~gdf['geometry'].is_empty & 
        gdf['geometry'].apply(lambda x: x is not None)
    ]

    if swap_xy:
            
        # Aplicar la función a la columna 'geometry'
        gdf['geometry'] = gdf['geometry'].apply(swap_coordinates)

    # Verificar si el CRS está definido y si es geográfico
    if gdf.crs is None or not gdf.crs.is_geographic:
        # Obtener los límites de las coordenadas
        minx, miny, maxx, maxy = gdf.total_bounds

        # Verificar si las coordenadas están fuera del rango de grados
        if (minx < -180 or maxx > 180) or (miny < -90 or maxy > 90):
            # Asumir que está en un CRS proyectado y asignar el CRS especificado
            gdf.set_crs(f"EPSG:{projected_crs_epsg}", inplace=True)
            # Transformar a EPSG:4326
            gdf = gdf.to_crs("EPSG:4326")
        else:
            # Asignar EPSG:4326 si las coordenadas están en rango
            gdf.set_crs("EPSG:4326", inplace=True)
    else:
        # Si el CRS está definido y no es EPSG:4326, transformar
        if gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")


    # Asegurarse de que el CRS es EPSG:4326
    gdf = gdf.to_crs("EPSG:4326")

    # Orientar y validar geometrías
    gdf['geometry'] = gdf['geometry'].apply(lambda geom: orient(geom, sign=1.0))
    gdf['geometry'] = gdf['geometry'].apply(make_valid)

    return gdf


def descargar_wfs(filename_temp, wfs_url, request_type, version, output_format):
    """
    Descarga capas de un servicio WFS y guarda cada capa en un archivo GeoPackage.

    Args:
        filename_temp (str): Nombre base temporal del archivo a guardar.
        wfs_url (str): URL del servicio WFS.
        request_type (str): Tipo de solicitud para el WFS, generalmente 'GetFeature'.
        version (str): Versión del servicio WFS a utilizar.
        output_format (str): Formato de salida deseado para la respuesta WFS. Ejemplos incluyen:
            - 'text/xml; subtype=gml/3.2.1'
            - 'application/json'
            - 'text/xml; subtype=gml/2.1.2'
            - 'application/gml+xml; version=3.2'
            - 'GML2'

    Returns:
        None
        En la ruta dada para filename_temp guarda el Geopackage que tiene todas las capas dentro
    """
    from owslib.wfs import WebFeatureService
    import requests
    import geopandas as gpd
    from io import BytesIO

    wfs = WebFeatureService(url=wfs_url, version=version)

    for layer_name in wfs.contents:
        try:
            response = requests.get(wfs_url, params={
                'service': 'WFS',
                'version': version,
                'request': request_type,
                'typeNames': layer_name,
                'outputFormat': output_format,
            }, timeout=240)

            if response.status_code == 200:
                try:
                    gdf = gpd.read_file(BytesIO(response.content))
                    gdf.to_file(f"{filename_temp}.gpkg", layer=layer_name, driver="GPKG")
                except Exception as e:
                    print(f"Error al cargar la capa '{layer_name}': {e}")
            else:
                print(f"Error al obtener la capa '{layer_name}': {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"Tiempo de espera excedido para la capa '{layer_name}', saltando a la siguiente.")
        except requests.exceptions.ConnectionError as e:
            print(f"Error de conexión para la capa '{layer_name}', saltando a la siguiente: {e}")


def info_geopackage(ruta_gpkg):
    capas = gpd.io.file.fiona.listlayers(ruta_gpkg)
    tamano_mb = os.path.getsize(ruta_gpkg) / (1024 * 1024)  # Convertir a MB
    
    data = []
    
    for capa in capas:
        gdf = gpd.read_file(ruta_gpkg, layer=capa)
        num_registros = len(gdf)
        data.append([capa, num_registros])
    
    df = pd.DataFrame(data, columns=["Capa", "Registros"])
    df["Tamaño (MB)"] = round(tamano_mb, 2)
    
    return df



