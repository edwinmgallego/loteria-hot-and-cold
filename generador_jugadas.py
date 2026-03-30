import os
import random
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()
usuario = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
host = os.getenv('DB_HOST', '127.0.0.1')
base_datos = os.getenv('DB_NAME', 'loterias_db')

def generar_propuestas_loteria():
    print("🤖 Analizando la base de datos para generar tus jugadas...")
    
    cadena_conexion = f"mysql+pymysql://{usuario}:{password}@{host}/{base_datos}"
    motor = create_engine(cadena_conexion)
    
    # 1. TRAER TODOS LOS DATOS
    query_numeros = """
    SELECT numero_mayor AS numero FROM sorteos_loteria_valle
    UNION ALL
    SELECT numero_ganador AS numero FROM premios_secos_valle
    """
    query_series = """
    SELECT serie_mayor AS serie FROM sorteos_loteria_valle
    UNION ALL
    SELECT serie_ganadora AS serie FROM premios_secos_valle
    """
    
    df_numeros = pd.read_sql(query_numeros, motor)
    df_series = pd.read_sql(query_series, motor)
    
    df_numeros['numero'] = df_numeros['numero'].astype(str).str.zfill(4)
    df_series['serie'] = df_series['serie'].astype(str).str.zfill(3)
    
    # 2. DESCOMPONER Y CONTAR (Como hicimos en el mapa de calor)
    conteo_num = df_numeros['numero'].apply(list).explode().value_counts().reset_index()
    conteo_num.columns = ['Dígito', 'Frecuencia']
    
    conteo_ser = df_series['serie'].apply(list).explode().value_counts().reset_index()
    conteo_ser.columns = ['Dígito', 'Frecuencia']
    
    # 3. IDENTIFICAR LOS EXTREMOS (Calientes y Fríos)
    # Tomamos los 4 primeros para el número y los 3 primeros para la serie
    num_calientes = conteo_num['Dígito'].head(4).tolist()
    num_frios = conteo_num['Dígito'].tail(4).tolist()
    
    ser_calientes = conteo_ser['Dígito'].head(3).tolist()
    ser_frios = conteo_ser['Dígito'].tail(3).tolist()
    
    print("\n==================================================")
    print(f"🔥 INGREDIENTES CALIENTES:")
    print(f"   Dígitos para Número: {num_calientes} | Para Serie: {ser_calientes}")
    print(f"❄️ INGREDIENTES FRÍOS:")
    print(f"   Dígitos para Número: {num_frios} | Para Serie: {ser_frios}")
    print("==================================================\n")

    # 4. FUNCIÓN GENERADORA DE BILLETES
    def armar_billetes(digitos_n, digitos_s, cantidad=3):
        billetes = []
        for _ in range(cantidad):
            # Usamos random.sample para mezclar los dígitos sin repetir la misma estructura
            n_mezclado = "".join(random.sample(digitos_n, len(digitos_n)))
            s_mezclado = "".join(random.sample(digitos_s, len(digitos_s)))
            billetes.append((n_mezclado, s_mezclado))
        return billetes

    # 5. GENERAR Y MOSTRAR RESULTADOS
    jugadas_calientes = armar_billetes(num_calientes, ser_calientes)
    jugadas_frias = armar_billetes(num_frios, ser_frios)

    print("🔥🔥🔥 TUS 3 JUGADAS CALIENTES (Mayor Probabilidad Histórica) 🔥🔥🔥")
    for i, (num, ser) in enumerate(jugadas_calientes, 1):
        print(f"   Opción {i}: Número {num} - Serie {ser}")
        
    print("\n🧊🧊🧊 TUS 3 JUGADAS FRÍAS (Los más olvidados por la máquina) 🧊🧊🧊")
    for i, (num, ser) in enumerate(jugadas_frias, 1):
        print(f"   Opción {i}: Número {num} - Serie {ser}")
    print("\n==================================================")

if __name__ == '__main__':
    generar_propuestas_loteria()