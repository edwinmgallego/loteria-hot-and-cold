# 🎲 Lotería del Valle: Data Engineering & Statistical Analysis (Hot & Cold Numbers)

Este proyecto es un pipeline completo de Ingeniería de Datos (ETL) y Análisis Estadístico (EDA) diseñado para extraer, almacenar y analizar el histórico completo de resultados de la Lotería del Valle (Colombia). 

El objetivo principal es descubrir patrones de frecuencia, identificando los números y series más "calientes" (que más caen) y los más "fríos" (los menos frecuentes), culminando en un algoritmo de recomendación basado en probabilidad histórica.

---

## 🚀 Características Principales

* **Ingeniería Inversa de API:** En lugar de hacer *web scraping* tradicional sobre HTML, el proyecto intercepta y consume directamente la API interna (`revisar_controlador.php`), reduciendo el tiempo de extracción de horas a segundos.
* **Pipeline ETL (Extract, Transform, Load):** * **Extracción:** Consumo masivo de payloads JSON vía peticiones HTTP POST.
  * **Transformación:** Limpieza de datos, formateo de fechas y descomposición de cifras usando Pandas.
  * **Carga:** Inserción eficiente en una base de datos relacional MySQL usando `INSERT IGNORE` para evitar duplicados y ejecuciones masivas (`executemany`).
* **Análisis Exploratorio de Datos (EDA):** Generación de gráficas de barras, análisis top 20 y Mapas de Calor (Heatmaps) con Seaborn/Matplotlib.
* **Sistema de Recomendación:** Un script generador de jugadas que utiliza combinatoria para proponer billetes con los dígitos con mayor y menor probabilidad histórica.

---

## 🛠️ Requisitos Previos

Asegúrate de tener instalado en tu máquina:
* **Python 3.10 o superior**
* **MySQL Server** (Puede ser a través de XAMPP, MySQL Workbench o servicio nativo)
* **Git**

---

## ⚙️ Guía de Instalación y Configuración Paso a Paso

### Paso 1: Configurar el archivo `.gitignore`
Antes de inicializar cualquier repositorio, es **crítico** crear un archivo llamado exactamente `.gitignore` en la raíz de tu proyecto para no subir contraseñas ni archivos pesados. Crea el archivo y pega esto dentro:

```text
# Entornos virtuales de Python
venv/
env/
__pycache__/
*.pyc

# Variables de entorno y credenciales (¡CRÍTICO!)
.env

# Archivos descargados y bases de datos locales
pdfs_loteria/
*.pdf
*.db
*.sqlite3

# Configuraciones de editores
.vscode/
.idea/