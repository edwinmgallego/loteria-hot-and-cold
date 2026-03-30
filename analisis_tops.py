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

def graficar_tops_historicos():
    print("📊 Calculando los números y series más ganadores del histórico...")
    
    cadena_conexion = f"mysql+pymysql://{usuario}:{password}@{host}/{base_datos}"
    motor = create_engine(cadena_conexion)
    
    # 1. Extraer TODOS los Números
    query_numeros = """
    SELECT numero_mayor AS numero FROM sorteos_loteria_valle
    UNION ALL
    SELECT numero_ganador AS numero FROM premios_secos_valle
    """
    df_numeros = pd.read_sql(query_numeros, motor)
    df_numeros['numero'] = df_numeros['numero'].astype(str).str.zfill(4)
    
    # 2. Extraer TODAS las Series
    query_series = """
    SELECT serie_mayor AS serie FROM sorteos_loteria_valle
    UNION ALL
    SELECT serie_ganadora AS serie FROM premios_secos_valle
    """
    df_series = pd.read_sql(query_series, motor)
    # Las series suelen tener 3 dígitos, rellenamos con ceros por si hay series como la "007"
    df_series['serie'] = df_series['serie'].astype(str).str.zfill(3)
    
    # 3. Calcular el Top 20 de cada categoría
    top_numeros = df_numeros['numero'].value_counts().head(20).reset_index()
    top_numeros.columns = ['Número Completo', 'Veces Ganador']
    
    top_series = df_series['serie'].value_counts().head(20).reset_index()
    top_series.columns = ['Serie Completa', 'Veces Ganadora']
    
    # 4. Configurar la visualización
    sns.set_theme(style="whitegrid")
    fig, ejes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Gráfica de los Números
    # Usamos la paleta "Reds_r" (Rojos invertidos) para que el más ganador sea el más oscuro
    sns.barplot(data=top_numeros, x='Número Completo', y='Veces Ganador', ax=ejes[0], palette="Reds_r", hue='Número Completo', legend=False)
    ejes[0].set_title('🏆 Top 20 Números Completos Más Frecuentes', fontsize=14, fontweight='bold')
    ejes[0].tick_params(axis='x', rotation=45)
    ejes[0].set_ylabel('Cantidad de Premios')
    
    # Gráfica de las Series
    # Usamos la paleta "Blues_r" para diferenciarlo visualmente
    sns.barplot(data=top_series, x='Serie Completa', y='Veces Ganadora', ax=ejes[1], palette="Blues_r", hue='Serie Completa', legend=False)
    ejes[1].set_title('🎫 Top 20 Series Más Frecuentes', fontsize=14, fontweight='bold')
    ejes[1].tick_params(axis='x', rotation=45)
    ejes[1].set_ylabel('Cantidad de Premios')
    
    plt.tight_layout()
    print("📈 Abriendo gráficas del Top 20...")
    plt.show()

if __name__ == '__main__':
    graficar_tops_historicos()