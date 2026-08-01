import pandas as pd

class MarkovService:
    def __init__(self):
        self.posiciones = ['balota_1', 'balota_2', 'balota_3', 'balota_4']
        self.matrices_transicion = {}

    def entrenar_markov(self, df):
        """
        Construye la matriz de probabilidad de transición para cada balotera.
        """
        # Asegurarnos de que el tiempo fluya hacia adelante
        df = df.sort_values('fecha_sorteo').reset_index(drop=True)
        
        for pos in self.posiciones:
            # Creamos una "máquina del tiempo" mirando un paso hacia el futuro
            df[f'next_{pos}'] = df[pos].shift(-1)
            
            # Quitamos la última fila porque el "futuro" de hoy aún no existe
            df_clean = df.dropna(subset=[f'next_{pos}'])
            
            # Magia estadística: crosstab cuenta cuántas veces pasamos del estado A al B.
            # normalize='index' lo convierte en porcentajes reales de probabilidad (0 a 1).
            matriz = pd.crosstab(df_clean[pos], df_clean[f'next_{pos}'], normalize='index')
            
            self.matrices_transicion[pos] = matriz

    def predecir_markov(self, ultimo_sorteo):
        """
        Dado el último sorteo, predice el número más probable de salir.
        """
        prediccion = ""
        probabilidades = []

        for pos in self.posiciones:
            estado_actual = ultimo_sorteo[pos]
            matriz = self.matrices_transicion.get(pos)
            
            if matriz is not None and estado_actual in matriz.index:
                # Extraemos la fila de probabilidades para el dígito que cayó ayer
                probabilidades_transicion = matriz.loc[estado_actual]
                
                # Buscamos el dígito con la probabilidad MÁS ALTA de seguirle
                siguiente_estado = probabilidades_transicion.idxmax()
                prob_max = probabilidades_transicion.max()
                
                prediccion += str(int(siguiente_estado))
                probabilidades.append(prob_max)
            else:
                prediccion += "0"
                probabilidades.append(0.0)

        # Calculamos la probabilidad combinada media
        confianza_media = (sum(probabilidades) / len(probabilidades)) * 100 if probabilidades else 0
        
        return prediccion, confianza_media