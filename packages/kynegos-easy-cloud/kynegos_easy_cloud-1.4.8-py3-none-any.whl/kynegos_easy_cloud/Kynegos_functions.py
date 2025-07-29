import os
import pandas as pd
import pickle
import time


class DataFrameAlreadyExistsError(Exception):
    pass

class ModelAlreadyExistsError(Exception):
    pass

def setup_credentials():
    """
    Configura las credenciales para usar Google Cloud API.
    Utiliza la variable de entorno GOOGLE_APPLICATION_CREDENTIALS si está definida,
    de lo contrario, usa la autenticación predeterminada.
    """
    from google.auth import default, load_credentials_from_file
    if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        # Usa las credenciales del archivo JSON especificado en la variable de entorno
        credentials, project = load_credentials_from_file(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    else:
        # Usa la autenticación predeterminada (por ejemplo, en Colab Enterprise)
        credentials, project = default()
    
    return credentials, project

def get_bigquery_client():
    from google.cloud import bigquery
    credentials, project = setup_credentials()
    return bigquery.Client(credentials=credentials, project=project)

def get_storage_client():
    from google.cloud import storage
    credentials, project = setup_credentials()
    return storage.Client(credentials=credentials, project=project)

def get_aiplatform_client():
    from google.cloud import aiplatform
    credentials, project = setup_credentials()
    aiplatform.init(credentials=credentials, project=project)
    return aiplatform

def convert_to_valid_bq_string(string_to_clean: str) -> str:
    """
    Para una string dada la devuelve formateada, quitando caracteres no alfanuméricos, tildes, etc

    Args:
        - string to clean
    
    Returns:
        - cleanded string
    
    """
    import re
    cleaned_layer = re.sub(r'[^a-zA-Z0-9]', '_', layer)
    valid_bq_string = re.sub(r'_+', '_', cleaned_layer)
    return valid_bq_string.lower()

def upload_to_bigquery(df, dataset_id, table_name, mode='insert'):
    """
    Sube un DataFrame a una tabla de BigQuery.

    Args:
        df (pd.DataFrame): El DataFrame que se desea subir.
        dataset_id (str): El ID del dataset de BigQuery.
        table_name (str): El nombre de la tabla en BigQuery.
        mode (str): 'insert' (por defecto) para agregar datos, 'truncate' para borrar lo que haya en la tabla y insertar los nuevos datos.

    Returns:
        None
    """

    from google.cloud import bigquery
    client_bq = get_bigquery_client()
    table_id = f"{dataset_id}.{table_name}"
    
    # Configurar write_disposition según el modo
    if mode == "insert":
        write_disposition = "WRITE_APPEND"
    elif mode == "truncate":
        write_disposition = "WRITE_TRUNCATE"
    else:
        raise ValueError("El parámetro 'mode' debe ser 'insert' o 'truncate'.")
    
    job_config = bigquery.LoadJobConfig(write_disposition=write_disposition)
    job = client_bq.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"DataFrame subido a BigQuery en la tabla '{table_id}'.")


def read_bigquery(query):
    """
    Ejecuta una consulta en BigQuery y devuelve los resultados como un DataFrame.

    Args:
        query (str): La consulta SQL a ejecutar.

    Returns:
        pd.DataFrame: Los resultados de la consulta.
    """
    client_bq = get_bigquery_client()
    query_job = client_bq.query(query)
    print(f"Ejecutando consulta en BigQuery: {query}")
    result_df = query_job.to_dataframe()
    print("Consulta completada y resultados devueltos como DataFrame.")
    return result_df

def crear_bucket(target_project, target_location, target_bucket_name):
    """
    Crea un bucket en Google Cloud Storage si no existe.

    Args:
        target_project (str): El ID del proyecto de Google Cloud.
        target_location (str): La ubicación donde se creará el bucket.
        target_bucket_name (str): El nombre del bucket.

    Returns:
        None
    """
    client = get_storage_client()
    try:
        bucket = client.bucket(target_bucket_name)
        if not bucket.exists():
            bucket.location = target_location
            client.create_bucket(bucket)
            print(f"Bucket '{target_bucket_name}' creado exitosamente en la ubicación '{target_location}'.")
        else:
            print(f"El bucket '{target_bucket_name}' ya existe.")
    except Exception as e:
        print(f"Error al crear el bucket '{target_bucket_name}': {e}")

def read_dataframe_from_pickle_gcs(bucket_name, file_name):
    """
    Lee un DataFrame de Pandas desde un bucket de Google Cloud Storage en formato binario (pickle).

    Args:
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        file_name (str): El nombre del archivo desde el cual se leerá el DataFrame.

    Returns:
        pd.DataFrame: El DataFrame leído desde el archivo en GCS.
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    print(f"Leyendo DataFrame desde gs://{bucket_name}/{file_name}.")
    df_pickle = blob.download_as_string()
    df = pickle.loads(df_pickle)
    print("DataFrame leído correctamente desde GCS.")
    return df

def save_dataframe_to_gcs_pickle(df, bucket_name, file_name):
    """
    Guarda un DataFrame de Pandas en un bucket de Google Cloud Storage en formato binario (pickle).

    Args:
        df (pd.DataFrame): El DataFrame que se desea guardar.
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        file_name (str): El nombre del archivo con el que se guardará el DataFrame.

    Raises:
        DataFrameAlreadyExistsError: Si el archivo con el nombre dado ya existe en el bucket.
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=file_name))

    if any(file_name in blob.name for blob in blobs):
        raise DataFrameAlreadyExistsError(f"El DataFrame con el nombre '{file_name}' ya existe en el bucket '{bucket_name}'.")
    else:
        df_pickle = pickle.dumps(df)
        blob = bucket.blob(file_name)
        blob.upload_from_string(df_pickle, content_type='application/octet-stream')
        print(f"DataFrame guardado en gs://{bucket_name}/{file_name}.")

def read_dataframe_from_gcs_csv(bucket_name, file_name):
    """
    Lee un DataFrame de Pandas desde un archivo CSV almacenado en un bucket de Google Cloud Storage.

    Args:
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        file_name (str): El nombre del archivo CSV en el bucket.

    Returns:
        pd.DataFrame: El DataFrame leído desde el archivo CSV en GCS.
    """
    from io import StringIO

    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    print(f"Leyendo DataFrame desde gs://{bucket_name}/{file_name}.")
    csv_data = blob.download_as_text()  # Descarga el contenido del archivo como texto
    df = pd.read_csv(StringIO(csv_data))  # Convierte el texto en un DataFrame de Pandas
    print("DataFrame leído correctamente desde GCS en formato CSV.")
    
    return df

def save_dataframe_to_gcs_csv(df, bucket_name, file_name):
    """
    Guarda un DataFrame de Pandas en un bucket de Google Cloud Storage en formato CSV.

    Args:
        df (pd.DataFrame): El DataFrame que se desea guardar.
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        file_name (str): El nombre del archivo con el que se guardará el DataFrame.

    Raises:
        DataFrameAlreadyExistsError: Si el archivo con el nombre dado ya existe en el bucket.
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=file_name))

    if any(file_name in blob.name for blob in blobs):
        raise DataFrameAlreadyExistsError(f"El DataFrame con el nombre '{file_name}' ya existe en el bucket '{bucket_name}'.")
    else:
        # Convierte el DataFrame a CSV en memoria y sube a GCS
        csv_data = df.to_csv(index=False)
        blob = bucket.blob(file_name)
        blob.upload_from_string(csv_data, content_type='text/csv')
        print(f"DataFrame guardado en formato CSV en gs://{bucket_name}/{file_name}.")

def save_model_to_gcs(model, bucket_name, model_name):
    """
    Guarda un modelo de TensorFlow en un bucket de Google Cloud Storage.

    Args:
        model (tf.keras.Model): El modelo de TensorFlow que se desea guardar.
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        model_name (str): El nombre del archivo con el que se guardará el modelo.

    Raises:
        ModelAlreadyExistsError: Si el modelo con el nombre dado ya existe en el bucket.
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=model_name))

    if any(model_name in blob.name for blob in blobs):
        raise ModelAlreadyExistsError(f"El modelo con el nombre '{model_name}' ya existe en el bucket '{bucket_name}'.")
    else:
        model_dir = f'gs://{bucket_name}/{model_name}'
        model.save(model_dir)
        print(f"Modelo guardado en {model_dir}.")

def upload_model_to_vertex_ai(target_project, target_location, bucket_name, model_name, display_name):
    """
    Sube un modelo de TensorFlow a Vertex AI.

    Args:
        target_project (str): El ID del proyecto de Google Cloud.
        target_location (str): La ubicación del modelo en Vertex AI.
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        model_name (str): El nombre del archivo con el que se guardó el modelo en GCS.
        display_name (str): El nombre que se mostrará en Vertex AI.

    Returns:
        google.cloud.aiplatform.Model: El modelo subido a Vertex AI.
    """
    client_ai = get_aiplatform_client()
    client_ai.init(project=target_project, location=target_location)
    print(f"Subiendo modelo desde gs://{bucket_name}/{model_name} a Vertex AI con el nombre '{display_name}'.")
    model = client_ai.Model.upload(
        display_name=display_name,
        artifact_uri=f'gs://{bucket_name}/{model_name}',
        serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-8:latest"
    )
    print(f"Modelo subido a Vertex AI con el nombre '{display_name}'.")
    return model

def load_model_from_vertex_ai(model_id, project_id, location):
    """
    Carga un modelo desde Vertex AI en una variable.

    Args:
        model_id (str): El ID del modelo en Vertex AI.
        project_id (str): El ID del proyecto de GCP.
        location (str): La ubicación del modelo en Vertex AI.

    Returns:
        aiplatform.Model: El modelo cargado desde Vertex AI.
    """
    client_ai = get_aiplatform_client()
    client_ai.init(project=project_id, location=location)
    model_name = f"projects/{project_id}/locations/{location}/models/{model_id}"
    print(f"Cargando modelo desde Vertex AI con ID '{model_name}'.")
    model = client_ai.Model(model_name=model_name)
    print(f"Modelo '{model_name}' cargado correctamente desde Vertex AI.")
    return model

def copy_model_between_buckets(source_project, source_location, source_bucket_name, source_model_name,
                               target_project, target_location, target_bucket_name, target_model_name):
    """
    Copia un modelo (carpeta) de un bucket en un proyecto y ubicación a otro bucket en otro proyecto y ubicación.

    Args:
        source_project (str): El ID del proyecto de origen.
        source_location (str): La ubicación del bucket de origen.
        source_bucket_name (str): El nombre del bucket de origen.
        source_model_name (str): El nombre de la carpeta del modelo en el bucket de origen.
        target_project (str): El ID del proyecto de destino.
        target_location (str): La ubicación del bucket de destino.
        target_bucket_name (str): El nombre del bucket de destino.
        target_model_name (str): El nombre de la carpeta del modelo en el bucket de destino.

    Returns:
        None
    """
    client = get_storage_client()
    source_bucket = client.bucket(source_bucket_name)
    target_bucket = client.bucket(target_bucket_name)

    blobs = list(source_bucket.list_blobs(prefix=source_model_name + "/"))

    print(f"Iniciando copia de modelo '{source_model_name}' de '{source_bucket_name}' a '{target_bucket_name}'.")

    for blob in blobs:
        if blob.name.startswith(source_model_name + "/"):
            target_blob_name = target_model_name + blob.name[len(source_model_name):]
            source_bucket.copy_blob(blob, target_bucket, target_blob_name)
            print(f"Copiado '{blob.name}' a '{target_blob_name}'.")

    print(f"Modelo '{source_model_name}' copiado correctamente a '{target_bucket_name}'.")

def deploy_model_with_new_endpoint(model, project_id, location, endpoint_display_name, display_name_pro):
    """
    Despliega un modelo en Vertex AI en un nuevo endpoint con un nombre personalizado.

    Args:
        model (aiplatform.Model): El objeto de modelo en Vertex AI ya cargado.
        project_id (str): El ID del proyecto de Google Cloud.
        location (str): La ubicación del modelo y el endpoint en Vertex AI.
        endpoint_display_name (str): El nombre de visualización del nuevo endpoint.
        display_name_pro (str): Prefijo para el nombre de visualización del modelo desplegado.

    Returns:
        None
    """
    client_ai = get_aiplatform_client()
    client_ai.init(project=project_id, location=location)

    print(f"Creando un nuevo endpoint con el nombre '{endpoint_display_name}'...")
    endpoint = client_ai.Endpoint.create(display_name=endpoint_display_name)
    print(f"Nuevo endpoint creado: {endpoint.resource_name}")

    time.sleep(30)

    deployed_model_display_name = f"{display_name_pro}_{model.name.split('/')[-1]}"

    print("Iniciando despliegue del modelo...")
    try:
        endpoint.deploy(
            model=model,
            deployed_model_display_name=deployed_model_display_name,
            traffic_split={"0": 100},
            machine_type="n2-standard-4"
        )

        print(f"Modelo desplegado exitosamente: {deployed_model_display_name} en el endpoint {endpoint.display_name}")

    except Exception as e:
        print(f"Error durante el despliegue: {e}")
        raise

def load_endpoint(project_id, location, endpoint_id):
    """
    Carga un endpoint en Vertex AI para poder realizar predicciones.

    Args:
        project_id (str): El ID del proyecto de Google Cloud.
        location (str): La ubicación del endpoint en Vertex AI.
        endpoint_id (str): El ID del endpoint en Vertex AI.

    Returns:
        aiplatform.Endpoint: El endpoint cargado desde Vertex AI.
    """
    client_ai = get_aiplatform_client()
    client_ai.init(project=project_id, location=location)
    print(f"Inicializado Vertex AI para el proyecto '{project_id}' en la ubicación '{location}'.")

    endpoint_name = f"projects/{project_id}/locations/{location}/endpoints/{endpoint_id}"
    endpoint = client_ai.Endpoint(endpoint_name=endpoint_name)
    print(f"Endpoint '{endpoint_name}' cargado desde Vertex AI.")

    return endpoint

def download_folder_as_zip(source_folder, zip_name='output_files.zip'):
    # Importar las librerías necesarias
    import shutil
    from google.colab import files

    # Comprimir la carpeta en un archivo ZIP
    print(f"Comprimiendo la carpeta {source_folder} en un archivo ZIP...")
    shutil.make_archive(zip_name.replace('.zip', ''), 'zip', source_folder)
    
    # Informar que la compresión ha sido exitosa
    print(f"Carpeta comprimida con éxito. Descargando {zip_name}...")
    
    # Descargar el archivo ZIP
    files.download(zip_name)

def download_bucket_as_zip(bucket_name, destination_zip_name='bucket_files.zip'):
    # Importar las librerías necesarias
    import os
    import shutil
    from io import BytesIO
    import zipfile

    client = get_storage_client()
    bucket = client.bucket(bucket_name)

    # Crear un objeto BytesIO para almacenar el ZIP en memoria
    zip_buffer = BytesIO()

    print(f"Descargando archivos del bucket {bucket_name} y comprimiendo en {destination_zip_name}...")

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        blobs = list(bucket.list_blobs())
        for blob in blobs:
            blob_data = blob.download_as_bytes()
            zip_file.writestr(blob.name, blob_data)
            print(f"Archivo {blob.name} añadido al ZIP.")

    # Guardar el ZIP en un archivo local
    with open(destination_zip_name, 'wb') as f:
        f.write(zip_buffer.getvalue())

    print(f"Archivos del bucket {bucket_name} comprimidos en {destination_zip_name} con éxito.")

def delete_all_files_in_directory(directory_path):
    """
    Elimina todos los archivos y subdirectorios dentro de un directorio especificado.

    Args:
        directory_path (str): La ruta del directorio a limpiar.

    Returns:
        None
    """
    import os
    import shutil

    if os.path.exists(directory_path):
        # Elimina todos los archivos y subdirectorios en el directorio
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Elimina archivos o enlaces simbólicos
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Elimina directorios y su contenido
            except Exception as e:
                print(f'Error al eliminar {file_path}. Razón: {e}')
        print(f'Todos los archivos en {directory_path} han sido eliminados.')
    else:
        print(f'El directorio {directory_path} no existe.')

def move_bucket_contents_between_projects(source_project, source_bucket_name, target_project, target_bucket_name):
    """
    Mueve todo el contenido de un bucket en un proyecto a otro bucket en un proyecto diferente.

    Args:
        source_project (str): El ID del proyecto de origen.
        source_bucket_name (str): El nombre del bucket de origen.
        target_project (str): El ID del proyecto de destino.
        target_bucket_name (str): El nombre del bucket de destino.

    Returns:
        None
    """
    # Obtener clientes de GCS para ambos proyectos
    source_client = get_storage_client()
    target_client = get_storage_client()

    # Acceder a los buckets
    source_bucket = source_client.bucket(source_bucket_name)
    target_bucket = target_client.bucket(target_bucket_name)

    # Listar blobs (archivos) en el bucket de origen
    blobs = list(source_bucket.list_blobs())

    print(f"Iniciando la transferencia del contenido de '{source_bucket_name}' (proyecto: {source_project}) "
          f"a '{target_bucket_name}' (proyecto: {target_project}).")

    # Copiar cada archivo del bucket de origen al bucket de destino
    for blob in blobs:
        target_blob = target_bucket.blob(blob.name)
        source_bucket.copy_blob(blob, target_bucket, blob.name)
        print(f"Archivo '{blob.name}' copiado de '{source_bucket_name}' a '{target_bucket_name}'.")

    print(f"Todo el contenido ha sido movido de '{source_bucket_name}' a '{target_bucket_name}'.")

    # Eliminar los archivos en el bucket de origen después de la copia
    for blob in blobs:
        blob.delete()
        print(f"Archivo '{blob.name}' eliminado de '{source_bucket_name}'.")

    print(f"El contenido del bucket '{source_bucket_name}' ha sido movido correctamente a '{target_bucket_name}'.")

def upload_file_to_gcs(bucket_name, destination_blob_name, file_obj):
    """
    Sube un archivo a un bucket de Google Cloud Storage.

    Args:
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        destination_blob_name (str): El nombre del archivo de destino en el bucket (incluyendo carpetas si es necesario).
        file_obj (BytesIO o str): El archivo a subir, puede ser un objeto en memoria (BytesIO) o una ruta de archivo local.

    Raises:
        Exception: En caso de errores durante la subida.
    """
    from io import BytesIO

    try:
        client = get_storage_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        if isinstance(file_obj, BytesIO):
            blob.upload_from_file(file_obj)
        else:
            blob.upload_from_filename(file_obj)

        print(f"Archivo subido exitosamente a gs://{bucket_name}/{destination_blob_name}")
    except Exception as e:
        raise Exception(f"Error al subir el archivo: {str(e)}")

def download_file_from_gcs(bucket_name, file_path, return_bytes=False):
    """
    Descarga un archivo desde un bucket de Google Cloud Storage.

    Args:
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        file_path (str): La ruta completa del archivo en el bucket (incluyendo carpetas y extensión).
        return_bytes (bool): Si es True, devuelve los datos como BytesIO. Por defecto es False.

    Returns:
        BytesIO o file_data: Dependiendo del argumento 'return_bytes', devuelve un objeto en memoria o los datos en crudo.
    """
    from io import BytesIO

    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    file_data = blob.download_as_bytes()  # Descargar el archivo como binario

    if return_bytes:
        return BytesIO(file_data)  # Envolver los bytes en BytesIO si se especifica
    else:
        return file_data  # Devolver los datos binarios sin envolver

def list_files_in_gcs_folder(bucket_name, folder_path):
    """
    Lista todos los archivos dentro de una carpeta en un bucket de Google Cloud Storage.

    Args:
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        folder_path (str): La ruta de la carpeta dentro del bucket (debe terminar con '/').

    Returns:
        list: Una lista de nombres de archivos encontrados dentro de la carpeta.
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_path)  # Listar archivos con el prefijo de la carpeta

    file_names = [blob.name for blob in blobs if not blob.name.endswith('/')]  # Filtrar directorios y devolver solo archivos

    return file_names


def list_all_in_gcs_folder(bucket_name, folder_path):
    """
    Lista todos los elementos dentro de una carpeta en un bucket de Google Cloud Storage,
    incluyendo archivos y subcarpetas.

    Args:
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        folder_path (str): La ruta de la carpeta dentro del bucket (debe terminar con '/').

    Returns:
        list: Una lista de nombres de todos los elementos (archivos y subcarpetas) encontrados dentro de la carpeta.
    """
    client = get_storage_client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_path)  # Listar todo con el prefijo de la carpeta
    
    all_items = set()
    for blob in blobs:
        # Extraer el nombre del objeto relativo a la carpeta
        relative_path = blob.name[len(folder_path):].strip('/')
        if '/' in relative_path:
            # Es una subcarpeta, tomamos solo el primer nivel
            top_level_folder = relative_path.split('/')[0] + '/'
            all_items.add(top_level_folder)
        else:
            # Es un archivo
            all_items.add(relative_path)
    
    return sorted(all_items)  # Ordenar alfabéticamente


def delete_all_tables_in_dataset(dataset_id):
    """
    Elimina todas las tablas de un dataset en BigQuery.

    Args:
        dataset_id (str): El ID del dataset en BigQuery (en formato project_id.dataset_id).

    Raises:
        Exception: En caso de errores durante la eliminación de las tablas.
    """
    from google.cloud import bigquery

    try:
        client = get_bigquery_client()

        # Separar el dataset en project_id y dataset_id si es necesario
        project_id, dataset = dataset_id.split('.')
        dataset_ref = client.dataset(dataset, project=project_id)

        # Listar todas las tablas en el dataset
        tables = client.list_tables(dataset_ref)

        # Eliminar cada tabla encontrada
        for table in tables:
            table_ref = dataset_ref.table(table.table_id)
            client.delete_table(table_ref)
            print(f"Tabla {table.table_id} eliminada exitosamente.")

    except Exception as e:
        raise Exception(f"Error al eliminar las tablas: {str(e)}")

def list_all_tables_in_dataset(dataset_id):
    """
    Lista todas las tablas de un dataset de BigQuery y devuelve una lista con los nombres de las tablas.

    Args:
        dataset_id (str): El ID del dataset en BigQuery (en formato project_id.dataset_id).

    Returns:
        list: Una lista con los nombres de las tablas en el dataset.

    Raises:
        Exception: En caso de error, la descripción del mismo.
    """
    try:
        client = get_bigquery_client()

        # Separar el dataset en project_id y dataset_id si es necesario
        project_id, dataset = dataset_id.split('.')
        dataset_ref = client.dataset(dataset, project=project_id)

        # Listar todas las tablas en el dataset
        tables = client.list_tables(dataset_ref)

        # Convertir el resultado en una lista de nombres de tablas
        table_names = [table.table_id for table in tables]

        return table_names

    except Exception as e:
        raise Exception(f"Error al leer las tablas del dataset {dataset_id}: {str(e)}")

def run_query_bigquery(query: str):
    """
    Ejecuta una consulta en BigQuery, imprime mensajes de estado y maneja errores.

    Args:
        query (str): La consulta SQL a ejecutar.
    """
    client_bq = get_bigquery_client()  # Inicializa el cliente de BigQuery
    try:
        query_job = client_bq.query(query)  # Lanza la consulta
        query_job.result()  # Asegura que la consulta se ejecute completamente
        print("Consulta ejecutada exitosamente.")
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")

def create_folder_in_bucket(bucket_name, folder_name):
    """
    Crea una carpeta en un bucket de Google Cloud Storage.

    Args:
        bucket_name (str): El nombre del bucket en Google Cloud Storage.
        folder_name (str): El nombre de la carpeta que se desea crear.

    Returns:
        str: Confirmación de que la carpeta ha sido creada.

    Raises:
        Exception: En caso de error, la descripción del mismo.
    """
    try:
        client = get_storage_client()
        bucket = client.bucket(bucket_name)

        # Crear un blob con el nombre de la carpeta (terminado en '/')
        folder_blob = bucket.blob(f"{folder_name}/")
        folder_blob.upload_from_string('')

        return f"Carpeta '{folder_name}' creada en el bucket '{bucket_name}'"

    except Exception as e:
        raise Exception(f"Error al crear la carpeta '{folder_name}' en el bucket '{bucket_name}': {str(e)}")

def insert_geometry_to_bigquery(df, dataset_id, table_name, swap_xy = False, mode="insert"):
    
    """
    Inserta un DataFrame en una tabla de BigQuery y asegura que la columna geometry sea de tipo GEOGRAPHY.
    Args:
        - df: GeoDataframe a subir
        - dataset_id: ID del Dataset junto con el proyecto en el que está
        - table_name: Nombre que se quiere dar a la tabla
        - swap_xy: (opcional) Si es True, intercambia las coordenadas X e Y
        - mode: 'insert' (por defecto) para agregar datos, 'truncate' para borrar lo que haya en la tabla y insertar los nuevos datos
    """
    
    from google.cloud import bigquery

    client_bq = get_bigquery_client()
    table_id = f"{dataset_id}.{table_name}"

    # Convertir la columna de geometrías a WKT (esto NO cambia su tipo a string, es solo formato para BigQuery)
    if 'geometry' in df.columns:

      df['geometry'] = df['geometry'].apply(lambda geom: geom if geom else None)


    # Especificar explícitamente el esquema, indicando que 'geometry' debe ser GEOGRAPHY
    schema = [
        bigquery.SchemaField("geometry", "GEOGRAPHY"),  # Aseguramos que se interprete como GEOGRAPHY
    ]

    # Configurar write_disposition según el modo
    if mode == "insert":
        write_disposition = "WRITE_APPEND"
    elif mode == "truncate":
        write_disposition = "WRITE_TRUNCATE"
    else:
        raise ValueError("El parámetro 'mode' debe ser 'insert' o 'truncate'.")

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        schema=schema  # Esquema definido manualmente, para asegurar que 'geometry' sea GEOGRAPHY
    )

    # Subir el DataFrame a BigQuery
    job = client_bq.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Esperar a que el trabajo termine

    print(f"DataFrame insertado en BigQuery en la tabla '{table_id}' con la columna geometry como GEOGRAPHY.")



def create_dataset_if_not_exists(dataset_id, location="europe-west1"):
    """
    Crea un dataset en BigQuery si no existe ya en el proyecto especificado.

    Args:
        dataset_id (str): El ID del dataset en BigQuery (en formato project_id.dataset_id).
        location (str): La localización del dataset (por defecto "europe-west1").

    Returns:
        str: Un mensaje confirmando la creación o existencia del dataset.

    Raises:
        Exception: En caso de error, la descripción del mismo.
    """

    from google.cloud import bigquery

    try:
        client = bigquery.Client()

        # Separar el dataset en project_id y dataset_id si es necesario
        project_id, dataset = dataset_id.split('.')
        dataset_ref = client.dataset(dataset, project=project_id)

        # Verificar si el dataset ya existe
        try:
            client.get_dataset(dataset_ref)
            return f"El dataset '{dataset_id}' ya existe."
        except Exception:
            # Crear el dataset ya que no existe
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = location
            client.create_dataset(dataset, exists_ok=True)
            return f"Dataset '{dataset_id}' creado exitosamente en la localización '{location}'."

    except Exception as e:
        raise Exception(f"Error al crear el dataset {dataset_id}: {str(e)}")

def save_file_temporarily(file):
    """
    Guarda un archivo temporalmente en el sistema y retorna su ruta.

    Args:
        file (bytes): Contenido del archivo que se desea almacenar temporalmente.

    Returns:
        str: Ruta del archivo temporal creado.
    """
    import tempfile

    try:
        # Guardar el archivo de forma temporal
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file)
            temp_file_path = temp_file.name

        return temp_file_path

    except Exception as e:
        raise Exception(f"Error al guardar el archivo temporalmente: {str(e)}")
    
def upload_folder_to_gcs(bucket_name, destination_folder, folder_path):
    """
    Sube una carpeta completa a un bucket de Google Cloud Storage.

    Args:
        bucket_name (str): El nombre del bucket de Google Cloud Storage.
        destination_folder (str): Carpeta destino en el bucket.
        folder_path (str): Ruta local de la carpeta a subir.

    Raises:
        Exception: En caso de errores durante la subida.
    """
    try:
        from os import walk, path
        client = get_storage_client()
        bucket = client.bucket(bucket_name)

        for root, _, files in walk(folder_path):
            for file_name in files:
                local_file_path = path.join(root, file_name)
                relative_path = path.relpath(local_file_path, folder_path)
                destination_blob_name = path.join(destination_folder, relative_path).replace("\\", "/")  # Compatibilidad con Windows

                blob = bucket.blob(destination_blob_name)
                blob.upload_from_filename(local_file_path)

                print(f"Archivo subido exitosamente a gs://{bucket_name}/{destination_blob_name}")

    except Exception as e:
        raise Exception(f"Error al subir la carpeta: {str(e)}")


def asegurar_columnas_en_tabla(df, dataset_id, table_name, col_types=None):
    from google.cloud import bigquery
    from google.api_core.exceptions import NotFound

    client = get_bigquery_client()
    table_id = f"{dataset_id}.{table_name}"
    col_types = col_types or {}

    try:
        table = client.get_table(table_id)
    except NotFound:
        return

    columnas_actuales = {field.name for field in table.schema}
    nuevas_columnas = [col for col in df.columns if col not in columnas_actuales]

    if nuevas_columnas:
        for col in nuevas_columnas:
            if col_types.get(col, "STRING") == "STRING":
                df[col] = df[col].astype(str)

        campos_nuevos = [
            bigquery.SchemaField(
                name=col,
                field_type=col_types.get(col, "STRING"),
                mode="NULLABLE"
            )
            for col in nuevas_columnas
        ]

        nueva_schema = table.schema + campos_nuevos
        table.schema = nueva_schema
        client.update_table(table, ["schema"])








