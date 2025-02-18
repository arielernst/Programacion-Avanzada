import os


ruta_actual = os.getcwd()+"\src"

# Obtiene la ruta de la carpeta anterior (directorio padre de la actual)
ruta_anterior = os.path.dirname(ruta_actual)

print(ruta_actual)