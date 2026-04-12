import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class ChartView:
    @staticmethod
    def mostrar_heatmap(df_numeros):
        """Muestra el mapa de calor de las 4 posiciones del billete."""
        print("📈 Abriendo el mapa de calor...")
        
        df_numeros['Posición 1 (Miles)'] = df_numeros['numero'].str[0].astype(int)
        df_numeros['Posición 2 (Centenas)'] = df_numeros['numero'].str[1].astype(int)
        df_numeros['Posición 3 (Decenas)'] = df_numeros['numero'].str[2].astype(int)
        df_numeros['Posición 4 (Unidades)'] = df_numeros['numero'].str[3].astype(int)
        
        matriz_frecuencia = pd.DataFrame(index=range(10))
        columnas_posicion = ['Posición 1 (Miles)', 'Posición 2 (Centenas)', 'Posición 3 (Decenas)', 'Posición 4 (Unidades)']
        
        for col in columnas_posicion:
            conteo = df_numeros[col].value_counts()
            matriz_frecuencia[col] = matriz_frecuencia.index.map(conteo).fillna(0)
            
        plt.figure(figsize=(12, 8))
        sns.heatmap(matriz_frecuencia, annot=True, fmt="g", cmap="YlOrRd", linewidths=.5, cbar_kws={'label': 'Frecuencia de aparición'})
        
        plt.title('🔥 Mapa de Calor: Frecuencia de Dígitos por Posición', fontsize=16, fontweight='bold')
        plt.xlabel('Posición en el Billete', fontsize=12)
        plt.ylabel('Dígito (0 - 9)', fontsize=12)
        plt.yticks(rotation=0) 
        plt.tight_layout()
        plt.show()