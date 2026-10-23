# -*- coding: utf-8 -*-
"""
pruebas.py
----------
Pruebas automáticas del prototipo (casos normales, casos límite y casos de error).

Ejecutar:   python pruebas.py

No toca el archivo real expedientes.txt: usa una carpeta temporal.
"""
import os
import sys
import tempfile
from datetime import date

import archivos as arch
import registros as reg
import validaciones as val

resultados = []     # (grupo, descripción, esperado, obtenido, aprobado)


def verificar(grupo, descripcion, obtenido, esperado):
    resultados.append((grupo, descripcion, esperado, obtenido, obtenido == esperado))


def captura(arreglos):
    """Copia el contenido de todos los arreglos paralelos."""
    return [list(a) for a in arreglos]


# ---------------------------------------------------------------------------
# 1. Validaciones
# ---------------------------------------------------------------------------
def probar_validaciones():
    g = "Validación"
    # Código
    verificar(g, "Código ING-0001 válido", val.validar_codigo("ING-0001"), (True, "ING-0001"))
    verificar(g, "Código ING-0000 rechazado", val.validar_codigo("ING-0000")[0], False)
    verificar(g, "Código ING-1 (corto) rechazado", val.validar_codigo("ING-1")[0], False)
    verificar(g, "Código ING-00A1 rechazado", val.validar_codigo("ING-00A1")[0], False)
    verificar(g, "Código XYZ-0001 rechazado", val.validar_codigo("XYZ-0001")[0], False)
    verificar(g, "Normalizar '2' -> ING-0002", val.normalizar_codigo("2"), "ING-0002")
    verificar(g, "Normalizar ' ing-0002 ' -> ING-0002", val.normalizar_codigo(" ing-0002 "), "ING-0002")
    verificar(g, "Normalizar '12345' no se modifica", val.normalizar_codigo("12345"), "12345")

    # Factura
    verificar(g, "Factura F001-00123 válida", val.validar_factura("F001-00123"), (True, "F001-00123"))
    verificar(g, "Factura ' fa01-5 ' se normaliza", val.validar_factura(" fa01-5 "), (True, "FA01-5"))
    verificar(g, "Factura sin guion rechazada", val.validar_factura("F00100123")[0], False)
    verificar(g, "Factura con serie de 3 caracteres rechazada", val.validar_factura("F00-123")[0], False)
    verificar(g, "Factura que inicia con número rechazada", val.validar_factura("0001-00123")[0], False)
    verificar(g, "Factura sin número rechazada", val.validar_factura("F001-")[0], False)
    verificar(g, "Factura con número no numérico rechazada", val.validar_factura("F001-ABC")[0], False)
    verificar(g, "Factura con 9 dígitos rechazada", val.validar_factura("F001-123456789")[0], False)
    verificar(g, "Factura con símbolo en la serie rechazada", val.validar_factura("F@01-123")[0], False)
    verificar(g, "Factura con dos guiones rechazada", val.validar_factura("F001-00123-1")[0], False)

    # RUC
    verificar(g, "RUC de 11 dígitos válido", val.validar_ruc("20123456789"), (True, "20123456789"))
    verificar(g, "RUC vacío es opcional (se guarda '-')", val.validar_ruc(""), (True, "-"))
    verificar(g, "RUC de 10 dígitos rechazado", val.validar_ruc("2012345678")[0], False)
    verificar(g, "RUC de 12 dígitos rechazado", val.validar_ruc("201234567890")[0], False)
    verificar(g, "RUC con una letra rechazado", val.validar_ruc("2012345678A")[0], False)
    verificar(g, "RUC con dígitos Unicode de ancho completo rechazado",
              val.validar_ruc("２０１２３４５６７８９")[0], False)

    # Fecha de recepción
    verificar(g, "Fecha 14/10/2026 válida", val.validar_fecha_recepcion("14/10/2026"), (True, "14/10/2026"))
    verificar(g, "Fecha 1/3/2026 se normaliza a 01/03/2026", val.validar_fecha_recepcion("1/3/2026"),
              (True, "01/03/2026"))
    verificar(g, "Fecha 31/02/2026 (inexistente) rechazada", val.validar_fecha_recepcion("31/02/2026")[0], False)
    verificar(g, "Fecha 29/02/2028 (año bisiesto) válida", val.validar_fecha_recepcion("29/02/2028")[0], True)
    verificar(g, "Fecha 29/02/2027 (no bisiesto) rechazada", val.validar_fecha_recepcion("29/02/2027")[0], False)
    verificar(g, "Fecha con guiones rechazada", val.validar_fecha_recepcion("14-10-2026")[0], False)
    verificar(g, "Fecha con año de 2 dígitos rechazada", val.validar_fecha_recepcion("14/10/26")[0], False)
    verificar(g, "Fecha vacía rechazada", val.validar_fecha_recepcion("")[0], False)

    # Texto libre
    verificar(g, "Producto 'Baptrin' válido", val.validar_texto("Baptrin", "Producto"), (True, "Baptrin"))
    verificar(g, "Producto con tilde 'Migradón' válido", val.validar_texto("Migradón", "Producto"),
              (True, "Migradón"))
    verificar(g, "Espacios repetidos se colapsan", val.validar_texto("  Sulfato   ferroso ", "Producto"),
              (True, "Sulfato ferroso"))
    verificar(g, "Producto vacío rechazado", val.validar_texto("   ", "Producto")[0], False)
    verificar(g, "Producto con '|' rechazado", val.validar_texto("A|B", "Producto")[0], False)
    verificar(g, "Producto con tabulación rechazado", val.validar_texto("A\tB", "Producto")[0], False)
    verificar(g, "Producto de 61 caracteres rechazado", val.validar_texto("x" * 61, "Producto")[0], False)

    # Lote y registro sanitario
    verificar(g, "Lote L2406 válido", val.validar_lote("L2406"), (True, "L2406"))
    verificar(g, "Lote 'l2406' se pasa a mayúsculas", val.validar_lote("l2406"), (True, "L2406"))
    verificar(g, "Lote de 2 caracteres rechazado", val.validar_lote("L2")[0], False)
    verificar(g, "Lote con símbolo '@' rechazado", val.validar_lote("L24@6")[0], False)
    verificar(g, "Lote vacío rechazado", val.validar_lote("")[0], False)
    verificar(g, "Lote que empieza con guion rechazado", val.validar_lote("-L2406")[0], False)
    verificar(g, "Lote con guion doble rechazado", val.validar_lote("L--24")[0], False)
    verificar(g, "Lote de 21 caracteres rechazado", val.validar_lote("A" * 21)[0], False)
    verificar(g, "Registro sanitario EN-12345 válido", val.validar_registro_sanitario("EN-12345"),
              (True, "EN-12345"))
    verificar(g, "Registro sanitario 'EN' (muy corto) rechazado", val.validar_registro_sanitario("EN")[0], False)

    # Cantidad
    verificar(g, "Cantidad 10 válida", val.validar_cantidad("10"), (True, 10))
    verificar(g, "Cantidad 0 rechazada", val.validar_cantidad("0")[0], False)
    verificar(g, "Cantidad negativa rechazada", val.validar_cantidad("-5")[0], False)
    verificar(g, "Cantidad con letras rechazada", val.validar_cantidad("abc")[0], False)
    verificar(g, "Cantidad decimal rechazada", val.validar_cantidad("2.5")[0], False)
    verificar(g, "Cantidad vacía rechazada", val.validar_cantidad("")[0], False)
    verificar(g, "Cantidad 1 000 000 (máximo) válida", val.validar_cantidad("1000000")[0], True)
    verificar(g, "Cantidad 1 000 001 rechazada", val.validar_cantidad("1000001")[0], False)
    verificar(g, "Cantidad con 5000 dígitos rechazada sin error", val.validar_cantidad("9" * 5000)[0], False)

    # Precio
    verificar(g, "Precio 5.00 válido", val.validar_precio("5.00"), (True, 5.0))
    verificar(g, "Precio '5,50' (coma decimal) válido", val.validar_precio("5,50"), (True, 5.5))
    verificar(g, "Precio 'S/ 5.00' válido", val.validar_precio("S/ 5.00"), (True, 5.0))
    verificar(g, "Precio entero 12 válido", val.validar_precio("12"), (True, 12.0))
    verificar(g, "Precio 99999.99 (máximo) válido", val.validar_precio("99999.99"), (True, 99999.99))
    verificar(g, "Precio 0 rechazado", val.validar_precio("0")[0], False)
    verificar(g, "Precio 0.00 rechazado", val.validar_precio("0.00")[0], False)
    verificar(g, "Precio negativo rechazado", val.validar_precio("-1")[0], False)
    verificar(g, "Precio con 3 decimales rechazado", val.validar_precio("5.555")[0], False)
    verificar(g, "Precio con letras rechazado", val.validar_precio("abc")[0], False)
    verificar(g, "Precio 'nan' rechazado", val.validar_precio("nan")[0], False)
    verificar(g, "Precio '1e3' rechazado", val.validar_precio("1e3")[0], False)
    verificar(g, "Precio 100000 rechazado", val.validar_precio("100000")[0], False)
    verificar(g, "Precio vacío rechazado", val.validar_precio("")[0], False)

    # Vencimiento (recepción 14/10/2026)
    rec = "14/10/2026"
    verificar(g, "Vencimiento 03/2028 válido", val.validar_vencimiento("03/2028", rec), (True, "03/2028"))
    verificar(g, "Vencimiento 3/2028 se normaliza", val.validar_vencimiento("3/2028", rec), (True, "03/2028"))
    verificar(g, "Vencimiento 13/2028 (mes 13) rechazado", val.validar_vencimiento("13/2028", rec)[0], False)
    verificar(g, "Vencimiento 00/2028 rechazado", val.validar_vencimiento("00/2028", rec)[0], False)
    verificar(g, "Vencimiento 09/2026 (anterior a la recepción) rechazado",
              val.validar_vencimiento("09/2026", rec)[0], False)
    verificar(g, "Vencimiento 10/2026 (fin de mes posterior a 14/10) válido",
              val.validar_vencimiento("10/2026", rec)[0], True)
    verificar(g, "Vencimiento con guion rechazado", val.validar_vencimiento("03-2028", rec)[0], False)


# ---------------------------------------------------------------------------
# 2. Registros, búsqueda, estados y ordenamiento
# ---------------------------------------------------------------------------
def probar_registros():
    g = "Registros"
    reg.limpiar()
    datos = [
        ("ING-0001", "F001-00123", "14/10/2026", "Droguería de ejemplo SAC", "20123456789",
         "Baptrin", "L2406", "EN-12345", 10, 5.00, "03/2028"),
        ("ING-0002", "F001-00124", "14/10/2026", "Droguería de ejemplo SAC", "",
         "Sulfato ferroso", "L3101", "EN-23456", 20, 12.50, "12/2026"),
        ("ING-0003", "F001-00125", "10/03/2026", "Laboratorio de ejemplo SA", "20987654321",
         "Migradón", "L1805", "EN-34567", 5, 18.90, "08/2026"),
        ("ING-0004", "F001-00126", "14/10/2026", "Droguería de ejemplo SAC", "20123456789",
         "Paracetamol", "L9999", "EN-45678", 100, 1.50, "12/2026"),
    ]
    for d in datos:
        verificar(g, f"Registrar {d[0]} ({d[5]})", reg.agregar_registro(*d)[0], True)
    verificar(g, "Total de registros = 4", reg.total(), 4)
    verificar(g, "Siguiente código generado = ING-0005", reg.generar_codigo(), "ING-0005")
    verificar(g, "RUC vacío se guarda como '-'", reg.rucs[1], "-")

    # Rechazos: no deben modificar los arreglos
    base = ("ING-0005", "F001-00127", "14/10/2026", "Droguería de ejemplo SAC", "20123456789",
            "Producto prueba", "L0001", "EN-00001", 1, 1.00, "03/2028")
    verificar(g, "Código repetido rechazado", reg.agregar_registro(*(("ING-0001",) + base[1:]))[0], False)
    verificar(g, "RUC de 10 dígitos rechazado", reg.agregar_registro(
        *(base[:4] + ("2012345678",) + base[5:]))[0], False)
    verificar(g, "Vencimiento anterior a la recepción rechazado", reg.agregar_registro(
        *(base[:10] + ("09/2026",)))[0], False)
    verificar(g, "Factura inválida rechazada", reg.agregar_registro(
        *(base[:1] + ("F001",) + base[2:]))[0], False)
    verificar(g, "Cantidad 0 rechazada", reg.agregar_registro(*(base[:8] + (0,) + base[9:]))[0], False)
    verificar(g, "Precio negativo rechazado", reg.agregar_registro(*(base[:9] + (-2,) + base[10:]))[0], False)
    verificar(g, "Los rechazos no alteran el total", reg.total(), 4)
    verificar(g, "Todos los arreglos siguen alineados (misma longitud)",
              [len(a) for a in reg.ARREGLOS], [4] * 11)

    # Búsqueda lineal
    verificar(g, "Buscar 'ING-0002' -> posición 1", reg.buscar_por_codigo("ING-0002"), 1)
    verificar(g, "Buscar 'ing-0002' (minúsculas) -> 1", reg.buscar_por_codigo("ing-0002"), 1)
    verificar(g, "Buscar '2' -> 1", reg.buscar_por_codigo("2"), 1)
    verificar(g, "Buscar código inexistente -> -1", reg.buscar_por_codigo("ING-0099"), -1)
    verificar(g, "Buscar texto vacío -> -1", reg.buscar_por_codigo(""), -1)

    # Estados con fecha fija (hoy = 22/10/2026)
    hoy = date(2026, 10, 22)
    verificar(g, "Estado de Baptrin (03/2028) = Recibido", reg.calcular_estado("03/2028", hoy), "Recibido")
    verificar(g, "Estado de Sulfato ferroso (12/2026) = Por vencer", reg.calcular_estado("12/2026", hoy),
              "Por vencer")
    verificar(g, "Estado de Migradón (08/2026) = Vencido", reg.calcular_estado("08/2026", hoy), "Vencido")
    verificar(g, "Contar estados (vencidos, por vencer, recibidos)", reg.contar_estados(hoy), (1, 2, 1))
    verificar(g, "Posiciones de los Por vencer", reg.indices_por_estado("Por vencer", hoy), [1, 3])
    verificar(g, "Días restantes de 12/2026 desde 22/10/2026", reg.dias_restantes("12/2026", hoy),
              (date(2026, 12, 31) - hoy).days)
    verificar(g, "Vence 10/2026 y hoy es 31/10/2026 -> Por vencer (último día)",
              reg.calcular_estado("10/2026", date(2026, 10, 31)), "Por vencer")
    verificar(g, "Vence 10/2026 y hoy es 01/11/2026 -> Vencido",
              reg.calcular_estado("10/2026", date(2026, 11, 1)), "Vencido")
    verificar(g, "Vence 01/2027 y hoy es 22/10/2026 -> Recibido (más de 3 meses)",
              reg.calcular_estado("01/2027", hoy), "Recibido")
    verificar(g, "Vence 01/2027 y hoy es 31/10/2026 -> Por vencer (exactamente 3 meses)",
              reg.calcular_estado("01/2027", date(2026, 10, 31)), "Por vencer")
    verificar(g, "Sumar 1 mes a 31/01/2026 = 28/02/2026", reg.sumar_meses(date(2026, 1, 31), 1),
              date(2026, 2, 28))
    verificar(g, "Sumar 3 meses a 30/11/2026 = 28/02/2027", reg.sumar_meses(date(2026, 11, 30), 3),
              date(2027, 2, 28))
    verificar(g, "Sumar 3 meses a 22/10/2026 = 22/01/2027", reg.sumar_meses(date(2026, 10, 22), 3),
              date(2027, 1, 22))

    # Ordenamiento por selección
    reg.ordenar("vencimiento")
    verificar(g, "Ordenar por vencimiento: códigos (desempate por código)", list(reg.codigos),
              ["ING-0003", "ING-0002", "ING-0004", "ING-0001"])
    verificar(g, "Ordenar por vencimiento: los productos acompañan a su código", list(reg.productos),
              ["Migradón", "Sulfato ferroso", "Paracetamol", "Baptrin"])
    verificar(g, "Ordenar por vencimiento: los precios acompañan a su código", list(reg.precios),
              [18.9, 12.5, 1.5, 5.0])
    verificar(g, "Ordenar por vencimiento: vencimientos", list(reg.vencimientos),
              ["08/2026", "12/2026", "12/2026", "03/2028"])
    reg.ordenar("codigo")
    verificar(g, "Ordenar por código: vuelve al orden ING-0001..0004", list(reg.codigos),
              ["ING-0001", "ING-0002", "ING-0003", "ING-0004"])
    verificar(g, "Ordenar por código: las cantidades acompañan", list(reg.cantidades), [10, 20, 5, 100])
    try:
        reg.ordenar("precio")
        resultado = "no lanzó error"
    except ValueError:
        resultado = "ValueError"
    verificar(g, "Criterio de orden desconocido lanza ValueError", resultado, "ValueError")

    # Actualizar precio
    verificar(g, "Actualizar precio ING-0001 a '6,50'", reg.actualizar_precio("ING-0001", "6,50"), (True, 6.5))
    verificar(g, "El precio quedó en 6.5", reg.precios[reg.buscar_por_codigo("ING-0001")], 6.5)
    verificar(g, "Precio negativo no actualiza", reg.actualizar_precio("ING-0001", "-3")[0], False)
    verificar(g, "El precio sigue en 6.5 tras el rechazo", reg.precios[0], 6.5)
    verificar(g, "Actualizar código inexistente falla", reg.actualizar_precio("ING-0099", "5")[0], False)

    # Códigos con huecos y límite
    reg.limpiar()
    verificar(g, "Sin registros, el primer código es ING-0001", reg.generar_codigo(), "ING-0001")
    reg.ordenar("codigo")
    verificar(g, "Ordenar sin registros no produce error", reg.total(), 0)
    reg.agregar_registro("ING-0009", "F001-1", "14/10/2026", "Distribuidora", "", "Baptrin",
                         "L2406", "EN-12345", 1, 5, "03/2028")
    reg.ordenar("vencimiento")
    verificar(g, "Ordenar con un solo registro no produce error", reg.codigos, ["ING-0009"])
    verificar(g, "Con ING-0009 el siguiente código es ING-0010", reg.generar_codigo(), "ING-0010")
    reg.agregar_registro("ING-9999", "F001-2", "14/10/2026", "Distribuidora", "", "Baptrin",
                         "L2406", "EN-12345", 1, 5, "03/2028")
    verificar(g, "Con ING-9999 ya no hay más códigos (None)", reg.generar_codigo(), None)
    reg.limpiar()


# ---------------------------------------------------------------------------
# 3. Archivos
# ---------------------------------------------------------------------------
def probar_archivos():
    g = "Archivos"
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "expedientes.txt")

        reg.limpiar()
        verificar(g, "Archivo inexistente: carga 0 registros sin error", arch.cargar_datos(ruta)[:3], (True, 0, 0))

        reg.agregar_registro("ING-0001", "F001-00123", "14/10/2026", "Droguería de ejemplo SAC",
                             "20123456789", "Baptrin", "L2406", "EN-12345", 10, 6.5, "03/2028")
        reg.agregar_registro("ING-0002", "F001-00124", "14/10/2026", "Droguería de ejemplo SAC", "",
                             "Migradón", "L3101", "EN-23456", 20, 12.5, "12/2026")
        verificar(g, "Guardar datos", arch.guardar_datos(ruta)[0], True)
        verificar(g, "No queda archivo temporal tras guardar", os.path.exists(ruta + ".tmp"), False)
        with open(ruta, "r", encoding="utf-8") as f:
            lineas = f.read().splitlines()
        verificar(g, "El archivo tiene una línea por registro", len(lineas), 2)
        verificar(g, "Formato de la línea 1", lineas[0],
                  "ING-0001|F001-00123|14/10/2026|Droguería de ejemplo SAC|20123456789|"
                  "Baptrin|L2406|EN-12345|10|6.50|03/2028")
        verificar(g, "Formato de la línea 2 (RUC '-' y tilde)", lineas[1],
                  "ING-0002|F001-00124|14/10/2026|Droguería de ejemplo SAC|-|"
                  "Migradón|L3101|EN-23456|20|12.50|12/2026")

        antes = captura(reg.ARREGLOS)
        reg.limpiar()
        verificar(g, "Tras limpiar la memoria no hay registros", reg.total(), 0)
        verificar(g, "Cargar devuelve (ok, 2 cargados, 0 omitidas)", arch.cargar_datos(ruta)[:3], (True, 2, 0))
        verificar(g, "Los datos cargados son idénticos a los guardados", captura(reg.ARREGLOS), antes)

        # Archivo con líneas dañadas
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("ING-0001|F001-00123|14/10/2026|Droguería de ejemplo SAC|-|Baptrin|L2406|EN-12345|10|5.00|03/2028\n")
            f.write("ING-0002|F001-00124|14/10/2026|X\n")
            f.write("ING-0002|F001-00124|14/10/2026|Droguería de ejemplo SAC|-|Migradón|L2407|EN-12346|0|5.00|03/2028\n")
            f.write("ING-0001|F001-00125|14/10/2026|Droguería de ejemplo SAC|-|Repetido|L2408|EN-12347|3|5.00|03/2028\n")
            f.write("\n")
            f.write(" ING-0005 |F001-00126|14/10/2026|Droguería de ejemplo SAC||Sulfato ferroso|L2409|EN-12348|20|12.50|12/2026 \n")
        ok, cargados, omitidas, mensajes = arch.cargar_datos(ruta)
        verificar(g, "Archivo con líneas dañadas: (ok, cargados, omitidas)", (ok, cargados, omitidas), (True, 2, 3))
        verificar(g, "Solo quedan los registros válidos", list(reg.codigos), ["ING-0001", "ING-0005"])
        verificar(g, "Se crea copia de respaldo del archivo original", os.path.exists(ruta + ".respaldo"), True)
        verificar(g, "Se informa de cada línea omitida (+ aviso de respaldo)", len(mensajes), 4)

        # Archivo con BOM y saltos de línea de Windows (CRLF)
        with open(ruta, "wb") as f:
            f.write(b"\xef\xbb\xbf" + "ING-0001|F001-00123|14/10/2026|Distribuidora|-|Migradón|L2406|EN-12345|10|5.00|03/2028\r\n".encode("utf-8"))
        verificar(g, "Archivo con BOM y CRLF se lee bien", arch.cargar_datos(ruta)[:3], (True, 1, 0))

        # Archivo ilegible: no debe borrar los datos en memoria
        antes = captura(reg.ARREGLOS)
        with open(ruta, "wb") as f:
            f.write(b"\xff\xfe\x00\xd8 no es utf-8")
        verificar(g, "Archivo ilegible: devuelve ok = False", arch.cargar_datos(ruta)[0], False)
        verificar(g, "Archivo ilegible: no se pierden los datos en memoria", captura(reg.ARREGLOS), antes)

        # Ruta de guardado imposible
        ruta_mala = os.path.join(carpeta, "no_existe", "expedientes.txt")
        verificar(g, "Guardar en carpeta inexistente falla sin cerrar el programa",
                  arch.guardar_datos(ruta_mala)[0], False)
    reg.limpiar()


# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------
def main():
    probar_validaciones()
    probar_registros()
    probar_archivos()

    print("=" * 96)
    print("PRUEBAS AUTOMÁTICAS DEL PROTOTIPO".center(96))
    print("=" * 96)
    print(f"{'N.°':>3}  {'Grupo':<11} {'Caso de prueba':<70} {'Resultado':<9}")
    print("-" * 96)
    for numero, (grupo, descripcion, esperado, obtenido, ok) in enumerate(resultados, start=1):
        print(f"{numero:>3}  {grupo:<11} {descripcion[:70]:<70} {'APROBADO' if ok else 'FALLÓ':<9}")
        if not ok:
            print(f"       esperado: {esperado!r}")
            print(f"       obtenido: {obtenido!r}")
    aprobadas = sum(1 for r in resultados if r[4])
    print("-" * 96)
    print(f"Total: {aprobadas} de {len(resultados)} pruebas aprobadas.")
    return 0 if aprobadas == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
