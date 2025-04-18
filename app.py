# -*- coding: utf-8 -*-
"""app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FqjGxl1az15bL5Bj_o8x5TLXz7SmCaH4
"""

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py

from PIL import Image, ImageOps
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import cv2
import os
import streamlit as st

# Vérification des dépendances
try:
    st.set_page_config(layout="wide")
except Exception as e:
    st.warning(f"Erreur de configuration : {e}")

# Chargement du modèle
@st.cache_resource
def load_model():
    try:
        model = tf.keras.models.load_model('keras_model.h5', compile=False)
        return model
    except Exception as e:
        st.error(f"Erreur de chargement du modèle : {e}")
        return None

model = load_model()
class_names = ['bus', 'camion,', 'minibus', 'suv']

# Interface utilisateur
st.title("🚗 Système de reconnaissance de Véhicules")
st.markdown("""
<style>
.stApp { max-width: 900px; margin: 0 auto; }
.st-bq { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# Fonction de prétraitement
def preprocess_image(image):
    try:
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        image_array = np.asarray(image)
        normalized_image = (image_array.astype(np.float32) / 127.5) - 1
        return normalized_image
    except Exception as e:
        st.error(f"Erreur de prétraitement : {e}")
        return None

# Upload d'image
uploaded_file = st.file_uploader("Importez une image de véhicule...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None and model is not None:
    try:
        # Affichage image originale
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption='Image importée', width=300)

        # Prétraitement
        processed_image = preprocess_image(image)

        if processed_image is not None:
            # Prédiction
            data = np.expand_dims(processed_image, axis=0)
            prediction = model.predict(data)
            class_idx = np.argmax(prediction[0])
            confidence = prediction[0][class_idx]

            # Résultats
            st.success(f"""
            **Résultat :** {class_names[class_idx].upper()}
            **Confiance :** {confidence:.2%}
            """)

            # Saliency Map
            st.subheader("Analyse des zones importantes")

            # Calcul avec OpenCV pour plus de robustesse
            image_array = np.asarray(image)
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            saliency = cv2.saliency.StaticSaliencyFineGrained_create()
            _, saliency_map = saliency.computeSaliency(gray)

            # Affichage
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,6))
            ax1.imshow(image_array)
            ax1.set_title("Image Originale")
            ax1.axis('off')

            ax2.imshow(saliency_map, cmap='hot')
            ax2.set_title("Saliency Map")
            ax2.axis('off')

            st.pyplot(fig)

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")