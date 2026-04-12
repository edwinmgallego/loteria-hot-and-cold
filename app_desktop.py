import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

        # 2. Crear Pestañas (Tabs)
        self.tabview = ctk.CTkTabview(self, width=650, height=500)
        self.tabview.pack(pady=10, padx=10)

        self.tab_scraping = self.tabview.add("🔄 Scraping")
        self.tab_recomendar = self.tabview.add("🎯 Recomendaciones")
        self.tab_historico = self.tabview.add("📜 Mi Histórico")

        self.construir_tab_scraping()
        self.construir_tab_recomendar()
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

    def ejecutar_scraping(self):
        self.txt_log_scraping.insert("end", "Conectando a la API...\n")
        self.update() # Refresca la interfaz
        
        try:
            datos_api = self.scraper.obtener_sorteos_recientes()
            ultimo = self.modelo.obtener_ultimo_sorteo_guardado()
            
            nuevos = []
            for item in datos_api:
                if int(item['sorteo']) > ultimo:
                    nuevos.append((item['sorteo'], item['fecha'].split(' ')[0], item['mayor']['resultado'], item['mayor']['serie'], None))
            
            insertados = self.modelo.guardar_sorteos_nuevos(nuevos)
            
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

        # Consola de resultados
        self.txt_resultados = ctk.CTkTextbox(self.tab_recomendar, width=600, height=350, font=("Consolas", 14))
        self.txt_resultados.pack(pady=10)

    def ejecutar_recomendacion(self):
        self.txt_resultados.delete("1.0", "end") # Limpiar caja
        self.txt_resultados.insert("end", "Analizando más de 14,000 registros...\n\n")
        self.update()

        df_n, df_s = self.modelo.obtener_datos_para_analisis()
        grupos = self.analizador.generar_frecuencias(df_n, df_s)
        
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
        df_n, _ = self.modelo.obtener_datos_para_analisis()
        df_n['Posición 1 (Miles)'] = df_n['numero'].str[0].astype(int)
        df_n['Posición 2 (Centenas)'] = df_n['numero'].str[1].astype(int)
        df_n['Posición 3 (Decenas)'] = df_n['numero'].str[2].astype(int)
        df_n['Posición 4 (Unidades)'] = df_n['numero'].str[3].astype(int)
        
        matriz = pd.DataFrame(index=range(10))
        cols = ['Posición 1 (Miles)', 'Posición 2 (Centenas)', 'Posición 3 (Decenas)', 'Posición 4 (Unidades)']
        for col in cols:
            conteo = df_n[col].value_counts()
            matriz[col] = matriz.index.map(conteo).fillna(0)
            
        plt.figure(figsize=(10, 6))
        sns.heatmap(matriz, annot=True, fmt="g", cmap="YlOrRd", linewidths=.5)
        plt.title('Frecuencia de Dígitos por Posición')
        plt.show() # Esto abre la ventana nativa de matplotlib automáticamente

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
        query = "SELECT numero, serie, fecha_hora FROM recomendaciones_loteria ORDER BY fecha_hora DESC LIMIT 30"
        try:
            df = pd.read_sql(query, self.modelo.conexion)
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