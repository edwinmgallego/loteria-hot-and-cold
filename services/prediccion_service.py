import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import datetime

class PrediccionService:
    def __init__(self):
        # Nombres actualizados a las nuevas balotas atómicas
        self.columnas_y = ['balota_1', 'balota_2', 'balota_3', 'balota_4']
        self.modelos = {
            col: RandomForestClassifier(n_estimators=100, random_state=42) 
            for col in self.columnas_y
        }

    def preparar_datos(self, df):
        """Feature Engineering avanzado con la nueva tabla de balotas"""
        df['fecha_sorteo'] = pd.to_datetime(df['fecha_sorteo'])
        
        # Variables de tiempo básicas
        df['dia'] = df['fecha_sorteo'].dt.day
        df['mes'] = df['fecha_sorteo'].dt.month
        df['dia_semana'] = df['fecha_sorteo'].dt.dayofweek
        
        # --- NUEVA CARACTERÍSTICA: LAGS (Memoria) ---
        for i in range(1, 5):
            df[f'lag_b{i}'] = df[f'balota_{i}'].shift(1)
            
        df = df.dropna()
        return df

    def entrenar_modelos(self, df_preparado):
        """Entrena usando las características de tiempo y la memoria del sorteo anterior"""
        X = df_preparado[['dia', 'mes', 'dia_semana', 'lag_b1', 'lag_b2', 'lag_b3', 'lag_b4']]
        
        resultados = {}
        for col in self.columnas_y:
            y = df_preparado[col]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.modelos[col].fit(X_train, y_train)
            pred = self.modelos[col].predict(X_test)
            resultados[col] = accuracy_score(y_test, pred)
            
        return resultados

    def realizar_backtesting(self, df_preparado, ultimos_sorteos=50):
        """Backtesting actualizado con Lags y Balotas"""
        df = df_preparado.sort_values('fecha_sorteo').reset_index(drop=True)
        historico_train = df.iloc[:-ultimos_sorteos]
        simulacion_test = df.iloc[-ultimos_sorteos:]
        
        X_train = historico_train[['dia', 'mes', 'dia_semana', 'lag_b1', 'lag_b2', 'lag_b3', 'lag_b4']]
        
        for pos in self.columnas_y:
            self.modelos[pos].fit(X_train, historico_train[pos])
            
        resultados_simulacion = []
        dinero_invertido = 0
        dinero_ganado = 0 
        
        for index, fila in simulacion_test.iterrows():
            X_prueba = pd.DataFrame({
                'dia': [fila['dia']], 
                'mes': [fila['mes']], 
                'dia_semana': [fila['dia_semana']],
                'lag_b1': [fila['lag_b1']],
                'lag_b2': [fila['lag_b2']],
                'lag_b3': [fila['lag_b3']],
                'lag_b4': [fila['lag_b4']]
            })
            
            prediccion_ia = ""
            for pos in self.columnas_y:
                prediccion_ia += str(int(self.modelos[pos].predict(X_prueba)[0]))
            
            resultado_real = str(int(fila['balota_1'])) + str(int(fila['balota_2'])) + str(int(fila['balota_3'])) + str(int(fila['balota_4']))
            
            digitos_acertados = sum(1 for a, b in zip(prediccion_ia, resultado_real) if a == b)
            
            dinero_invertido += 2000
            if digitos_acertados == 4:
                dinero_ganado += 4500000 * 2
            elif digitos_acertados == 3:
                dinero_ganado += 400000 * 2
            
            resultados_simulacion.append({
                'fecha': fila['fecha_sorteo'].strftime('%Y-%m-%d'),
                'ia': prediccion_ia,
                'real': resultado_real,
                'aciertos': digitos_acertados
            })
            
        return resultados_simulacion, dinero_invertido, dinero_ganado

    def predecir_proximo_sorteo(self, df_preparado):
        """Predicción de hoy usando los datos del sorteo de ayer (Lags)"""
        hoy = datetime.datetime.now()
        
        # Extraemos el último sorteo de la base de datos para usarlo como memoria
        ultimo_sorteo = df_preparado.iloc[-1]
        
        X_hoy = pd.DataFrame({
            'dia': [hoy.day],
            'mes': [hoy.month],
            'dia_semana': [hoy.weekday()],
            'lag_b1': [ultimo_sorteo['balota_1']],
            'lag_b2': [ultimo_sorteo['balota_2']],
            'lag_b3': [ultimo_sorteo['balota_3']],
            'lag_b4': [ultimo_sorteo['balota_4']]
        })
        
        numero_predicho = ""
        probabilidades = []
        
        for pos in self.columnas_y:
            digito = self.modelos[pos].predict(X_hoy)[0]
            numero_predicho += str(int(digito))
            
            proba = self.modelos[pos].predict_proba(X_hoy)[0].max()
            probabilidades.append(proba)
            
        confianza_promedio = sum(probabilidades) / len(probabilidades)
        return numero_predicho, confianza_promedio