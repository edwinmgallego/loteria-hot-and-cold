import pandas as pd
import numpy as np

class BenfordService:
    def __init__(self):
        # Calculamos la probabilidad de Benford para los dígitos del 1 al 9
        # (Benford clásico no aplica al 0)
        self.benford_probs = {d: np.log10(1 + 1/d) * 100 for d in range(1, 10)}

    def analizar_distribucion(self, df):
        """
        Analiza el primer dígito (balota_1) y lo compara con Benford y la Uniforme.
        """
        # Filtramos el 0 porque Benford se aplica del 1 al 9
        df_filtrado = df[df['balota_1'] != 0]
        
        # Calculamos el porcentaje real de aparición de cada dígito
        conteo_real = df_filtrado['balota_1'].value_counts(normalize=True) * 100
        
        datos_grafica = {
            'digito': [],
            'real': [],
            'benford': [],
            'uniforme': []
        }
        
        for d in range(1, 10):
            datos_grafica['digito'].append(d)
            datos_grafica['real'].append(conteo_real.get(d, 0))
            datos_grafica['benford'].append(self.benford_probs[d])
            datos_grafica['uniforme'].append(11.11) # 100% dividido en 9 dígitos
            
        return pd.DataFrame(datos_grafica)