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
    
    # 2. DESCOMPONER Y CONTAR
    conteo_num = df_numeros['numero'].apply(list).explode().value_counts().reset_index()
    conteo_num.columns = ['Dígito', 'Frecuencia']
    
    conteo_ser = df_series['serie'].apply(list).explode().value_counts().reset_index()
    conteo_ser.columns = ['Dígito', 'Frecuencia']
    
    # 3. IDENTIFICAR LOS GRUPOS (Calientes, Tibios y Fríos)
    todos_num = conteo_num['Dígito'].tolist()
    num_calientes = todos_num[:4]  # Top 4
    num_tibios = todos_num[4:6]    # Los 2 del medio
    num_frios = todos_num[6:]      # Los 4 menos frecuentes
    
    todos_ser = conteo_ser['Dígito'].tolist()
    ser_calientes = todos_ser[:3]  # Top 3
    ser_tibios = todos_ser[3:7]    # Los 4 del medio
    ser_frios = todos_ser[7:]      # Los 3 menos frecuentes
    
    print("\n==================================================")
    print(f"🔥 CALIENTES : Número {num_calientes} | Serie {ser_calientes}")
    print(f"🌤️ TIBIOS    : Número {num_tibios} | Serie {ser_tibios}")
    print(f"❄️ FRÍOS     : Número {num_frios} | Serie {ser_frios}")
    print("==================================================\n")

    # 4. FUNCIONES GENERADORAS
    def armar_billetes_extremos(digitos_n, digitos_s, cantidad=3):
        """Genera billetes puros (solo calientes o solo fríos)"""
        billetes = []
        for _ in range(cantidad):
            n_mezclado = "".join(random.sample(digitos_n, len(digitos_n)))
            s_mezclado = "".join(random.sample(digitos_s, len(digitos_s)))
            billetes.append((n_mezclado, s_mezclado))
        return billetes

    def armar_billetes_hibridos(cantidad=5):
        """Genera billetes realistas mezclando los 3 grupos"""
        billetes = []
        # Patrones para el Número (4 cifras): (Cant. Calientes, Cant. Tibios, Cant. Fríos)
        patrones_numero = [
            (2, 1, 1), # 2 calientes, 1 tibio, 1 frío (Muy balanceado)
            (1, 2, 1), # 1 caliente, 2 tibios, 1 frío
            (1, 0, 3), # 1 caliente, 0 tibios, 3 fríos (El patrón que detectaste ayer)
            (1, 1, 2)  # 1 caliente, 1 tibio, 2 fríos
        ]
        
        # Patrones para la Serie (3 cifras):
        patrones_serie = [
            (1, 1, 1), # 1 de cada uno
            (2, 0, 1), # 2 calientes, 1 frío
            (0, 2, 1)  # 2 tibios, 1 frío
        ]
        
        for _ in range(cantidad):
            # 1. Armar el número
            p_n_cal, p_n_tib, p_n_fri = random.choice(patrones_numero)
            sel_num = random.sample(num_calientes, p_n_cal) + \
                      random.sample(num_tibios, p_n_tib) + \
                      random.sample(num_frios, p_n_fri)
            random.shuffle(sel_num) # Revolver posiciones
            
            # 2. Armar la serie
            p_s_cal, p_s_tib, p_s_fri = random.choice(patrones_serie)
            sel_ser = random.sample(ser_calientes, p_s_cal) + \
                      random.sample(ser_tibios, p_s_tib) + \
                      random.sample(ser_frios, p_s_fri)
            random.shuffle(sel_ser) # Revolver posiciones
            
            billetes.append(("".join(sel_num), "".join(sel_ser)))
            
        return billetes

    # 5. GENERAR Y MOSTRAR RESULTADOS
    jugadas_calientes = armar_billetes_extremos(num_calientes, ser_calientes, 2)
    jugadas_frias = armar_billetes_extremos(num_frios, ser_frios, 2)
    jugadas_hibridas = armar_billetes_hibridos(5) # Generamos 5 opciones realistas

    print("🔥🔥 JUGADAS EXTREMAS (Puro Fuego) 🔥🔥")
    for i, (num, ser) in enumerate(jugadas_calientes, 1):
        print(f"   Opción {i}: Número {num} - Serie {ser}")
        
    print("\n🧊🧊 JUGADAS EXTREMAS (Puro Hielo) 🧊🧊")
    for i, (num, ser) in enumerate(jugadas_frias, 1):
        print(f"   Opción {i}: Número {num} - Serie {ser}")
        
    print("\n🎯🎯 JUGADAS HÍBRIDAS (Regresión a la Media - Recomendadas) 🎯🎯")
    for i, (num, ser) in enumerate(jugadas_hibridas, 1):
        print(f"   Opción {i}: Número {num} - Serie {ser}")
    print("\n==================================================")

if __name__ == '__main__':
    generar_propuestas_loteria()