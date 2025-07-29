from setuptools import setup, find_packages

setup(
    name='kynegos_easy_cloud', # Nombre del paquete
    version='1.4.8',                     # Versión
    packages=find_packages(),            # Encuentra automáticamente los paquetes en la estructura
    install_requires=[                   # Lista de dependencias necesarias
        'google-auth',
        'google-cloud-bigquery',
        'google-cloud-storage',
        'google-cloud-aiplatform',
        'pandas',
        'atoma',
        #'gdal==3.6.4',
        'geopandas',
        'db-dtypes',
        'shapely',
        'owslib',
    ],

    author='Kynegos <> Data Hub',
    author_email='digital.data@capitalenergy.com',
    description='Kynegos Easy Cloud: automatiza Google Cloud para equipos de datos sin DevOps',
    long_description = open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    keywords=[
    'Kynegos', 'kynegos easy cloud', 'Google Cloud', 'BigQuery', 'GCS', 'Python',
    'Data Engineering', 'automatización cloud', 'catastro', 'GIS', 'GIS BigQuery', 'GIS Cloud'],
    url='https://kynegos.com/',  # Enlace a la página principal de la empresa
    project_urls={
    'PyPI': 'https://pypi.org/project/kynegos-easy-cloud/',
    'LinkedIn': 'https://www.linkedin.com/company/kynegos/',
    'X': 'https://x.com/Kynegos_',
    'Documentación': 'https://kynegos.com/',
    },

    
    # Agregar el campo de la licencia personalizada
    license='Kynegos License',

    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'License :: Other/Proprietary License',
    'Operating System :: OS Independent',
    ],

    python_requires='>=3.6',
    include_package_data=True,  # Incluir archivos adicionales en la distribución
    package_data={
        '': ['LICENSE'],  # Asegurar que el archivo LICENSE esté en la distribución
    },
)
