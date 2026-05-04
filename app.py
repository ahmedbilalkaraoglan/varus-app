import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
from streamlit_image_coordinates import streamlit_image_coordinates

st.set_page_config(layout="centered")
st.title("HKA Mekanik Aks Analizi (Click Version)")

uploaded_file = st.file_uploader("Görüntü yükle", type=["jpg", "jpeg", "png"])

def angle(v1, v2):
    dot = np.dot(v1, v2)
    mag = np.linalg.norm(v1) * np.linalg.norm(v2)
    if mag == 0:
        return 0
    return np.degrees(np.arccos(np.clip(dot / mag, -1, 1)))

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    w, h = image.size

    st.info("👉 Görsel üzerine sırayla tıkla: HIP → KNEE → ANKLE")

    # 📌 click capture
    clicked = streamlit_image_coordinates(image)

    if "points" not in st.session_state:
        st.session_state.points = []

    if clicked:
        if len(st.session_state.points) < 3:
            st.session_state.points.append((clicked["x"], clicked["y"]))

    st.write("📍 Noktalar:", st.session_state.points)

    if len(st.session_state.points) == 3:

        hip, knee, ankle = [np.array(p) for p in st.session_state.points]

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
            st.warning("Hafif")
        elif deg <= 10:
            st.warning("Orta")
        else:
            st.error("İleri deviasyon")

        if st.button("Reset"):
            st.session_state.points = []
