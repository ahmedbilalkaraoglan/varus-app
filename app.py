import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import math

st.set_page_config(layout="centered")
st.title("HKA Mekanik Aks Analizi (Stable Version)")

uploaded_file = st.file_uploader("Görüntü yükle", type=["jpg", "jpeg", "png"])

# 📐 açı hesabı
def angle(v1, v2):
    dot = np.dot(v1, v2)
    mag = np.linalg.norm(v1) * np.linalg.norm(v2)
    if mag == 0:
        return 0
    return np.degrees(np.arccos(np.clip(dot / mag, -1, 1)))

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")

    # resize (çok büyük görüntüleri kontrol eder)
    MAX_WIDTH = 700
    w, h = image.size

    if w > MAX_WIDTH:
        ratio = MAX_WIDTH / w
        w, h = int(w * ratio), int(h * ratio)
        image = image.resize((w, h))

    st.image(image, caption="Orijinal Görüntü")

    st.info("👉 HIP → KNEE → ANKLE koordinatlarını gir")

    # 📌 INPUTLAR
    col1, col2, col3 = st.columns(3)

    with col1:
        hx = st.number_input("Hip X", 0, w, 0)
        hy = st.number_input("Hip Y", 0, h, 0)

    with col2:
        kx = st.number_input("Knee X", 0, w, 0)
        ky = st.number_input("Knee Y", 0, h, 0)

    with col3:
        ax = st.number_input("Ankle X", 0, w, 0)
        ay = st.number_input("Ankle Y", 0, h, 0)

    if st.button("Hesapla"):

        hip = np.array([hx, hy])
        knee = np.array([kx, ky])
        ankle = np.array([ax, ay])

        # çizim
        draw_img = image.copy()
        draw = ImageDraw.Draw(draw_img)

        # çizgiler
        draw.line([tuple(hip), tuple(knee)], fill="red", width=3)
        draw.line([tuple(knee), tuple(ankle)], fill="red", width=3)

        # noktalar
        for p in [hip, knee, ankle]:
            r = 5
            draw.ellipse(
                (p[0]-r, p[1]-r, p[0]+r, p[1]+r),
                fill="blue"
            )

        # vektörler
        femur = hip - knee
        tibia = ankle - knee

        deg = angle(femur, tibia)

        st.image(draw_img, caption="Analiz Sonucu")

        st.success(f"HKA Açısı: {deg:.2f}°")

        # klinik yorum
        if deg <= 2:
            st.info("🟢 Normal aks")
        elif deg <= 5:
            st.warning("🟡 Hafif deviasyon")
        elif deg <= 10:
            st.warning("🟠 Orta deviasyon")
        else:
            st.error("🔴 İleri varus / valgus")
