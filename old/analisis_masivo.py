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

def generar_mapa_calor():
    print("📊 Extrayendo el histórico completo (Mayor + Secos)...")
    
    # Conexión a la base de datos
    cadena_conexion = f"mysql+pymysql://{usuario}:{password}@{host}/{base_datos}"
    motor = create_engine(cadena_conexion)
    
    # 1. UNION ALL: Traemos TODOS los números ganadores en una sola columna
    query = """
    SELECT numero_mayor AS numero FROM sorteos_loteria_valle
    UNION ALL
    SELECT numero_ganador AS numero FROM premios_secos_valle
    """
    df = pd.read_sql(query, motor)
    
    print(f"✅ ¡Se cargaron {len(df)} números ganadores en total!")
    
    # 2. Limpieza y separación por posiciones
    df['numero'] = df['numero'].astype(str).str.zfill(4)
    df['Posición 1 (Miles)'] = df['numero'].str[0].astype(int)
    df['Posición 2 (Centenas)'] = df['numero'].str[1].astype(int)
    df['Posición 3 (Decenas)'] = df['numero'].str[2].astype(int)
    df['Posición 4 (Unidades)'] = df['numero'].str[3].astype(int)
    
    # 3. Preparar la matriz para el Heatmap
    # Creamos un DataFrame vacío con índices del 0 al 9
    matriz_frecuencia = pd.DataFrame(index=range(10))
    
    # Llenamos la matriz contando cuántas veces aparece cada dígito por posición
    columnas_posicion = ['Posición 1 (Miles)', 'Posición 2 (Centenas)', 'Posición 3 (Decenas)', 'Posición 4 (Unidades)']
    for col in columnas_posicion:
        conteo = df[col].value_counts()
        matriz_frecuencia[col] = matriz_frecuencia.index.map(conteo).fillna(0)
        
    # 4. Configurar y graficar el Mapa de Calor
    plt.figure(figsize=(12, 8))
    
    # cmap="YlOrRd" usa la paleta Yellow-Orange-Red (Amarillo=Frío, Rojo=Caliente)
    # annot=True muestra el número exacto de veces dentro del cuadro
    sns.heatmap(matriz_frecuencia, annot=True, fmt="g", cmap="YlOrRd", linewidths=.5, 
                cbar_kws={'label': 'Frecuencia de aparición'})
    
    plt.title('🔥 Mapa de Calor: Frecuencia de Dígitos por Posición\n(Más de 4.600 premios de la Lotería del Valle)', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Posición en el Billete', fontsize=12)
    plt.ylabel('Dígito (0 - 9)', fontsize=12)
    plt.yticks(rotation=0) # Para que los números del 0 al 9 se lean derechos
    
    plt.tight_layout()
    print("📈 Abriendo el mapa de calor...")
    plt.show()

if __name__ == '__main__':
    generar_mapa_calor()