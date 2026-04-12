import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Cargar configuración
load_dotenv()
usuario = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
host = os.getenv('DB_HOST', '127.0.0.1')
base_datos = os.getenv('DB_NAME', 'loterias_db')

def analizar_premio_mayor():
    print("📊 Conectando a MySQL para extraer datos...")
    
    # Crear el motor de conexión (Mejor práctica para Pandas)
    cadena_conexion = f"mysql+pymysql://{usuario}:{password}@{host}/{base_datos}"
    motor = create_engine(cadena_conexion)
    
    # 2. Extraer datos con SQL directamente a un DataFrame de Pandas
    query = "SELECT * FROM sorteos_loteria_valle"
    df = pd.read_sql(query, motor)
    
    print(f"✅ Se cargaron {len(df)} sorteos en memoria.")
    
    # 3. Transformación de datos para el análisis
    # Asegurarnos de que el número tenga 4 cifras (rellenando con ceros a la izquierda si es necesario)
    df['numero_mayor'] = df['numero_mayor'].astype(str).str.zfill(4)
    
    # Extraer columnas calculadas
    df['ultimo_digito'] = df['numero_mayor'].str[-1]
    df['dos_ultimas'] = df['numero_mayor'].str[-2:]
    
    # 4. Configurar el estilo visual de las gráficas
    sns.set_theme(style="whitegrid")
    
    # Crear una figura con 2 subgráficos (1 fila, 2 columnas)
    fig, ejes = plt.subplots(1, 2, figsize=(16, 6))
    
    # --- GRÁFICO 1: Frecuencia del Último Dígito ---
    conteo_digitos = df['ultimo_digito'].value_counts().reset_index()
    conteo_digitos.columns = ['Dígito', 'Frecuencia']
    conteo_digitos = conteo_digitos.sort_values('Dígito') # Ordenar del 0 al 9
    
    sns.barplot(data=conteo_digitos, x='Dígito', y='Frecuencia', ax=ejes[0], palette="viridis", hue='Dígito', legend=False)
    ejes[0].set_title('Frecuencia del Último Dígito (El Chance)', fontsize=14, fontweight='bold')
    ejes[0].set_ylabel('Veces que ha caído')
    
    # --- GRÁFICO 2: Top 10 Series más Ganadoras ---
    conteo_series = df['serie_mayor'].value_counts().head(10).reset_index()
    conteo_series.columns = ['Serie', 'Frecuencia']
    
    sns.barplot(data=conteo_series, x='Serie', y='Frecuencia', ax=ejes[1], palette="magma", hue='Serie', legend=False)
    ejes[1].set_title('Top 10 Series más Ganadoras', fontsize=14, fontweight='bold')
    ejes[1].set_ylabel('Veces que ha caído')
    ejes[1].tick_params(axis='x', rotation=45) # Rotar los nombres de las series
    
    # Ajustar el diseño y mostrar la ventana con las gráficas
    plt.tight_layout()
    print("📈 Abriendo ventana de visualización...")
    plt.show()

if __name__ == '__main__':
    analizar_premio_mayor()