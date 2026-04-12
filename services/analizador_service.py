import random

class AnalizadorService:
    def generar_frecuencias(self, df_numeros, df_series):
        conteo_num = df_numeros['numero'].apply(list).explode().value_counts().reset_index()
        conteo_num.columns = ['Dígito', 'Frecuencia']
        todos_num = conteo_num['Dígito'].tolist()

        conteo_ser = df_series['serie'].apply(list).explode().value_counts().reset_index()
        conteo_ser.columns = ['Dígito', 'Frecuencia']
        todos_ser = conteo_ser['Dígito'].tolist()

        return {
            "num": {"calientes": todos_num[:4], "tibios": todos_num[4:6], "frios": todos_num[6:]},
            "ser": {"calientes": todos_ser[:3], "tibios": todos_ser[3:7], "frios": todos_ser[7:]}
        }

    def crear_jugadas_hibridas(self, grupos, cantidad=5):
        num_c, num_t, num_f = grupos['num']['calientes'], grupos['num']['tibios'], grupos['num']['frios']
        ser_c, ser_t, ser_f = grupos['ser']['calientes'], grupos['ser']['tibios'], grupos['ser']['frios']

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
            
            jugadas.append(("".join(sel_n), "".join(sel_s)))
        return jugadas