import random
import pandas as pd

class AnalizadorService:
    def generar_frecuencias(self, df):
        """Calcula frecuencias usando las columnas atómicas"""
        # Unimos las 4 columnas de balotas en una sola serie para contar la frecuencia global
        todas_balotas = pd.concat([df['balota_1'], df['balota_2'], df['balota_3'], df['balota_4']])
        frecuencia_num = todas_balotas.value_counts().sort_values(ascending=False)

        # Lo mismo para la serie
        todas_series = pd.concat([df['serie_1'], df['serie_2'], df['serie_3']])
        frecuencia_ser = todas_series.value_counts().sort_values(ascending=False)

        return {
            'num': {
                'calientes': frecuencia_num.index[:4].tolist(),
                'tibios': frecuencia_num.index[4:-4].tolist(),
                'frios': frecuencia_num.index[-4:].tolist()
            },
            'ser': {
                'calientes': frecuencia_ser.index[:3].tolist(),
                'tibios': frecuencia_ser.index[3:-3].tolist(),
                'frios': frecuencia_ser.index[-3:].tolist()
            }
        }

    def crear_jugadas_hibridas(self, grupos, cantidad=5):
        num_c, num_t, num_f = grupos['num']['calientes'], grupos['num']['tibios'], grupos['num']['frios']
        ser_c, ser_t, ser_f = grupos['ser']['calientes'], grupos['ser']['tibios'], grupos['ser']['frios']

        # Patrones de mezcla (cuántos calientes, tibios y fríos tomar)
        patrones_n = [(2, 1, 1), (1, 2, 1), (1, 0, 3), (1, 1, 2)]
        patrones_s = [(1, 1, 1), (2, 0, 1), (0, 2, 1)]
        
        jugadas = []
        for _ in range(cantidad):
            pn = random.choice(patrones_n)
            sel_n = random.sample(num_c, pn[0]) + random.sample(num_t, pn[1]) + random.sample(num_f, pn[2])
            random.shuffle(sel_n)
            
            ps = random.choice(patrones_s)
            sel_s = random.sample(ser_c, ps[0]) + random.sample(ser_t, ps[1]) + random.sample(ser_f, ps[2])
            random.shuffle(sel_s)
            
            # Map convierte cada número entero a string antes de unirlos
            jugadas.append(("".join(map(str, sel_n)), "".join(map(str, sel_s))))
            
        return jugadas