from config.database import obtener_conexion
from controllers.main_controller import MainController

def main():
    conexion = obtener_conexion()
    if not conexion: return
    
    ctrl = MainController(conexion)
    
    while True:
        print("\n=== 🎲 LOTERÍA ANALYZER MVC 🎲 ===")
        print("1. Buscar nuevos sorteos (Actualizar BD)")
        print("2. Generar Recomendaciones (Híbridas)")
        print("3. Ver Mapa de Calor (Gráfica)")
        print("4. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            ctrl.actualizar_base_datos()
        elif opcion == "2":
            ctrl.generar_recomendaciones()
        elif opcion == "3":
            ctrl.mostrar_graficas_calor()
        elif opcion == "4":
            print("\n¡Buena suerte! 🍀")
            break
        else:
            print("❌ Opción no válida.")

    # Cerrar conexión al salir del programa
    if conexion and conexion.is_connected():
        conexion.close()

if __name__ == "__main__":
    main()