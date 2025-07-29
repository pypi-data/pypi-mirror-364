import geopandas as gpd
import os
import gc
from . import Kynegos_functions as KYNEGOS_FUNCTIONS
from . import Kynegos_GIS_functions as KYNEGOS_GIS_FUNCTIONS

def create_big_query_geometry_table_from_bucket(
    bucket_name,
    folder_path,
    bigquery_dataset,
    bigquery_table,
    projected_crs_epsg=25830,
    swap_xy=False,
    mode="insert"
):
    """
    Descarga archivos de un bucket de Google Cloud Storage, los procesa con geopandas y los sube a una tabla de BigQuery.

    Args:
        bucket_name (str): Nombre del bucket de Google Cloud Storage donde están los archivos.
        folder_path (str): Ruta de la carpeta dentro del bucket desde donde se descargarán los archivos.
        bigquery_dataset (str): Nombre del dataset de BigQuery donde se insertarán los datos procesados.
        bigquery_table (str): Nombre de la tabla en BigQuery donde se subirá el GeoDataFrame.
        projected_crs_epsg (int): Código EPSG del CRS proyectado si las coordenadas están en metros (por defecto 25830).
        swap_xy (bool): Si es True, intercambia las coordenadas X e Y.
        mode (str): 'insert' para agregar datos o 'truncate' para reemplazar los datos existentes.

    Returns:
        None
    """
    print(f"Iniciando el proceso para el bucket '{bucket_name}' y carpeta '{folder_path}'.")

    archivos = KYNEGOS_FUNCTIONS.list_files_in_gcs_folder(bucket_name, folder_path)
    print(f"Archivos encontrados: {archivos}")

    for archivo in archivos:
        print(f"\nProcesando archivo: {archivo}")
        
        # Descargar el archivo en formato bytes
        file_bytes = KYNEGOS_FUNCTIONS.download_file_from_gcs(bucket_name, archivo, return_bytes=True)
        print(f"Archivo descargado: {archivo}")

        # Guardar temporalmente el archivo y obtener la ruta local
        local_path = KYNEGOS_FUNCTIONS.save_file_temporarily(file_bytes.getvalue())
        print(f"Archivo guardado temporalmente en: {local_path}")

        del file_bytes
        gc.collect()
        
        # Leer el archivo con geopandas
        gdf = gpd.read_file(local_path)
        print(f"GeoDataFrame creado, número de registros: {len(gdf)}")

        # Procesar el GeoDataFrame para BigQuery
        gdf = KYNEGOS_GIS_FUNCTIONS.process_gdf_for_bigquery(
            gdf,
            projected_crs_epsg=projected_crs_epsg,
            swap_xy=swap_xy
        )
        print("GeoDataFrame procesado para BigQuery.")

        # Insertar en BigQuery
        KYNEGOS_FUNCTIONS.insert_geometry_to_bigquery(
            gdf,
            bigquery_dataset,
            bigquery_table,
            swap_xy=swap_xy,
            mode=mode
        )
        print(f"GeoDataFrame insertado en BigQuery en {bigquery_dataset}.{bigquery_table}")

        # Eliminar el archivo local después de procesarlo
        os.remove(local_path)
        print(f"Archivo temporal eliminado: {local_path}")

        gc.collect()

    print("Proceso completado.")
