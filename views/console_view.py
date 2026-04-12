class ConsoleView:
    @staticmethod
    def mostrar_mensaje(mensaje):
        print(mensaje)
        
    @staticmethod
    def mostrar_resumen_scraping(total_obtenidos, insertados):
        print("\n==================================================")
        print("📊 REPORTE DE ACTUALIZACIÓN DE BASE DE DATOS")
        print(f"📡 Sorteos extraídos de la API: {total_obtenidos}")
        print(f"💾 Sorteos nuevos guardados: {insertados}")
        print(f"⏩ Sorteos ignorados (ya existían): {total_obtenidos - insertados}")
        print("==================================================\n")

    @staticmethod
    def mostrar_grupos_frecuencia(grupos):
        print("\n==================================================")
        print(f"🔥 CALIENTES : Número {grupos['num']['calientes']} | Serie {grupos['ser']['calientes']}")
        print(f"🌤️ TIBIOS    : Número {grupos['num']['tibios']} | Serie {grupos['ser']['tibios']}")
        print(f"❄️ FRÍOS     : Número {grupos['num']['frios']} | Serie {grupos['ser']['frios']}")
        print("==================================================\n")

    @staticmethod
    def mostrar_jugadas_hibridas(jugadas):
        print("🎯🎯 JUGADAS HÍBRIDAS RECOMENDADAS 🎯🎯")
        for i, (num, ser) in enumerate(jugadas, 1):
            print(f"   Opción {i}: Número {num} - Serie {ser}")
        print("==================================================\n")