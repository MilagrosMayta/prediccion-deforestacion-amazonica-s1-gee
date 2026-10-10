# IA generativa — alcance actual

El nombre del proyecto incluye IA generativa, pero la adquisición de datos debe mantenerse desacoplada del modelo final.

Esta versión incluye dos autoencoders mínimos (PyTorch y TensorFlow) únicamente como bloques experimentales de software. No constituyen el modelo científico definitivo ni una validación de capacidad predictiva.

Antes de definir el modelo final se requiere acordar:

- variable objetivo;
- horizonte de predicción;
- unidad espacial;
- construcción de etiquetas;
- división temporal de entrenamiento/validación/prueba;
- métricas;
- tratamiento de desbalance;
- rol exacto del componente generativo.
