# Registro digital de productos recibidos – RODRIFARMA

Prototipo en **Python 3** (consola) para registrar, validar, buscar, ordenar y
almacenar de forma permanente los productos que recibe una farmacia de
droguerías y laboratorios, con alerta de productos vencidos o por vencer.

Curso: Fundamentos de Programación (CIIN1205P) – Desafío:
*Del archivador al algoritmo, un prototipo para la mesa de partes digital*.

## Requisitos y ejecución
- Python 3.8 o superior (solo biblioteca estándar, no hay que instalar nada).
- `python main.py` para usar el sistema.
- `python pruebas.py` para ejecutar las pruebas automáticas.

## Estructura
| Archivo | Responsabilidad |
|---|---|
| `main.py` | Menú, lectura de datos por consola y presentación de resultados |
| `validaciones.py` | Validación y normalización de cada campo; conversión de fechas |
| `registros.py` | Arreglos paralelos, registrar, búsqueda lineal, ordenamiento por selección, estados |
| `archivos.py` | Guardar y cargar `expedientes.txt` |
| `pruebas.py` | Pruebas automáticas (normales, límite y de error) |
| `expedientes.txt` | Datos de ejemplo (reemplazar por los datos reales de la observación) |

## Menú
`1` Registrar · `2` Buscar por código · `3` Listar · `4` Ordenar (código o vencimiento) ·
`5` Vencidos y por vencer · `6` Actualizar precio · `7` Guardar · `0` Salir

## Formato del archivo `expedientes.txt`
Un registro por línea, 11 campos separados por `|`:

`código | factura | fecha recepción | distribuidora | RUC (o -) | producto | lote | registro sanitario | cantidad | precio | vencimiento`

## Reglas de validación
| Campo | Regla |
|---|---|
| Código | Lo genera el sistema: `ING-0001` … `ING-9999`, sin repetir |
| Factura | `SERIE-NÚMERO`: serie de 4 caracteres (1.º letra), número de 1 a 8 dígitos. Ej. `F001-00123` |
| Fecha de recepción | `DD/MM/AAAA`, fecha real (Enter = hoy) |
| Distribuidora / Producto | No vacío, hasta 60 caracteres, sin `|` |
| RUC | Opcional; si se escribe, exactamente 11 dígitos |
| Lote | 3 a 20 caracteres: letras, números y guion. Ej. `L2406` |
| Registro sanitario | 5 a 20 caracteres: letras, números y guion. Ej. `EN-12345` |
| Cantidad | Entero mayor que 0 |
| Precio | Mayor que 0, hasta 2 decimales (acepta `5,50` y `S/ 5.00`) |
| Vencimiento | `MM/AAAA`, posterior a la fecha de recepción |

## Estados (calculados con la fecha de hoy)
Un producto con vencimiento `MM/AAAA` es válido hasta el **último día de ese mes**.
- **Vencido**: ese último día ya pasó.
- **Por vencer**: vence dentro de los próximos 3 meses (incluye hoy).
- **Recibido**: vence más adelante.

> Los estados del archivo de ejemplo dependen del día en que se ejecute el programa.

## Casos de prueba manuales sugeridos (para capturas)
| Caso | Qué ingresar | Resultado esperado |
|---|---|---|
| Registro correcto | Baptrin, `F001-00123`, `14/10/2026`, lote `L2406`, `EN-12345`, 10, `5.00`, `03/2028` | Ficha del registro y "Datos guardados" |
| Factura inválida | `F001` | Error de formato y vuelve a preguntar |
| Fecha inexistente | `31/02/2026` | Error de fecha |
| RUC incompleto | `2012345678` (10 dígitos) | Error: debe tener 11 dígitos |
| Cantidad inválida | `0`, `-5`, `abc` | Error: entero mayor que 0 |
| Precio inválido | `0`, `-1`, `5.555` | Error de precio |
| Vencimiento anterior | recepción `14/10/2026`, vence `09/2026` | Error: debe ser posterior |
| Producto vencido | recepción `10/03/2026`, vence `08/2026` | Estado VENCIDO |
| Búsqueda | `ING-0001`, `ing-0001` o `1` | Ficha del producto |
| Código inexistente | `ING-0099` | "No se encontró ningún registro…" |
| Ordenar | opción 4 → 2 | Listado por vencimiento |
| Persistencia | Salir (0) y volver a ejecutar | Los registros siguen ahí |
