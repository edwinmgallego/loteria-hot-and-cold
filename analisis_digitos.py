import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()
usuario = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
host = os.getenv('DB_HOST', '127.0.0.1')
base_datos = os.getenv('DB_NAME', 'loterias_db')

def analizar_digitos_individuales():
    print("📊 Descomponiendo todos los números y series dígito por dígito...")
    
    cadena_conexion = f"mysql+pymysql://{usuario}:{password}@{host}/{base_datos}"
    motor = create_engine(cadena_conexion)
    
    # ==========================================
    # 1. ANÁLISIS DE LOS NÚMEROS (4 CIFRAS)
    # ==========================================
    query_numeros = """
    SELECT numero_mayor AS numero FROM sorteos_loteria_valle
    UNION ALL
    SELECT numero_ganador AS numero FROM premios_secos_valle
    """
    df_numeros = pd.read_sql(query_numeros, motor)
    df_numeros['numero'] = df_numeros['numero'].astype(str).str.zfill(4)
    
    # Truco de Pandas: convertimos "1234" en ['1', '2', '3', '4'] y luego "explotamos" la lista
    todos_los_digitos_num = df_numeros['numero'].apply(list).explode()
    
    # Contamos la frecuencia y ordenamos del 0 al 9
    conteo_num = todos_los_digitos_num.value_counts().reset_index()
    conteo_num.columns = ['Dígito', 'Frecuencia']
    conteo_num = conteo_num.sort_values('Dígito')
    
    # ==========================================
    # 2. ANÁLISIS DE LAS SERIES (3 CIFRAS)
    # ==========================================
    query_series = """
    SELECT serie_mayor AS serie FROM sorteos_loteria_valle
    UNION ALL
    SELECT serie_ganadora AS serie FROM premios_secos_valle
    """
    df_series = pd.read_sql(query_series, motor)
    df_series['serie'] = df_series['serie'].astype(str).str.zfill(3)
    
    # Aplicamos el mismo proceso a las series
    todos_los_digitos_serie = df_series['serie'].apply(list).explode()
    conteo_serie = todos_los_digitos_serie.value_counts().reset_index()
    conteo_serie.columns = ['Dígito', 'Frecuencia']
    conteo_serie = conteo_serie.sort_values('Dígito')
    
    # ==========================================
    # 3. VISUALIZACIÓN
    # ==========================================
    sns.set_theme(style="whitegrid")
    fig, ejes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Gráfica de los Números
    sns.barplot(data=conteo_num, x='Dígito', y='Frecuencia', ax=ejes[0], palette="inferno", hue='Dígito', legend=False)
    ejes[0].set_title('🔥 Dígitos Más Calientes en los NÚMEROS (0-9)', fontsize=14, fontweight='bold')
    ejes[0].set_ylabel('Veces que ha salido (Global)')
    
    # Gráfica de las Series
    sns.barplot(data=conteo_serie, x='Dígito', y='Frecuencia', ax=ejes[1], palette="coolwarm", hue='Dígito', legend=False)
    ejes[1].set_title('🎟️ Dígitos Más Calientes en las SERIES (0-9)', fontsize=14, fontweight='bold')
    ejes[1].set_ylabel('Veces que ha salido (Global)')
    
    plt.tight_layout()
    print("📈 Abriendo gráficas de calor de los dígitos...")
    plt.show()

if __name__ == '__main__':
    analizar_digitos_individuales()