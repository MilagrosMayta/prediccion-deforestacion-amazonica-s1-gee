def construir_autoencoder(input_shape=(128, 128, 2), latent_filters: int = 32):
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError("Instale TensorFlow con: python -m pip install -e \".[tensorflow]\"") from exc

    inputs = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.Conv2D(16, 3, activation="relu", padding="same")(inputs)
    x = tf.keras.layers.MaxPool2D(2)(x)
    x = tf.keras.layers.Conv2D(latent_filters, 3, activation="relu", padding="same")(x)
    encoded = tf.keras.layers.MaxPool2D(2)(x)
    x = tf.keras.layers.Conv2DTranspose(16, 2, strides=2, activation="relu")(encoded)
    outputs = tf.keras.layers.Conv2DTranspose(input_shape[-1], 2, strides=2)(x)
    return tf.keras.Model(inputs, outputs, name="autoencoder_sentinel1")
