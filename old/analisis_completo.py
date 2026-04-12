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

def analizar_todas_las_cifras():
    print("📊 Conectando a MySQL para extraer datos...")
    
    cadena_conexion = f"mysql+pymysql://{usuario}:{password}@{host}/{base_datos}"
    motor = create_engine(cadena_conexion)
    
    query = "SELECT numero_mayor FROM sorteos_loteria_valle"
    df = pd.read_sql(query, motor)
    
    # Asegurarnos de que siempre sean 4 caracteres (ej: "0456" en lugar de "456")
    df['numero_mayor'] = df['numero_mayor'].astype(str).str.zfill(4)
    
    # 2. SEPARAR LAS CIFRAS POR POSICIÓN
    # Usamos .str[] para acceder a cada letra (número) de la cadena de texto
    df['cifra_1_miles'] = df['numero_mayor'].str[0]
    df['cifra_2_centenas'] = df['numero_mayor'].str[1]
    df['cifra_3_decenas'] = df['numero_mayor'].str[2]
    df['cifra_4_unidades'] = df['numero_mayor'].str[3]
    
    # 3. CONFIGURAR LA VISUALIZACIÓN
    sns.set_theme(style="whitegrid")
    
    # Creamos una cuadrícula de 2 filas por 2 columnas para los 4 gráficos
    fig, ejes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Análisis de Frecuencia: ¿Qué número cae más en cada posición?', fontsize=16, fontweight='bold')
    
    # Listas para automatizar el dibujado de las 4 gráficas
    posiciones = ['cifra_1_miles', 'cifra_2_centenas', 'cifra_3_decenas', 'cifra_4_unidades']
    titulos = ['1ra Cifra (Miles)', '2da Cifra (Centenas)', '3ra Cifra (Decenas)', '4ta Cifra (Unidades)']
    
    # Usamos ejes.flat para iterar fácilmente por los 4 espacios de la cuadrícula
    for i, ax in enumerate(ejes.flat):
        columna = posiciones[i]
        
        # Contar cuántas veces cayó cada número (del 0 al 9) y ordenarlos
        conteo = df[columna].value_counts().reset_index()
        conteo.columns = ['Dígito', 'Frecuencia']
        conteo = conteo.sort_values('Dígito') 
        
        # Dibujar la gráfica de barras
        sns.barplot(data=conteo, x='Dígito', y='Frecuencia', ax=ax, palette="viridis", hue='Dígito', legend=False)
        
        # Títulos y etiquetas
        ax.set_title(titulos[i], fontsize=12, fontweight='bold')
        ax.set_xlabel('Número (0-9)')
        ax.set_ylabel('Veces que ha caído')
        
    # Ajustar espacios para que no se superpongan los textos y mostrar
    plt.tight_layout()
    print("📈 Abriendo ventana de visualización...")
    plt.show()

if __name__ == '__main__':
    analizar_todas_las_cifras()