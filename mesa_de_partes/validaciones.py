# -*- coding: utf-8 -*-
"""
validaciones.py
---------------
Funciones de validación y conversión de datos del prototipo.

Cada función validar_* recibe el texto escrito por el usuario y devuelve una
tupla (ok, valor):
    ok = True   -> valor es el dato ya normalizado (listo para guardarse).
    ok = False  -> valor es el mensaje que explica qué debe corregirse.

Son funciones "puras": no leen ni escriben archivos ni usan la consola, por
eso se pueden probar de forma automática (ver pruebas.py).
"""
import calendar
from datetime import date

DIGITOS = "0123456789"
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALFANUMERICOS = LETRAS + DIGITOS

ANIO_MIN = 2000
ANIO_MAX = 2100
CANTIDAD_MAX = 1000000
PRECIO_MAX_ENTEROS = 5          # hasta 99999.99


# ---------------------------------------------------------------------------
# Utilidades de cadenas
# ---------------------------------------------------------------------------
def solo_digitos(texto):
    """True si el texto no está vacío y todos sus caracteres son 0-9 (ASCII).

    Se usa en lugar de str.isdigit() porque isdigit() también acepta otros
    símbolos Unicode (por ejemplo '²' o dígitos de ancho completo).
    """
    if texto == "":
        return False
    for caracter in texto:
        if caracter not in DIGITOS:
            return False
    return True


def normalizar_codigo(texto):
    """Prepara un código escrito por el usuario para compararlo.

    - Quita espacios y pasa a mayúsculas: ' ing-0001 ' -> 'ING-0001'.
    - Si solo escribió números (hasta 4 dígitos), completa el formato:
      '2' -> 'ING-0002'.
    """
    texto = texto.strip().upper()
    if solo_digitos(texto) and len(texto) <= 4:
        texto = "ING-" + texto.zfill(4)
    return texto


# ---------------------------------------------------------------------------
# Fechas
# ---------------------------------------------------------------------------
def convertir_fecha(texto):
    """Convierte 'DD/MM/AAAA' en un objeto date. Devuelve None si no es válida."""
    partes = texto.strip().split("/")
    if len(partes) != 3:
        return None
    dia, mes, anio = partes
    if not (solo_digitos(dia) and solo_digitos(mes) and solo_digitos(anio)):
        return None
    if len(dia) > 2 or len(mes) > 2 or len(anio) != 4:
        return None
    if int(anio) < ANIO_MIN or int(anio) > ANIO_MAX:
        return None
    try:
        return date(int(anio), int(mes), int(dia))   # falla con 31/02, mes 13, etc.
    except ValueError:
        return None


def convertir_vencimiento(texto):
    """Convierte 'MM/AAAA' en el ÚLTIMO DÍA de ese mes (objeto date).

    En farmacia, un producto con vencimiento 03/2028 es válido hasta el último
    día de marzo de 2028. Devuelve None si el texto no es válido.
    """
    partes = texto.strip().split("/")
    if len(partes) != 2:
        return None
    mes, anio = partes
    if not (solo_digitos(mes) and solo_digitos(anio)):
        return None
    if len(mes) > 2 or len(anio) != 4:
        return None
    mes = int(mes)
    anio = int(anio)
    if mes < 1 or mes > 12 or anio < ANIO_MIN or anio > ANIO_MAX:
        return None
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, ultimo_dia)


def formatear_fecha(fecha):
    """date -> 'DD/MM/AAAA'."""
    return f"{fecha.day:02d}/{fecha.month:02d}/{fecha.year}"


def formatear_vencimiento(fecha):
    """date -> 'MM/AAAA'."""
    return f"{fecha.month:02d}/{fecha.year}"


# ---------------------------------------------------------------------------
# Validaciones de cada campo
# ---------------------------------------------------------------------------
def validar_codigo(codigo):
    """Código de ingreso: 'ING-' seguido de 4 dígitos (ING-0001 ... ING-9999)."""
    if (len(codigo) == 8 and codigo[:4] == "ING-"
            and solo_digitos(codigo[4:]) and codigo != "ING-0000"):
        return True, codigo
    return False, "Código inválido. Use el formato ING-0001."


def validar_factura(texto):
    """N.° de factura con formato SERIE-NÚMERO, ej. F001-00123.

    Serie: 4 caracteres, el primero una letra y los demás letras o dígitos.
    Número: de 1 a 8 dígitos.
    """
    texto = texto.strip().upper()
    mensaje = "N.° de factura inválido. Use el formato SERIE-NÚMERO, ej. F001-00123."
    partes = texto.split("-")
    if len(partes) != 2:
        return False, mensaje
    serie, numero = partes
    if len(serie) != 4 or serie[0] not in LETRAS:
        return False, mensaje
    for caracter in serie[1:]:
        if caracter not in ALFANUMERICOS:
            return False, mensaje
    if not solo_digitos(numero) or len(numero) > 8:
        return False, mensaje
    return True, texto


def validar_fecha_recepcion(texto):
    """Fecha de recepción real, en formato DD/MM/AAAA."""
    fecha = convertir_fecha(texto)
    if fecha is None:
        return False, "Fecha inválida. Use DD/MM/AAAA con una fecha real, ej. 14/10/2026."
    return True, formatear_fecha(fecha)


def validar_texto(texto, campo, largo_max=60):
    """Texto libre (producto, distribuidora): no vacío, sin '|' ni caracteres de control."""
    texto = texto.strip()
    if texto == "":
        return False, f"{campo}: no puede estar vacío."
    if not texto.isprintable() or "|" in texto:
        return False, f"{campo}: contiene caracteres no permitidos (no use '|')."
    texto = " ".join(texto.split())          # colapsa espacios repetidos
    if len(texto) > largo_max:
        return False, f"{campo}: no puede superar {largo_max} caracteres."
    return True, texto


def validar_ruc(texto):
    """RUC opcional: vacío (se guarda '-') o exactamente 11 dígitos."""
    texto = texto.strip()
    if texto == "" or texto == "-":
        return True, "-"
    if len(texto) != 11 or not solo_digitos(texto):
        return False, "El RUC debe tener exactamente 11 dígitos (o déjelo vacío si no lo tiene)."
    return True, texto


def _validar_codigo_alfanumerico(texto, campo, largo_min, largo_max, ejemplo):
    """Base común para lote y registro sanitario (letras, números y guion)."""
    texto = texto.strip().upper()
    mensaje = (f"{campo} inválido. Use de {largo_min} a {largo_max} caracteres "
               f"(letras, números y guion), ej. {ejemplo}.")
    if len(texto) < largo_min or len(texto) > largo_max:
        return False, mensaje
    for caracter in texto:
        if caracter not in ALFANUMERICOS and caracter != "-":
            return False, mensaje
    if texto[0] == "-" or texto[-1] == "-" or "--" in texto:
        return False, mensaje
    return True, texto


def validar_lote(texto):
    """Lote: 3 a 20 caracteres (letras, números y guion), ej. L2406."""
    return _validar_codigo_alfanumerico(texto, "Lote", 3, 20, "L2406")


def validar_registro_sanitario(texto):
    """Registro sanitario: 5 a 20 caracteres (letras, números y guion), ej. EN-12345."""
    return _validar_codigo_alfanumerico(texto, "Registro sanitario", 5, 20, "EN-12345")


def validar_cantidad(texto):
    """Cantidad: entero mayor que 0 (máximo 1 000 000)."""
    texto = texto.strip()
    mensaje = "La cantidad debe ser un número entero mayor que 0 (ej. 10)."
    if not solo_digitos(texto):
        return False, mensaje
    if len(texto) > 7:                         # evita convertir cadenas gigantes
        return False, f"La cantidad no puede superar {CANTIDAD_MAX}."
    cantidad = int(texto)
    if cantidad <= 0:
        return False, mensaje
    if cantidad > CANTIDAD_MAX:
        return False, f"La cantidad no puede superar {CANTIDAD_MAX}."
    return True, cantidad


def validar_precio(texto):
    """Precio en soles: número mayor que 0, hasta 2 decimales (acepta '5,50' y 'S/ 5.00')."""
    mensaje = "El precio debe ser un número mayor que 0, con máximo 2 decimales (ej. 5.00)."
    texto = texto.strip().upper()
    texto = texto.replace("S/.", "").replace("S/", "").replace(" ", "").replace(",", ".")
    partes = texto.split(".")
    if len(partes) > 2:
        return False, mensaje
    entero = partes[0]
    decimales = partes[1] if len(partes) == 2 else ""
    if entero == "" and decimales == "":
        return False, mensaje
    if entero != "" and not solo_digitos(entero):
        return False, mensaje
    if decimales != "" and not solo_digitos(decimales):
        return False, mensaje
    if len(decimales) > 2:
        return False, "El precio admite como máximo 2 decimales (ej. 5.00)."
    if len(entero) > PRECIO_MAX_ENTEROS:
        return False, "El precio no puede superar S/ 99999.99."
    if entero == "":
        entero = "0"
    if decimales == "":
        decimales = "0"
    precio = round(float(entero + "." + decimales), 2)
    if precio <= 0:
        return False, mensaje
    return True, precio


def validar_vencimiento(texto, fecha_recepcion):
    """Vencimiento en MM/AAAA, posterior a la fecha de recepción (DD/MM/AAAA)."""
    fin_de_mes = convertir_vencimiento(texto)
    if fin_de_mes is None:
        return False, "Vencimiento inválido. Use MM/AAAA, ej. 03/2028."
    recepcion = convertir_fecha(fecha_recepcion)
    if recepcion is not None and fin_de_mes <= recepcion:
        return False, "El vencimiento debe ser posterior a la fecha de recepción."
    return True, formatear_vencimiento(fin_de_mes)
