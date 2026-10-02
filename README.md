# Reordenar carpetas

Ordena los archivos de una carpeta en subcarpetas según su tipo (PDFs, Imágenes, Videos, etc.).

## Uso rápido

- **Doble clic en `organizar.bat`** → ordena tu carpeta de Descargas.
- **Arrastrar una carpeta sobre `organizar.bat`** → ordena esa carpeta.

## Desde la terminal

```
python organizar.py                     # ordena Descargas
python organizar.py "D:\Mis cosas"      # ordena otra carpeta
python organizar.py --simular           # muestra qué haría, sin mover nada
python organizar.py --deshacer          # revierte el último ordenamiento
```

## Ejecución automática

Hay una tarea en el Programador de tareas de Windows llamada **"Ordenar Descargas"** que corre
todos los días a las 13:00 (si la PC estaba apagada, corre apenas se prende). Para cambiar la hora
o desactivarla, abrí el Programador de tareas y buscala por nombre. Para borrarla:

```
schtasks /Delete /TN "Ordenar Descargas" /F
```

## Detalles

- Las categorías se editan en `categorias.json` (nombre de carpeta → extensiones).
  Lo que no coincide con ninguna va a `Otros`.
- Solo mueve archivos sueltos en la carpeta; no toca subcarpetas existentes.
- Si ya existe un archivo con el mismo nombre en el destino, lo renombra a `nombre (1).ext`.
- Ignora descargas en curso (`.crdownload`, `.part`, `.tmp`), accesos directos y archivos del sistema.
- Cada ordenamiento guarda un registro oculto (`.organizador_registro.json`) en la carpeta,
  que es lo que usa `--deshacer`.
