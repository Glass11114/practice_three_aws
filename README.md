# Práctica 2: Generación y Estructuración de un Esquema Estrella

**Modelado dimensional con Python, Pandas y NumPy**

## 1. Descripción del proyecto

Esta práctica consiste en simular un conjunto de transacciones de ventas de un sistema operacional (OLTP) y transformarlo en un modelo dimensional de tipo estrella, utilizando Python y la biblioteca Pandas.

El proceso permite organizar la información en tres tablas de dimensiones y una tabla de hechos, facilitando el análisis de las transacciones, los productos, los clientes y las fechas de venta.

La ejecución se realiza en una instancia EC2 de AWS con Ubuntu, utilizando un entorno virtual de Python.

## 2. Objetivo

Desarrollar un proceso de transformación de datos que permita generar 500 transacciones simuladas y estructurarlas en un esquema estrella, mediante la creación de llaves subrogadas, relaciones entre tablas y métricas de ventas.

**Objetivos específicos:**

- Generar datos operativos ficticios utilizando NumPy y Pandas.
- Identificar atributos descriptivos y construir tablas dimensionales.
- Generar llaves subrogadas para identificar registros.
- Relacionar las dimensiones con la tabla de hechos mediante operaciones `merge()`.
- Calcular el monto total de cada transacción.
- Incorporar atributos adicionales para enriquecer el análisis temporal.
- Validar la integridad de los datos transformados.

## 3. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Python 3 | Desarrollo del proceso de transformación |
| Pandas | Manipulación y estructuración de DataFrames |
| NumPy | Generación de datos sintéticos |
| PyYAML | Lectura de parámetros de configuración |
| AWS EC2 | Entorno de ejecución del proyecto |
| Ubuntu | Sistema operativo de la instancia |
| Git y GitHub | Control de versiones y documentación |

## 4. Estructura del proyecto

```text
practicas-aws/
│
├── .gitignore
├── practica1/
│
└── practica2/
    ├── practica2.py
    ├── config.yaml
    ├── config.example.yaml
    ├── requirements.txt
    └── README.md
```

**Descripción de los archivos:**

- `practica2.py`: contiene el proceso completo de generación, transformación y validación de datos.
- `config.yaml`: almacena los parámetros de ejecución y se mantiene fuera del repositorio.
- `config.example.yaml`: proporciona una plantilla de configuración para reproducir el proyecto.
- `requirements.txt`: contiene las dependencias necesarias.
- `README.md`: documenta el desarrollo y funcionamiento de la práctica.
- `.gitignore`: excluye archivos privados y temporales del control de versiones.

## 5. Instalación y ejecución

### 5.1. Acceder al proyecto

Desde la terminal de la instancia EC2:

```bash
cd ~/practicas-aws/practica2
```

### 5.2. Activar el entorno virtual

```bash
source ~/accessbucket/accessbucket/bin/activate
```

### 5.3. Instalar dependencias

```bash
python3 -m pip install -r requirements.txt
```

### 5.4. Preparar la configuración

Si el archivo `config.yaml` no existe, se puede generar a partir de la plantilla:

```bash
cp config.example.yaml config.yaml
```

Los principales parámetros son:

| Parámetro | Valor |
|---|---|
| Semilla aleatoria | 101 |
| Cantidad de transacciones | 500 |
| Fecha inicial | 2026-01-01 |
| Día de la semana | Habilitado |
| Indicador de fin de semana | Habilitado |
| Persistencia en base de datos | Deshabilitada |

### 5.5. Ejecutar el programa

```bash
python3 practica2.py
```

El programa muestra en la terminal las transacciones generadas, las tablas dimensionales, la tabla de hechos, las validaciones y los indicadores generales de ventas.

## 6. Desarrollo del proceso

### 6.1. Generación de datos operativos (OLTP)

Se utiliza NumPy para simular 500 transacciones de ventas con información de clientes, ciudades, productos, categorías, precios y cantidades.

Cada transacción cuenta con un identificador único y una fecha de registro.

Los datos generados se almacenan inicialmente en el DataFrame `df_operativo`.

### 6.2. Construcción de Dim_Cliente

Se seleccionan los atributos `cliente_nombre` y `cliente_ciudad`.

Mediante `drop_duplicates()` se eliminan las combinaciones repetidas y se genera `id_cliente_sk` como llave subrogada.

El resultado contiene **9 combinaciones únicas de cliente y ciudad**.

### 6.3. Construcción de Dim_Producto

Se seleccionan los atributos `producto_nombre`, `categoria_prod` y `precio_unitario`.

Se eliminan las combinaciones duplicadas y se asigna una llave subrogada denominada `id_producto_sk`.

El resultado contiene **27 combinaciones únicas de productos, categorías y precios**.

### 6.4. Construcción de Dim_Tiempo

Se extraen las fechas únicas de las transacciones y se generan los siguientes atributos:

- `id_tiempo_sk`: identificador de fecha con formato AAAAMMDD.
- `fecha_completa`: fecha de la transacción.
- `anio`: año.
- `mes`: mes.
- `dia`: día del mes.
- `dia_semana`: nombre del día de la semana.
- `es_fin_semana`: indicador que identifica sábados y domingos.

El resultado contiene **21 fechas únicas**.

### 6.5. Construcción de Fact_Ventas

Se utilizan operaciones `merge()` para relacionar los registros operativos con las tres dimensiones.

La tabla de hechos contiene los siguientes campos:

| Campo | Descripción |
|---|---|
| `id_transaccion` | Identificador único de la venta |
| `id_cliente_sk` | Referencia a Dim_Cliente |
| `id_producto_sk` | Referencia a Dim_Producto |
| `id_tiempo_sk` | Referencia a Dim_Tiempo |
| `cantidad` | Unidades vendidas |
| `monto_total` | Importe calculado de la transacción |

El campo `monto_total` se obtiene mediante:

```python
fact_ventas["monto_total"] = (
    fact_ventas["cantidad"] * fact_ventas["precio_unitario"]
)
```

La tabla final conserva los **500 registros originales**.

## 7. Modelo dimensional

El proyecto implementa un esquema estrella compuesto por una tabla de hechos central y tres dimensiones relacionadas.

```text
                  DIM_CLIENTE
                 id_cliente_sk
                       |
                       |
DIM_PRODUCTO ---- FACT_VENTAS ---- DIM_TIEMPO
id_producto_sk    id_transaccion   id_tiempo_sk
                  id_cliente_sk
                  id_producto_sk
                  id_tiempo_sk
                  cantidad
                  monto_total
```

Las dimensiones proporcionan el contexto descriptivo, mientras que la tabla de hechos almacena las métricas utilizadas para el análisis de ventas.

## 8. Adecuaciones realizadas

Como extensión del ejercicio original, se incorporaron dos atributos adicionales en `Dim_Tiempo`:

**Día de la semana (`dia_semana`):** permite identificar el día correspondiente a cada transacción.

**Fin de semana (`es_fin_semana`):** permite distinguir entre días laborales y fines de semana.

También se incorporaron mejoras de visualización en consola y validaciones para comprobar que:

- Se conservan las 500 transacciones.
- No existen llaves foráneas sin asignar.
- Los identificadores de transacción son únicos.
- Los montos de venta se calculan correctamente.

Estas adecuaciones facil