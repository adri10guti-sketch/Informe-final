# -*- coding: utf-8 -*-
"""
main.py
-------
Prototipo: registro digital de productos recibidos y control de vencimientos
(RODRIFARMA - Cajamarca). Interfaz de consola con menú.

Ejecutar:   python main.py
"""
from datetime import date

import archivos as arch
import registros as reg
import validaciones as val

TITULO = "REGISTRO DIGITAL DE PRODUCTOS RECIBIDOS - RODRIFARMA"


# ---------------------------------------------------------------------------
# Entrada y salida por consola
# ---------------------------------------------------------------------------
def pedir_dato(pregunta, validador, por_defecto=None):
    """Repite la pregunta hasta que el dato sea válido.

    validador: función que recibe el texto y devuelve (ok, valor_o_mensaje).
    Devuelve el valor ya normalizado, o None si el usuario escribe 'cancelar'.
    """
    while True:
        entrada = input(pregunta).strip()
        if entrada.lower() == "cancelar":
            return None
        if entrada == "" and por_defecto is not None:
            entrada = por_defecto
        ok, resultado = validador(entrada)
        if ok:
            return resultado
        print("  Error:", resultado)


def leer_codigo(pregunta):
    """Pide un código y lo valida. Devuelve el código normalizado o None si es inválido."""
    codigo = val.normalizar_codigo(input(pregunta))
    ok, mensaje = val.validar_codigo(codigo)
    if not ok:
        print("  Error:", mensaje)
        return None
    return codigo


def texto_dias(dias):
    """Describe los días que faltan (o pasaron) respecto al vencimiento."""
    if dias > 1:
        return f"faltan {dias} días"
    if dias == 1:
        return "falta 1 día"
    if dias == 0:
        return "vence hoy (último día de validez)"
    if dias == -1:
        return "venció hace 1 día"
    return f"venció hace {-dias} días"


def mostrar_menu():
    print("\n================ MENÚ PRINCIPAL ================")
    print(" 1. Registrar producto recibido")
    print(" 2. Buscar registro por código")
    print(" 3. Listar todos los registros")
    print(" 4. Ordenar registros (por código o vencimiento)")
    print(" 5. Ver productos vencidos y por vencer")
    print(" 6. Actualizar precio de un producto")
    print(" 7. Guardar datos en el archivo")
    print(" 0. Salir")
    print("================================================")


def mostrar_tabla(indices, titulo):
    """Imprime en forma de tabla los registros cuyas posiciones están en 'indices'."""
    print(f"\n--- {titulo} ({len(indices)}) ---")
    if len(indices) == 0:
        print("(sin registros)")
        return
    print(f"{'Código':<8} {'Producto':<18} {'Lote':<12} {'Cant.':>6} "
          f"{'Precio S/':>10} {'Vence':<7} {'Estado':<10}")
    print("-" * 77)
    for i in indices:
        print(f"{reg.codigos[i]:<8} {reg.productos[i][:18]:<18} {reg.lotes[i][:12]:<12} "
              f"{reg.cantidades[i]:>6} {reg.precios[i]:>10.2f} {reg.vencimientos[i]:<7} "
              f"{reg.calcular_estado(reg.vencimientos[i]):<10}")


def mostrar_ficha(i):
    """Imprime todos los datos del registro en la posición i."""
    estado = reg.calcular_estado(reg.vencimientos[i])
    dias = reg.dias_restantes(reg.vencimientos[i])
    print("\n----- FICHA DEL PRODUCTO -----")
    print(f"Código             : {reg.codigos[i]}")
    print(f"N.° de factura     : {reg.facturas[i]}")
    print(f"Fecha de recepción : {reg.fechas_recepcion[i]}")
    print(f"Distribuidora      : {reg.distribuidoras[i]}")
    print(f"RUC                : {reg.rucs[i]}")
    print(f"Producto           : {reg.productos[i]}")
    print(f"Lote               : {reg.lotes[i]}")
    print(f"Registro sanitario : {reg.registros_sanitarios[i]}")
    print(f"Cantidad           : {reg.cantidades[i]}")
    print(f"Precio             : S/ {reg.precios[i]:.2f}")
    print(f"Vencimiento        : {reg.vencimientos[i]}")
    print(f"Estado             : {estado.upper()} ({texto_dias(dias)})")
    print("------------------------------")


def mostrar_resumen_alertas():
    """Alerta breve de productos vencidos o por vencer."""
    vencidos, por_vencer, _ = reg.contar_estados()
    if vencidos > 0 or por_vencer > 0:
        print(f"\n*** ALERTA: {vencidos} producto(s) VENCIDO(S) y {por_vencer} "
              f"POR VENCER (3 meses o menos). Use la opción 5 para verlos. ***")


def guardar_con_mensaje():
    """Guarda los datos y muestra el resultado. Devuelve True si se guardó."""
    ok, mensaje = arch.guardar_datos()
    print(mensaje if ok else "ADVERTENCIA: " + mensaje)
    return ok


# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------
def registrar():
    print("\n--- REGISTRAR PRODUCTO RECIBIDO ---")
    print("(escriba 'cancelar' en cualquier momento para volver al menú)")
    codigo = reg.generar_codigo()
    if codigo is None:
        print("Error: se alcanzó el límite de registros (ING-9999).")
        return
    print(f"Código asignado por el sistema: {codigo}")

    factura = pedir_dato("N.° de factura (SERIE-NÚMERO, ej. F001-00123): ", val.validar_factura)
    if factura is None:
        print("Registro cancelado.")
        return

    hoy = val.formatear_fecha(date.today())
    fecha = pedir_dato(f"Fecha de recepción (DD/MM/AAAA) [Enter = {hoy}]: ",
                       val.validar_fecha_recepcion, hoy)
    if fecha is None:
        print("Registro cancelado.")
        return

    distribuidora = pedir_dato("Distribuidora: ",
                               lambda t: val.validar_texto(t, "Distribuidora"))
    if distribuidora is None:
        print("Registro cancelado.")
        return

    ruc = pedir_dato("RUC (11 dígitos, Enter si no lo tiene): ", val.validar_ruc)
    if ruc is None:
        print("Registro cancelado.")
        return

    producto = pedir_dato("Producto: ", lambda t: val.validar_texto(t, "Producto"))
    if producto is None:
        print("Registro cancelado.")
        return

    lote = pedir_dato("Lote (ej. L2406): ", val.validar_lote)
    if lote is None:
        print("Registro cancelado.")
        return

    sanitario = pedir_dato("Registro sanitario (ej. EN-12345): ", val.validar_registro_sanitario)
    if sanitario is None:
        print("Registro cancelado.")
        return

    cantidad = pedir_dato("Cantidad (entero mayor que 0): ", val.validar_cantidad)
    if cantidad is None:
        print("Registro cancelado.")
        return

    precio = pedir_dato("Precio unitario en S/ (ej. 5.00): ", val.validar_precio)
    if precio is None:
        print("Registro cancelado.")
        return

    vencimiento = pedir_dato("Vencimiento (MM/AAAA, ej. 03/2028): ",
                             lambda t: val.validar_vencimiento(t, fecha))
    if vencimiento is None:
        print("Registro cancelado.")
        return

    ok, mensaje = reg.agregar_registro(codigo, factura, fecha, distribuidora, ruc, producto,
                                       lote, sanitario, cantidad, precio, vencimiento)
    if not ok:
        print("Error:", mensaje)
        return
    print(mensaje)
    mostrar_ficha(reg.buscar_por_codigo(codigo))
    guardar_con_mensaje()


def buscar():
    print("\n--- BUSCAR POR CÓDIGO ---")
    codigo = leer_codigo("Código a buscar (ej. ING-0001): ")
    if codigo is None:
        return
    posicion = reg.buscar_por_codigo(codigo)
    if posicion == -1:
        print(f"No se encontró ningún registro con el código {codigo}.")
    else:
        mostrar_ficha(posicion)


def listar():
    mostrar_tabla(list(range(reg.total())), "LISTADO DE REGISTROS")


def ordenar_registros():
    print("\n--- ORDENAR REGISTROS ---")
    print(" 1. Por código")
    print(" 2. Por fecha de vencimiento (los que vencen primero, arriba)")
    opcion = input("Elija 1 o 2: ").strip()
    if opcion == "1":
        reg.ordenar("codigo")
        mostrar_tabla(list(range(reg.total())), "ORDENADO POR CÓDIGO")
    elif opcion == "2":
        reg.ordenar("vencimiento")
        mostrar_tabla(list(range(reg.total())), "ORDENADO POR VENCIMIENTO")
    else:
        print("Opción no válida. No se ordenó nada.")


def ver_alertas():
    mostrar_tabla(reg.indices_por_estado("Vencido"), "PRODUCTOS VENCIDOS")
    mostrar_tabla(reg.indices_por_estado("Por vencer"), "PRODUCTOS POR VENCER (3 meses o menos)")


def actualizar_precio():
    print("\n--- ACTUALIZAR PRECIO ---")
    codigo = leer_codigo("Código del producto (ej. ING-0001): ")
    if codigo is None:
        return
    posicion = reg.buscar_por_codigo(codigo)
    if posicion == -1:
        print(f"No se encontró ningún registro con el código {codigo}.")
        return
    print(f"Producto: {reg.productos[posicion]} | Precio actual: S/ {reg.precios[posicion]:.2f}")
    nuevo = pedir_dato("Nuevo precio en S/ ('cancelar' para volver): ", val.validar_precio)
    if nuevo is None:
        print("Operación cancelada.")
        return
    ok, resultado = reg.actualizar_precio(codigo, nuevo)
    if ok:
        print(f"Precio actualizado: S/ {resultado:.2f}")
        guardar_con_mensaje()
    else:
        print("Error:", resultado)


def salir():
    """Guarda y confirma la salida. Devuelve True si se debe cerrar el programa."""
    if guardar_con_mensaje():
        print("Gracias por usar el sistema. ¡Hasta pronto!")
        return True
    respuesta = input("No se pudieron guardar los últimos cambios. ¿Salir de todos modos? (s/n): ")
    if respuesta.strip().lower() == "s":
        print("Programa cerrado sin guardar.")
        return True
    return False


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print(TITULO.center(60))
    print("=" * 60)

    ok, cargados, omitidas, mensajes = arch.cargar_datos()
    if not ok:
        for mensaje in mensajes:
            print("ERROR:", mensaje)
        print("El programa se cerró para no perder los datos. Corrija o cierre el archivo "
              "y vuelva a ejecutarlo.")
        return
    for mensaje in mensajes[:5]:
        print("Aviso:", mensaje)
    if len(mensajes) > 5:
        print(f"Aviso: y {len(mensajes) - 5} aviso(s) más.")
    print(f"Registros cargados: {cargados}" + (f" | Líneas omitidas: {omitidas}" if omitidas else ""))
    mostrar_resumen_alertas()

    while True:
        try:
            mostrar_menu()
            opcion = input("Elija una opción (0-7): ").strip()
            if opcion == "1":
                registrar()
            elif opcion == "2":
                buscar()
            elif opcion == "3":
                listar()
            elif opcion == "4":
                ordenar_registros()
            elif opcion == "5":
                ver_alertas()
            elif opcion == "6":
                actualizar_precio()
            elif opcion == "7":
                guardar_con_mensaje()
            elif opcion == "0":
                if salir():
                    break
            else:
                print("Opción no válida. Escriba un número del 0 al 7.")
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada interrumpida. Guardando datos antes de salir...")
            guardar_con_mensaje()
            break


if __name__ == "__main__":
    main()
