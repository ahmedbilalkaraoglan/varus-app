import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
import math

st.set_page_config(layout="centered")
st.title("HKA Mekanik Aks Analizi (Stable Version)")

uploaded_file = st.file_uploader("Görüntü yükle", type=["jpg", "jpeg", "png"])

# açı hesabı
def angle(v1, v2):
    dot = np.dot(v1, v2)
    mag = np.linalg.norm(v1) * np.linalg.norm(v2)
    if mag == 0:
        return 0
    return np.degrees(np.arccos(np.clip(dot / mag, -1, 1)))

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    w, h = image.size

    st.image(image, caption="Orijinal Görüntü")

    st.info("👉 Görselin üstüne sırayla 3 noktayı tıklayın: HIP → KNEE → ANKLE")

    # session state
    if "points" not in st.session_state:
        st.session_state.points = []

    # click capture (Streamlit hack - image click simulation)
    click = st.experimental_data_editor(
        {"x": [], "y": []},
        num_rows="dynamic",
        key="click_table"
    )

    st.warning("⚠️ Bu tabloda 3 satır gir: x-y koordinatlarını manuel yaz")

    # alternatif daha stabil input
    col1, col2, col3 = st.columns(3)

    with col1:
        hx = st.number_input("Hip X", 0, w)
        hy = st.number_input("Hip Y", 0, h)

    with col2:
        kx = st.number_input("Knee X", 0, w)
        ky = st.number_input("Knee Y", 0, h)

    with col3:
        ax = st.number_input("Ankle X", 0, w)
        ay = st.number_input("Ankle Y", 0, h)

    if st.button("Hesapla"):

        hip = np.array([hx, hy])
        knee = np.array([kx, ky])
        ankle = np.array([ax, ay])

        # çizim
        draw_img = image.copy()
        draw = ImageDraw.Draw(draw_img)

        draw.line([tuple(hip), tuple(knee)], fill="red", width=3)
        draw.line([tuple(knee), tuple(ankle)], fill="red", width=3)

        for p in [hip, knee, ankle]:
            r = 5
            draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill="blue")

        femur = hip - knee
        tibia = ankle - knee

        deg = angle(femur, tibia)

        st.image(draw_img, caption="Analiz")

        st.success(f"HKA Açısı: {deg:.2f}°")

        if deg <= 2:
            st.info("Normal")
        elif deg <= 5:
            st.warning("Hafif deviasyon")
        elif deg <= 10:
            st.warning("Orta deviasyon")
        else:
            st.error("İleri varus/valgus")
