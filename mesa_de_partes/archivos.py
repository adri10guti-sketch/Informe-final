# -*- coding: utf-8 -*-
"""
archivos.py
-----------
Persistencia de datos en un archivo de texto (expedientes.txt).

Formato: un registro por línea, con 11 campos separados por '|':

ING-0001|F001-00123|14/10/2026|Distribuidora|20123456789|Baptrin|L2406|EN-12345|10|5.00|03/2028

Orden de los campos:
código | factura | fecha recepción | distribuidora | RUC ('-' si no tiene) |
producto | lote | registro sanitario | cantidad | precio | vencimiento (MM/AAAA)
"""
import os
import shutil

import registros as reg

NOMBRE_ARCHIVO = "expedientes.txt"
# El archivo se guarda junto a los scripts, sin importar desde dónde se ejecute.
RUTA_ARCHIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), NOMBRE_ARCHIVO)
SEPARADOR = "|"
CAMPOS_POR_LINEA = 11


def guardar_datos(ruta=RUTA_ARCHIVO):
    """Escribe todos los registros en el archivo.

    Primero escribe en un archivo temporal y luego lo reemplaza, de modo que si
    algo falla a mitad de la escritura el archivo anterior no se daña.
    Devuelve (ok, mensaje).
    """
    ruta_temporal = ruta + ".tmp"
    try:
        with open(ruta_temporal, "w", encoding="utf-8") as archivo:
            for i in range(reg.total()):
                campos = [reg.codigos[i], reg.facturas[i], reg.fechas_recepcion[i],
                          reg.distribuidoras[i], reg.rucs[i], reg.productos[i],
                          reg.lotes[i], reg.registros_sanitarios[i],
                          str(reg.cantidades[i]), f"{reg.precios[i]:.2f}",
                          reg.vencimientos[i]]
                archivo.write(SEPARADOR.join(campos) + "\n")
        os.replace(ruta_temporal, ruta)
    except OSError as error:
        try:
            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)
        except OSError:
            pass
        return False, f"No se pudo guardar el archivo: {error}"
    total = reg.total()
    palabra = "registro" if total == 1 else "registros"
    return True, f"Datos guardados en {os.path.basename(ruta)} ({total} {palabra})."


def cargar_datos(ruta=RUTA_ARCHIVO):
    """Lee el archivo y llena los arreglos.

    Devuelve (ok, cargados, omitidas, mensajes):
        ok        False solo si el archivo existe pero no se pudo leer (en ese
                  caso los arreglos NO se tocan, para no perder datos).
        cargados  registros válidos leídos.
        omitidas  líneas rechazadas (campos incompletos, datos inválidos o
                  código repetido).
        mensajes  explicación de cada problema encontrado.
    """
    if not os.path.exists(ruta):
        return True, 0, 0, [f"No se encontró {os.path.basename(ruta)}; se creará al guardar."]

    try:
        # utf-8-sig tolera archivos guardados con BOM (algunas versiones del Bloc de notas)
        with open(ruta, "r", encoding="utf-8-sig") as archivo:
            lineas = archivo.readlines()
    except (OSError, UnicodeDecodeError) as error:
        return False, 0, 0, [f"No se pudo leer {os.path.basename(ruta)}: {error}"]

    reg.limpiar()
    cargados = 0
    omitidas = 0
    mensajes = []

    for numero, linea in enumerate(lineas, start=1):
        linea = linea.strip()
        if linea == "":
            continue                                   # línea en blanco: se ignora
        campos = linea.split(SEPARADOR)
        if len(campos) != CAMPOS_POR_LINEA:
            omitidas += 1
            mensajes.append(f"Línea {numero} omitida: se esperaban {CAMPOS_POR_LINEA} "
                            f"campos y hay {len(campos)}.")
            continue
        ok, texto = reg.agregar_registro(*campos)
        if ok:
            cargados += 1
        else:
            omitidas += 1
            mensajes.append(f"Línea {numero} omitida: {texto}")

    if omitidas > 0:
        # Al guardar de nuevo, las líneas omitidas desaparecerían: se conserva una copia.
        try:
            shutil.copyfile(ruta, ruta + ".respaldo")
            mensajes.append(f"Se guardó una copia del archivo original en "
                            f"{os.path.basename(ruta)}.respaldo")
        except OSError:
            mensajes.append("No se pudo crear la copia de respaldo del archivo original.")

    return True, cargados, omitidas, mensajes
