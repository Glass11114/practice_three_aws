
# ============================================================
# PRÁCTICA 3: LIMPIEZA DE DATOS AVANZADA EN PYTHON
# Detección IQR, imputación KNN y comparación de métodos
# ============================================================

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Permite guardar gráficos en EC2 sin interfaz gráfica.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler


# ============================================================
# 1. CONFIGURACIÓN DEL PROYECTO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as archivo:
    config = yaml.safe_load(archivo)

multiplicador_iqr = config["limpieza"]["multiplicador_iqr"]
vecinos_knn = config["limpieza"]["vecinos_knn"]
valores_k = config["comparacion"]["valores_k"]

generar_graficos = config["graficos"]["generar"]
directorio_graficos = BASE_DIR / config["graficos"]["directorio"]

directorio_graficos.mkdir(parents=True, exist_ok=True)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)

print("=" * 75)
print("PRÁCTICA 3: LIMPIEZA DE DATOS AVANZADA EN PYTHON")
print("=" * 75)

print("\n=== 1. CONFIGURACIÓN ===")
print(f"Multiplicador IQR: {multiplicador_iqr}")
print(f"Vecinos KNN: {vecinos_knn}")
print(f"Valores de k para comparar: {valores_k}")


# ============================================================
# 2. GENERACIÓN DEL DATASET ORIGINAL
# ============================================================

data = {
    "edad": [
        25, 30, np.nan, 45, 22,
        120, 35, 28, np.nan, 40
    ],
    "ingreso_mensual": [
        15000, 22000, 18000, np.nan, 12000,
        950000, 25000, 21000, 19000, np.nan
    ],
    "scoring_credito": [
        650, 700, 680, 710, 590,
        800, 670, 640, 620, 730
    ]
}

df_original = pd.DataFrame(data)

print("\n=== 2. DATASET ORIGINAL ===")
print(df_original.to_string(index=True))

print("\nValores faltantes por columna:")
print(df_original.isna().sum().to_string())


# ============================================================
# 3. DETECCIÓN DE VALORES ATÍPICOS CON IQR
# ============================================================

print("\n=== 3. DETECCIÓN DE OUTLIERS MEDIANTE IQR ===")

df_limpieza = df_original.copy()

columnas_outliers = ["edad", "ingreso_mensual"]

for columna in columnas_outliers:

    q1 = df_limpieza[columna].quantile(0.25)
    q3 = df_limpieza[columna].quantile(0.75)

    iqr = q3 - q1

    limite_inferior = q1 - multiplicador_iqr * iqr
    limite_superior = q3 + multiplicador_iqr * iqr

    mascara_outliers = (
        (df_limpieza[columna] < limite_inferior)
        | (df_limpieza[columna] > limite_superior)
    )

    cantidad_outliers = mascara_outliers.sum()

    print(f"\nColumna: {columna}")
    print(f"Q1: {q1:.2f}")
    print(f"Q3: {q3:.2f}")
    print(f"IQR: {iqr:.2f}")
    print(f"Límite inferior: {limite_inferior:.2f}")
    print(f"Límite superior: {limite_superior:.2f}")
    print(f"Valores atípicos detectados: {cantidad_outliers}")

    # Los valores atípicos se sustituyen por NaN.
    # Después serán imputados mediante KNN.
    df_limpieza.loc[mascara_outliers, columna] = np.nan

print("\n=== 4. DATASET DESPUÉS DE TRATAR OUTLIERS ===")
print(df_limpieza.to_string(index=True))

print("\nValores faltantes después de aplicar IQR:")
print(df_limpieza.isna().sum().to_string())


# ============================================================
# 5. IMPUTACIÓN DE VALORES FALTANTES CON KNN
# ============================================================

print("\n=== 5. IMPUTACIÓN MEDIANTE KNN ===")

# Se escalan los atributos para evitar que el ingreso,
# por su magnitud, domine el cálculo de distancias.
scaler = StandardScaler()

datos_escalados = scaler.fit_transform(df_limpieza)

imputador = KNNImputer(
    n_neighbors=vecinos_knn,
    weights="uniform"
)

datos_imputados = imputador.fit_transform(datos_escalados)

# Regresar los valores a su escala original.
datos_recuperados = scaler.inverse_transform(datos_imputados)

df_knn = pd.DataFrame(
    datos_recuperados,
    columns=df_limpieza.columns,
    index=df_limpieza.index
)

print(df_knn.round(2).to_string(index=True))

print("\nValores faltantes después de KNN:")
print(df_knn.isna().sum().to_string())


# ============================================================
# 6. COMPARACIÓN CON MEDIA Y MEDIANA
# ============================================================

print("\n=== 6. COMPARACIÓN DE MÉTODOS DE IMPUTACIÓN ===")

df_media = df_limpieza.fillna(df_limpieza.mean())
df_mediana = df_limpieza.fillna(df_limpieza.median())

comparacion = pd.DataFrame({
    "Original": df_original["ingreso_mensual"],
    "KNN": df_knn["ingreso_mensual"],
    "Media": df_media["ingreso_mensual"],
    "Mediana": df_mediana["ingreso_mensual"]
})

print("\nComparación para ingreso_mensual:")
print(comparacion.round(2).to_string(index=True))


# ============================================================
# 7. EXPERIMENTACIÓN CON DIFERENTES VALORES DE K
# ============================================================

print("\n=== 7. EXPERIMENTACIÓN CON DIFERENTES VALORES DE K ===")

for k in valores_k:

    imputador_k = KNNImputer(n_neighbors=k)

    resultado_k = imputador_k.fit_transform(datos_escalados)

    resultado_k = scaler.inverse_transform(resultado_k)

    df_resultado_k = pd.DataFrame(
        resultado_k,
        columns=df_limpieza.columns,
        index=df_limpieza.index
    )

    print(f"\nResultados utilizando k = {k}")
    print(df_resultado_k.round(2).to_string(index=True))


# ============================================================
# 8. GRÁFICOS ANTES Y DESPUÉS DE LA LIMPIEZA
# ============================================================

print("\n=== 8. GENERACIÓN DE GRÁFICOS ===")

if generar_graficos:

    for columna in columnas_outliers:

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.boxplot(
            [
                df_original[columna].dropna(),
                df_knn[columna].dropna()
            ],
            tick_labels=["Antes", "Después"]
        )

        ax.set_title(f"Limpieza de datos: {columna}")
        ax.set_ylabel(columna.replace("_", " ").capitalize())
        ax.grid(axis="y", alpha=0.25)

        fig.tight_layout()

        ruta = directorio_graficos / f"comparacion_{columna}.png"

        fig.savefig(ruta, dpi=160)
        plt.close(fig)

        print(f"Gráfico guardado: {ruta}")

else:
    print("La generación de gráficos está desactivada.")


# ============================================================
# 9. VALIDACIONES DEL PROCESO
# ============================================================

print("\n=== 9. VALIDACIÓN DE RESULTADOS ===")

if len(df_original) == len(df_knn):
    print("[OK] Se conservaron todos los registros.")
else:
    print("[ERROR] Cambió la cantidad de registros.")

if not df_knn.isna().any().any():
    print("[OK] No quedan valores faltantes.")
else:
    print("[ERROR] Todavía existen valores faltantes.")

if np.isfinite(df_knn.to_numpy()).all():
    print("[OK] Los resultados contienen valores numéricos finitos.")
else:
    print("[ERROR] Se detectaron valores no finitos.")

print("\n=== 10. RESUMEN FINAL ===")

print(f"Registros originales: {len(df_original)}")
print(f"Registros procesados: {len(df_knn)}")
print(f"Valores faltantes originales: {df_original.isna().sum().sum()}")
print(f"Valores faltantes finales: {df_knn.isna().sum().sum()}")

print("\nPROCESO COMPLETADO CORRECTAMENTE")
