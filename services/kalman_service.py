import pandas as pd
import numpy as np
from pykalman import KalmanFilter

class KalmanService:
    def predecir_tendencia(self, df, ventana=50):
        """
        Usa el Filtro de Kalman para suavizar el ruido estocástico y predecir
        la tendencia subyacente del próximo número para cada balotera.
        """
        # Ordenamos cronológicamente
        df = df.sort_values('fecha_sorteo').reset_index(drop=True)
        
        # Tomamos una ventana de los últimos N sorteos (ej. 50 semanas)
        # No usamos los 14,000 para que el filtro pueda reaccionar a tendencias recientes
        df_reciente = df.tail(ventana)
        
        prediccion_final = ""
        detalles_tendencia = []
        
        posiciones = ['balota_1', 'balota_2', 'balota_3', 'balota_4']
        
        for pos in posiciones:
            # Nuestra "señal ruidosa" son los números que caen
            mediciones = df_reciente[pos].values
            
            # Configuración del Filtro 1D
            kf = KalmanFilter(
                transition_matrices=[1],      # A: La inercia del sistema
                observation_matrices=[1],     # H: Observamos el estado directamente
                initial_state_mean=mediciones[0],
                initial_state_covariance=1,
                observation_covariance=10,    # R: Alto ruido (es una lotería, hay mucho azar)
                transition_covariance=1       # Q: El "estado real" de la máquina cambia lentamente
            )
            
            # Aplicamos el filtro para encontrar la señal limpia
            state_means, _ = kf.filter(mediciones)
            
            # El estado en el tiempo t_actual nos da la inercia hacia t+1
            tendencia_continua = state_means[-1][0]
            
            # Discretizamos (redondeamos) al dígito de la balota
            siguiente_digito = int(round(tendencia_continua))
            # Aseguramos que se mantenga en los límites físicos (0-9)
            siguiente_digito = max(0, min(9, siguiente_digito))
            
            prediccion_final += str(siguiente_digito)
            detalles_tendencia.append(tendencia_continua)
            
        return prediccion_final, detalles_tendencia