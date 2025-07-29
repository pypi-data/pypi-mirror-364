import os
import requests
import zipfile
import subprocess
from urllib import request, parse
import atoma
import tempfile
from io import BytesIO
import pandas as pd

# El diccionario atom_urls mantiene las URLs para parcels, buildings y addresses
atom_urls = {
    'parcels': 'https://www.catastro.hacienda.gob.es/INSPIRE/CadastralParcels/ES.SDGC.CP.atom.xml',
    'buildings': 'https://www.catastro.hacienda.gob.es/INSPIRE/buildings/ES.SDGC.BU.atom.xml',
    'addresses': 'https://www.catastro.hacienda.gob.es/INSPIRE/Addresses/ES.SDGC.AD.atom.xml'
}

def format_codmun(provincia, municipio):
    """Obtiene el código de municipio a partir de la provincia y el municipio"""
    return str(provincia).zfill(2) + str(municipio).zfill(3)

def parse_url(url):
    """Codifica la URL"""
    url = parse.urlsplit(url)
    url = list(url)
    url[2] = parse.quote(url[2])
    parsed_url = parse.urlunsplit(url)
    return parsed_url

def get_municipality_atoms_url(atom_url, codmun=None):
    """
    Lee el Atom específico para cada municipio.
    Devuelve el URL del Atom de cada municipio con su EPSG.
    """
    response = requests.get(atom_url)
    feed = atoma.parse_atom_bytes(response.content)

    urls = []
    for entry in feed.entries:
        url = parse_url(entry.links[0].href)
        epsg = entry.categories[0].term.split('/')[-1]
        codmun_atom = os.path.basename(url).split('.')[4]

        if codmun is None or codmun == codmun_atom:
            urls.append((url, epsg))

    return urls

def get_provinces_atoms_url(url, province_code=None):
    """
    Lee el Atom general de Catastro Inspire que contiene los diferentes
    Atoms para cada provincia.
    Devuelve una lista con URL a los Atoms y el título.
    """
    response = requests.get(url)
    feed = atoma.parse_atom_bytes(response.content)

    atoms_provincias = []
    for entry in feed.entries:
        if province_code is not None:
            if os.path.basename(entry.links[0].href).split('.')[3] == f'atom_{str(province_code).zfill(2)}':
                url = parse_url(entry.links[0].href)
                title = entry.title.value
                atoms_provincias.append((url, title))
        else:
            url = parse_url(entry.links[0].href)
            title = entry.title.value
            atoms_provincias.append((url, title))

    return atoms_provincias

def download_and_process_municipality(url, epsg, output_gpkg, to_epsg=None, output_dir='.'):
    """
    Descarga un GML de Catastro a partir de una URL y un EPSG.
    Lo convierte a GeoPackage.
    Permite declarar un EPSG de destino.
    """
    if not to_epsg:
        to_epsg = epsg

    try:
        # Crear un directorio temporal para descargar y extraer
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_filename = os.path.join(temp_dir, os.path.basename(url))
            print(f"Descargando archivo ZIP a {zip_filename}")
            request.urlretrieve(url, zip_filename)

            with zipfile.ZipFile(zip_filename, "r") as z:
                z.extractall(path=temp_dir)

            for gml in os.listdir(temp_dir):
                if os.path.splitext(gml)[1].lower() == '.gml':
                    layer_name = os.path.splitext(gml)[0]
                    gml_path = os.path.join(temp_dir, gml)
                    geopackage_path = os.path.join(output_dir, f"{output_gpkg}.gpkg")
                    ogr_cmd = (
                        f"ogr2ogr -update -append -f GPKG "
                        f"-s_srs EPSG:{epsg} -t_srs EPSG:{to_epsg} "
                        f"-lco IDENTIFIER={layer_name} '{geopackage_path}' '{gml_path}'"
                    )
                    print(f"Ejecutando comando: {ogr_cmd}")
                    result = subprocess.run(ogr_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # nosec
                    if result.returncode != 0:
                        print(f"Error ejecutando ogr2ogr: {result.stderr.decode()}")
                    else:
                        # Imprime la ruta donde se ha guardado el archivo GeoPackage
                        print(f"Archivo guardado en: {geopackage_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

def cidownloader(provincia=None, municipio=None, srs=None, tipo='all', filename="buildings", output_dir='.'):
    """
    Función principal para descargar los datos de Catastro Inspire.

    Args:
        provincia (int): Código de la provincia.
        municipio (int): Código del municipio.
        srs (int): Código EPSG final.
        tipo (str): Tipo de datos a descargar (parcels, buildings, addresses, all).
        filename (str): Nombre del archivo GeoPackage de salida.
        output_dir (str): Directorio donde se guardará el archivo GeoPackage final.
    """
    if tipo == 'all':
        for key, url in atom_urls.items():
            print(f'Comenzando descarga de {key}:')
            download_data(url, provincia, municipio, srs, filename, output_dir)
    else:
        url = atom_urls[tipo]
        print(f'Comenzando descarga de {tipo}:')
        download_data(url, provincia, municipio, srs, filename, output_dir)

    # Imprime la ubicación del archivo guardado
    geopackage_path = os.path.join(output_dir, f"{filename}.gpkg")
    print(f"Archivo guardado en: {geopackage_path}")

def download_data(data_url, provincia=None, municipio=None, srs=None, filename="buildings", output_dir='.'):
    """
    Lógica para descargar y procesar los datos desde una URL específica.
    """
    atoms_provincias = get_provinces_atoms_url(data_url, provincia)
    codmun = format_codmun(provincia, municipio) if municipio is not None else None

    geopackage_name = filename
    for atom in atoms_provincias:
        prov_title = atom[1]
        prov_url = atom[0]
        print(f"Procesando provincia: {prov_title}")
        urls = get_municipality_atoms_url(prov_url, codmun=codmun)

        for url in urls:
            print(f"Descargando {url[0]}")
            download_and_process_municipality(url[0], url[1], geopackage_name, to_epsg=srs, output_dir=output_dir)




