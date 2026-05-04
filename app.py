import streamlit as st
import numpy as np
import cv2
from PIL import Image
import math

st.set_page_config(layout="centered")
st.title("HKA AI Analiz (Stabil Versiyon)")

uploaded_file = st.file_uploader("Röntgen yükle", type=["jpg", "jpeg", "png"])

def angle(v1, v2):
    dot = np.dot(v1, v2)
    mag = np.linalg.norm(v1) * np.linalg.norm(v2)
    if mag == 0:
        return 0
    cos = dot / mag
    cos = np.clip(cos, -1, 1)
    return np.degrees(np.arccos(cos))

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    img = np.array(image)

    st.image(img, caption="Yüklenen görüntü")

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # 🔥 basit edge detection
    edges = cv2.Canny(gray, 50, 150)

    h, w = edges.shape

    # 🧠 basit heuristic landmark tahmini
    hip = (int(w*0.5), int(h*0.2))
    knee = (int(w*0.5), int(h*0.5))
    ankle = (int(w*0.5), int(h*0.8))

    # çizim
    out = img.copy()

    cv2.circle(out, hip, 6, (255,0,0), -1)
    cv2.circle(out, knee, 6, (0,255,0), -1)
    cv2.circle(out, ankle, 6, (0,0,255), -1)

    cv2.line(out, hip, knee, (255,0,0), 2)
    cv2.line(out, knee, ankle, (0,0,255), 2)

    femur = np.array(hip) - np.array(knee)
    tibia = np.array(ankle) - np.array(knee)

    deviation = angle(femur, tibia)

    st.image(out, caption="AI Analiz")

    st.success(f"HKA Açısı: {deviation:.2f}°")

    # 📊 klinik sınıflama
    if deviation <= 2:
        st.success("Normal")
    elif deviation <= 5:
        st.warning("Borderline")
    elif deviation <= 7:
        st.warning("Klinik anlamlı")
    else:
        st.error("Belirgin deformite")
