from __future__ import annotations

import sys
from pathlib import Path


def entrenar_random_forest(csv_path: str | Path, etiqueta: str, modelo_salida: str | Path, grupo: str | None = None):
    try:
        import joblib
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import classification_report
        from sklearn.model_selection import GroupShuffleSplit, train_test_split
    except ImportError as exc:
        raise RuntimeError(
            "Faltan dependencias ML. Instale: python -m pip install -e \".[ml]\""
        ) from exc

    df = pd.read_csv(csv_path)
    for col in (etiqueta, grupo):
        if col is not None and col not in df.columns:
            raise ValueError(f"No existe la columna '{col}'.")
    X = df.drop(columns=[c for c in (etiqueta, grupo) if c]).select_dtypes(include="number")
    y = df[etiqueta]
    if X.empty:
        raise ValueError("No existen columnas numéricas para entrenar.")
    if grupo:  # zonas/bloques completos fuera del entrenamiento: evita fuga por vecindad espacial
        tr, te = next(GroupShuffleSplit(test_size=0.25, random_state=42).split(X, y, df[grupo]))
        X_train, X_test, y_train, y_test = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]
    else:
        print("AVISO: sin --grupo el reparto es aleatorio por fila; con píxeles vecinos las métricas salen optimistas.", file=sys.stderr)
        estratificar = y.value_counts().min() >= 2
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y if estratificar else None
        )
    model = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    reporte = classification_report(y_test, pred, output_dict=False, zero_division=0)
    modelo_salida = Path(modelo_salida)
    modelo_salida.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": list(X.columns)}, modelo_salida)
    return reporte
