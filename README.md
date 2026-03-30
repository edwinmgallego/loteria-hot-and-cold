# 🎲 Lotería del Valle: Data Engineering & Statistical Analysis (Hot & Cold Numbers)

Este proyecto es un pipeline completo de Ingeniería de Datos (ETL) y Análisis Estadístico (EDA) diseñado para extraer, almacenar y analizar el histórico completo de resultados de la Lotería del Valle (Colombia).

El objetivo principal es descubrir patrones de frecuencia, identificando los números y series más "calientes" (que más caen) y los más "fríos" (los menos frecuentes), culminando en un algoritmo de recomendación basado en probabilidad histórica.

## 🚀 Características Principales

* **Ingeniería Inversa de API:** En lugar de hacer *web scraping* tradicional sobre HTML renderizado por JavaScript, el proyecto intercepta y consume directamente la API oculta del servidor (`revisar_controlador.php`), reduciendo el tiempo de extracción de horas a segundos.
* **Pipeline ETL (Extract, Transform, Load):** * **Extracción:** Consumo masivo de payloads JSON vía peticiones HTTP POST.
  * **Transformación:** Limpieza de datos, formateo de fechas y descomposición de cifras usando Pandas.
  * **Carga:** Inserción eficiente en una base de datos relacional MySQL usando `INSERT IGNORE` para evitar duplicados y `Ejecuciones Masivas` (executemany).
* **Análisis Exploratorio de Datos (EDA):** Generación de gráficas de barras, análisis top 20 y Mapas de Calor (Heatmaps) para visualizar la distribución estadística de los números ganadores.
* **Sistema de Recomendación:** Un script generador de jugadas que utiliza combinatoria y los hallazgos estadísticos para proponer billetes con los dígitos más "calientes".

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Bases de Datos:** MySQL
* **Librerías Core:** `requests`, `mysql-connector-python`, `SQLAlchemy`, `python-dotenv`
* **Librerías de Análisis y Visualización:** `pandas`, `matplotlib`, `seaborn`

## 📂 Estructura de la Base de Datos

El proyecto utiliza un modelo relacional sencillo pero robusto:
1. `sorteos_loteria_valle`: Almacena el Premio Mayor y los metadatos del sorteo (Fecha, Ruta del PDF oficial).
2. `premios_secos_valle`: Tabla hija vinculada por Foreign Key que almacena los miles de premios menores asociados a cada sorteo.

## ⚙️ Instalación y Configuración Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/loteria-hot-and-cold.git](https://github.com/tu-usuario/loteria-hot-and-cold.git)
   cd loteria-hot-and-cold