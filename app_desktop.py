import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# --- EN LA SECCIÓN DE IMPORTACIONES (Arriba) ---
from services.prediccion_service import PrediccionService
from services.markov_service import MarkovService # <--- ¡NUEVA LÍNEA!
from services.benford_service import BenfordService

# Importamos tu backend MVC intacto
from config.database import obtener_conexion
from models.loteria_model import LoteriaModel
from services.scraper_service import ScraperService
from services.analizador_service import AnalizadorService

# Configuración visual de la App
ctk.set_appearance_mode("dark")  # Modo oscuro por defecto
ctk.set_default_color_theme("blue")  # Tema de colores

class LoteriaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎲 Lotería Analyzer - Data Engineering")
        self.geometry("700x550")
        self.resizable(False, False)

        # 1. Iniciar Backend
        conexion = obtener_conexion()
        if not conexion:
            messagebox.showerror("Error", "No hay conexión a la Base de Datos.")
            self.destroy()
            return
            
        self.modelo = LoteriaModel(conexion)
        self.scraper = ScraperService()
        self.analizador = AnalizadorService()
        self.prediccion = PrediccionService() # <--- ¡NUEVA LÍNEA!
        self.markov = MarkovService() # <--- ¡NUEVA LÍNEA!
        self.benford = BenfordService()

        # 2. Crear Pestañas (Tabs)
        self.tabview = ctk.CTkTabview(self, width=650, height=500)
        self.tabview.pack(pady=10, padx=10)

        self.tab_scraping = self.tabview.add("🔄 Scraping")
        self.tab_recomendar = self.tabview.add("🎯 Recomendaciones")
        self.tab_ia = self.tabview.add("🧠 IA Predictiva") # <--- ¡NUEVA PESTAÑA!
        self.tab_historico = self.tabview.add("📜 Mi Histórico")

        self.construir_tab_scraping()
        self.construir_tab_recomendar()
        self.construir_tab_ia() # <--- ¡NUEVA LÍNEA!
        self.construir_tab_historico()

    # ==========================================
    # PESTAÑA 1: SCRAPING
    # ==========================================
    def construir_tab_scraping(self):
        lbl_titulo = ctk.CTkLabel(self.tab_scraping, text="Sincronización de Base de Datos", font=("Arial", 20, "bold"))
        lbl_titulo.pack(pady=20)

        lbl_desc = ctk.CTkLabel(self.tab_scraping, text="Conéctate a la API oculta y descarga los sorteos más recientes.")
        lbl_desc.pack(pady=10)

        self.btn_scraping = ctk.CTkButton(self.tab_scraping, text="📥 Iniciar Descarga", command=self.ejecutar_scraping)
        self.btn_scraping.pack(pady=20)

        self.txt_log_scraping = ctk.CTkTextbox(self.tab_scraping, width=500, height=200)
        self.txt_log_scraping.pack(pady=10)
    # ==========================================
    # PESTAÑA NUEVA: INTELIGENCIA ARTIFICIAL
    # ==========================================
    def construir_tab_ia(self):
        lbl_titulo = ctk.CTkLabel(self.tab_ia, text="Motor Predictivo: Random Forest", font=("Arial", 20, "bold"))
        lbl_titulo.pack(pady=10)

        lbl_desc = ctk.CTkLabel(self.tab_ia, text="Entrena 4 redes de Bosques Aleatorios para encontrar estacionalidades.")
        lbl_desc.pack(pady=5)

        self.btn_entrenar = ctk.CTkButton(self.tab_ia, text="🧠 Entrenar IA y Predecir", command=self.ejecutar_ia, fg_color="purple", hover_color="darkviolet")
        self.btn_entrenar.pack(pady=15)
        # NUEVO BOTÓN DE MARKOV
        self.btn_markov = ctk.CTkButton(self.tab_ia, text="🔗 Predecir con Cadenas de Markov", command=self.ejecutar_markov, fg_color="teal", hover_color="darkcyan")
        self.btn_markov.pack(pady=5)
        self.txt_log_ia = ctk.CTkTextbox(self.tab_ia, width=600, height=300, font=("Consolas", 14))
        self.txt_log_ia.pack(pady=10)
        # En def construir_tab_ia(self): (Agrega esto antes del txt_log_ia)
        self.btn_backtesting = ctk.CTkButton(self.tab_ia, text="⏱️ Iniciar Backtesting (Últimos 50 sorteos)", command=self.ejecutar_backtesting, fg_color="blue", hover_color="darkblue")
        self.btn_backtesting.pack(pady=5)
    def ejecutar_backtesting(self):
        self.btn_backtesting.configure(state="disabled", text="Simulando...")
        self.txt_log_ia.delete("1.0", "end")
        self.txt_log_ia.insert("end", "⏱️ Iniciando Máquina del Tiempo de Backtesting...\n")
        self.update()
        
        try:
            df = self.modelo.obtener_datos_para_analisis()
            df_preparado = self.prediccion.preparar_datos(df)
            
            self.txt_log_ia.insert("end", "📉 Simulando inversiones en los últimos 50 sorteos...\n\n")
            self.update()
            
            resultados, invertido, ganado = self.prediccion.realizar_backtesting(df_preparado, ultimos_sorteos=50)
            
            # Mostrar los 10 sorteos más recientes de la simulación
            self.txt_log_ia.insert("end", "ÚLTIMAS 10 SIMULACIONES:\n")
            self.txt_log_ia.insert("end", "FECHA       | IA APUESTA | SALIÓ REAL | ACIERTOS\n")
            self.txt_log_ia.insert("end", "-"*50 + "\n")
            
            for r in resultados[-10:]:
                icono = "✅" if r['aciertos'] > 0 else "❌"
                self.txt_log_ia.insert("end", f"{r['fecha']}  |    {r['ia']}    |    {r['real']}    | {r['aciertos']} {icono}\n")
                
            # Reporte Financiero
            self.txt_log_ia.insert("end", "\n" + "="*50 + "\n")
            self.txt_log_ia.insert("end", "📊 REPORTE FINANCIERO DEL BACKTESTING:\n")
            self.txt_log_ia.insert("end", f"   💸 Dinero Invertido (Simulado): ${invertido:,}\n")
            self.txt_log_ia.insert("end", f"   💰 Dinero Ganado (Simulado):    ${ganado:,}\n")
            
            roi = ((ganado - invertido) / invertido) * 100 if invertido > 0 else 0
            color_roi = "🟢" if roi > 0 else "🔴"
            self.txt_log_ia.insert("end", f"   📈 Retorno de Inversión (ROI):  {roi:.2f}% {color_roi}\n")
            self.txt_log_ia.insert("end", "="*50 + "\n")

        except Exception as e:
            self.txt_log_ia.insert("end", f"\n❌ Error en backtesting: {e}")
        finally:
            self.btn_backtesting.configure(state="normal", text="⏱️ Iniciar Backtesting (Últimos 50 sorteos)")
    def ejecutar_ia(self):
        self.btn_entrenar.configure(state="disabled", text="Entrenando...")
        self.txt_log_ia.delete("1.0", "end")
        self.txt_log_ia.insert("end", "⏳ Extrayendo histórico para entrenamiento...\n")
        self.update() # Forzar actualización visual
        
        try:
            # 1. Obtener datos
            #df_n, _ = self.modelo.obtener_datos_para_analisis()
            df = self.modelo.obtener_datos_para_analisis()
            df_preparado = self.prediccion.preparar_datos(df)
            
            # 2. Preparar datos (Feature Engineering)
            self.txt_log_ia.insert("end", "⚙️ Procesando Feature Engineering (Fechas y posiciones)...\n")
            self.update()
            df_preparado = self.prediccion.preparar_datos(df)
            
            # 3. Entrenar
            self.txt_log_ia.insert("end", "🏋️ Entrenando 4 Modelos de Inteligencia Artificial (Esto puede tardar unos segundos)...\n")
            self.update()
            metricas = self.prediccion.entrenar_modelos(df_preparado)
            
            # 4. Mostrar métricas
            self.txt_log_ia.insert("end", "-"*50 + "\n")
            self.txt_log_ia.insert("end", "📊 RESULTADOS DEL ENTRENAMIENTO (Accuracy):\n")
            for pos, acc in metricas.items():
                self.txt_log_ia.insert("end", f"   - Modelo {pos.upper()}: {acc*100:.2f}% de precisión en el test.\n")
                
            # 5. Predecir
            numero, confianza = self.prediccion.predecir_proximo_sorteo(df_preparado)
            
            self.txt_log_ia.insert("end", "\n" + "="*50 + "\n")
            self.txt_log_ia.insert("end", "🔮 PREDICCIÓN PARA EL DÍA DE HOY:\n\n")
            self.txt_log_ia.insert("end", f"   🎟️ NÚMERO GANADOR CALCULADO: {numero}\n")
            self.txt_log_ia.insert("end", f"   📈 NIVEL DE CONFIANZA DEL MODELO: {confianza*100:.2f}%\n")
            self.txt_log_ia.insert("end", "="*50 + "\n")
            
            # Opcional: Si quieres guardar la predicción de la IA en tu histórico, puedes descomentar esto:
            # self.modelo.guardar_recomendaciones([(numero, "IA")])

        except Exception as e:
            self.txt_log_ia.insert("end", f"\n❌ Ocurrió un error en el entrenamiento: {e}")
        
        finally:
            self.btn_entrenar.configure(state="normal", text="🧠 Entrenar IA y Predecir")
    
    def ejecutar_markov(self):
        self.btn_markov.configure(state="disabled", text="Calculando matrices...")
        self.txt_log_ia.delete("1.0", "end")
        self.txt_log_ia.insert("end", "🔗 Iniciando análisis de Cadenas de Markov...\n")
        self.update()

        try:
            # 1. Traer datos limpios
            df = self.modelo.obtener_datos_para_analisis()
            
            self.txt_log_ia.insert("end", "📊 Extrayendo Matrices de Transición de Estados...\n")
            self.update()
            
            # 2. Entrenar el modelo de Markov
            self.markov.entrenar_markov(df)
            
            # 3. Obtener el último sorteo (nuestro "Estado Actual")
            df_ordenado = df.sort_values('fecha_sorteo').reset_index(drop=True)
            ultimo_sorteo = df_ordenado.iloc[-1]
            numero_real = f"{int(ultimo_sorteo['balota_1'])}{int(ultimo_sorteo['balota_2'])}{int(ultimo_sorteo['balota_3'])}{int(ultimo_sorteo['balota_4'])}"
            
            self.txt_log_ia.insert("end", f"⬅️ Estado Inicial: El último sorteo fue {numero_real}\n")
            self.txt_log_ia.insert("end", "🔍 Calculando el salto probabilístico más frecuente...\n")
            self.update()
            
            # 4. Predecir
            numero_predicho, confianza = self.markov.predecir_markov(ultimo_sorteo)
            
            self.txt_log_ia.insert("end", "\n" + "="*50 + "\n")
            self.txt_log_ia.insert("end", "🔮 PREDICCIÓN CON CADENAS DE MARKOV:\n\n")
            self.txt_log_ia.insert("end", f"   🎟️ NÚMERO DE MAYOR TRANSICIÓN: {numero_predicho}\n")
            self.txt_log_ia.insert("end", f"   📈 PROBABILIDAD DE LA RUTA: {confianza:.2f}%\n")
            self.txt_log_ia.insert("end", "="*50 + "\n")
            
        except Exception as e:
            self.txt_log_ia.insert("end", f"\n❌ Error en Markov: {e}")
        finally:
            self.btn_markov.configure(state="normal", text="🔗 Predecir con Cadenas de Markov")
    
    
    def ejecutar_scraping(self):
        self.txt_log_scraping.insert("end", "Conectando a la API...\n")
        self.update() 
        
        try:
            datos_api = self.scraper.obtener_sorteos_recientes()
            ultimo = self.modelo.obtener_ultimo_sorteo_guardado()
            
            datos_crudos = []
            datos_atomicos = []
            
            for item in datos_api:
                if int(item['sorteo']) > ultimo:
                    # Rellenar con ceros si el número es corto
                    num = str(item['mayor']['resultado']).zfill(4)
                    ser = str(item['mayor']['serie']).zfill(3)
                    
                    # 1. Lista para la tabla original (Cruda)
                    datos_crudos.append((
                        item['sorteo'], 
                        item['fecha'].split(' ')[0], 
                        num, 
                        ser, 
                        None
                    ))
                    
                    # 2. Lista para la nueva tabla (Atómica/Balotas separadas)
                    datos_atomicos.append((
                        item['sorteo'],
                        num[0], num[1], num[2], num[3], # Balotas del número
                        ser[0], ser[1], ser[2]          # Balotas de la serie
                    ))
            
            # Enviamos ambas listas al modelo
            insertados = self.modelo.guardar_sorteos_nuevos(datos_crudos, datos_atomicos)
            
            log = f"✅ Descarga completada.\nSorteos analizados: {len(datos_api)}\nNuevos guardados: {insertados}\n"
            self.txt_log_scraping.insert("end", log)
            messagebox.showinfo("Éxito", "Base de datos actualizada.")
        except Exception as e:
            messagebox.showerror("Error", f"Falló el scraping: {e}")

    # ==========================================
    # PESTAÑA 2: RECOMENDACIONES & GRÁFICAS
    # ==========================================
    def construir_tab_recomendar(self):
        # Botones superiores
        frame_botones = ctk.CTkFrame(self.tab_recomendar)
        frame_botones.pack(pady=10, fill="x", padx=20)

        btn_generar = ctk.CTkButton(frame_botones, text="🎲 Generar Jugadas Híbridas", command=self.ejecutar_recomendacion, fg_color="green", hover_color="darkgreen")
        btn_generar.pack(side="left", padx=10, expand=True)

        btn_grafica = ctk.CTkButton(frame_botones, text="🔥 Ver Mapa de Calor", command=self.mostrar_heatmap, fg_color="orange", hover_color="darkorange")
        btn_grafica.pack(side="right", padx=10, expand=True)

    # NUEVO BOTÓN
        btn_benford = ctk.CTkButton(frame_botones, text="🕵️ Auditoría Benford", command=self.mostrar_anomalias_benford, fg_color="darkred", hover_color="maroon")
        btn_benford.pack(side="left", padx=5, expand=True)
        # Consola de resultados
        self.txt_resultados = ctk.CTkTextbox(self.tab_recomendar, width=600, height=350, font=("Consolas", 14))
        self.txt_resultados.pack(pady=10)

    def ejecutar_recomendacion(self):
        self.txt_resultados.delete("1.0", "end") 
        self.txt_resultados.insert("end", "Analizando más de 14,000 registros...\n\n")
        self.update()

        # CAMBIO AQUÍ: Ahora recibimos un solo DataFrame con todo integrado
        df = self.modelo.obtener_datos_para_analisis()
        grupos = self.analizador.generar_frecuencias(df)
        
        # Guardar en BD
        recomendadas = self.analizador.crear_jugadas_hibridas(grupos, cantidad=5)
        self.modelo.guardar_recomendaciones(recomendadas)

        # Mostrar en pantalla
        self.txt_resultados.insert("end", f"🔥 CALIENTES: Num {grupos['num']['calientes']} | Serie {grupos['ser']['calientes']}\n")
        self.txt_resultados.insert("end", f"❄️ FRÍOS:     Num {grupos['num']['frios']} | Serie {grupos['ser']['frios']}\n")
        self.txt_resultados.insert("end", "-"*50 + "\n")
        self.txt_resultados.insert("end", "🎯 TUS JUGADAS RECOMENDADAS:\n\n")

        for i, (num, ser) in enumerate(recomendadas, 1):
            self.txt_resultados.insert("end", f"   🎫 Billete {i}: Número {num} - Serie {ser}\n")
            
        self.txt_resultados.insert("end", "\n✅ Se han guardado en tu historial.")

    def mostrar_heatmap(self):
        # CAMBIO AQUÍ: Recibimos un solo df y usamos las nuevas columnas
        df = self.modelo.obtener_datos_para_analisis()
        
        matriz = pd.DataFrame(index=range(10))
        # Mapeamos los nombres de la BD a los nombres bonitos para la gráfica
        cols = {
            'balota_1': 'Posición 1 (Miles)', 
            'balota_2': 'Posición 2 (Centenas)', 
            'balota_3': 'Posición 3 (Decenas)', 
            'balota_4': 'Posición 4 (Unidades)'
        }
        
        for col_db, col_nombre in cols.items():
            conteo = df[col_db].value_counts()
            matriz[col_nombre] = matriz.index.map(conteo).fillna(0)
            
        plt.figure(figsize=(10, 6))
        import seaborn as sns # Por si no estaba importado a nivel local
        import matplotlib.pyplot as plt
        sns.heatmap(matriz, annot=True, fmt="g", cmap="YlOrRd", linewidths=.5)
        plt.title('Frecuencia de Dígitos por Posición (Balotas Atómicas)')
        plt.show()


    def mostrar_anomalias_benford(self):
        try:
            df = self.modelo.obtener_datos_para_analisis()
            df_benford = self.benford.analizar_distribucion(df)
            
            plt.figure(figsize=(10, 6))
            
            # 1. Pintamos la realidad de la lotería (Barras)
            plt.bar(df_benford['digito'], df_benford['real'], color='skyblue', label='Realidad (Lotería del Valle)', alpha=0.7)
            
            # 2. Pintamos la Ley de Benford (Línea roja)
            plt.plot(df_benford['digito'], df_benford['benford'], color='red', marker='o', linestyle='-', linewidth=2, label='Curva de Benford (Naturaleza)')
            
            # 3. Pintamos la Línea Uniforme (Línea verde punteada)
            plt.axhline(y=11.11, color='green', linestyle='--', linewidth=2, label='Distribución Uniforme (Teoría Ideal)')
            
            plt.title("Auditoría de Anomalías: Primer Dígito vs Ley de Benford", fontsize=14, pad=15)
            plt.xlabel("Primer Dígito (1-9)")
            plt.ylabel("Frecuencia de Aparición (%)")
            plt.xticks(range(1, 10))
            plt.legend()
            plt.grid(axis='y', linestyle=':', alpha=0.6)
            
            # Etiquetamos las barras con su porcentaje real
            for i, val in enumerate(df_benford['real']):
                plt.text(i + 1, val + 0.5, f"{val:.1f}%", ha='center', fontsize=9)
                
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la gráfica: {e}")
    # ==========================================
    # PESTAÑA 3: HISTÓRICO
    # ==========================================
    def construir_tab_historico(self):
        btn_refresh = ctk.CTkButton(self.tab_historico, text="🔄 Actualizar Historial", command=self.cargar_historico)
        btn_refresh.pack(pady=10)

        self.txt_historico = ctk.CTkTextbox(self.tab_historico, width=600, height=380, font=("Consolas", 14))
        self.txt_historico.pack(pady=10)
        self.cargar_historico()

    def cargar_historico(self):
        self.txt_historico.delete("1.0", "end")
        
        try:
            # ¡AQUÍ ESTÁ LA MAGIA! Ya no usamos pd.read_sql aquí, 
            # sino que llamamos al modelo que ya tiene SQLAlchemy configurado.
            df = self.modelo.obtener_historico_recomendaciones(limite=30)
            
            if df.empty:
                self.txt_historico.insert("end", "Aún no hay recomendaciones guardadas.")
            else:
                self.txt_historico.insert("end", "FECHA / HORA         | NÚMERO | SERIE\n")
                self.txt_historico.insert("end", "-"*45 + "\n")
                for _, row in df.iterrows():
                    self.txt_historico.insert("end", f"{row['fecha_hora']}  |  {row['numero']}  |  {row['serie']}\n")
        except Exception as e:
            self.txt_historico.insert("end", f"Error cargando historial: {e}")

# ==========================================
# EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    app = LoteriaApp()
    app.mainloop()