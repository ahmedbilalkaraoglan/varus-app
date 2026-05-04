import streamlit as st
from PIL import Image, ImageDraw
import numpy as np

st.set_page_config(layout="centered")
st.title("HKA Mekanik Aks Analizi (Stable Click Version)")

uploaded_file = st.file_uploader("Görüntü yükle", type=["jpg", "jpeg", "png"])

# 📐 açı hesabı
def angle(v1, v2):
    dot = np.dot(v1, v2)
    mag = np.linalg.norm(v1) * np.linalg.norm(v2)
    if mag == 0:
        return 0
    return np.degrees(np.arccos(np.clip(dot / mag, -1, 1)))

# 📌 anatomik sıralama (EN KRİTİK FIX)
def order_points(points):
    points = sorted(points, key=lambda p: p[1])  # y eksenine göre sırala

    hip = points[0]

    # knee & ankle ayrımı (mesafeye göre)
    if np.linalg.norm(np.array(points[1]) - np.array(hip)) < np.linalg.norm(np.array(points[2]) - np.array(hip)):
        knee, ankle = points[1], points[2]
    else:
        knee, ankle = points[2], points[1]

    return hip, knee, ankle

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")

    # 📏 görüntü kırpılmasın diye
    st.image(image, use_container_width=True)

    st.info("👉 3 nokta gir: HIP → KNEE → ANKLE (sıra önemli değil)")

    # session state
    if "points" not in st.session_state:
        st.session_state.points = []

    col1, col2, col3 = st.columns(3)

    with col1:
        x1 = st.number_input("X1", 0, 2000)
        y1 = st.number_input("Y1", 0, 2000)

    with col2:
        x2 = st.number_input("X2", 0, 2000)
        y2 = st.number_input("Y2", 0, 2000)

    with col3:
        x3 = st.number_input("X3", 0, 2000)
        y3 = st.number_input("Y3", 0, 2000)

    if st.button("Noktaları Ekle"):
        st.session_state.points = [(x1,y1), (x2,y2), (x3,y3)]

    if len(st.session_state.points) == 3:

        hip, knee, ankle = order_points(st.session_state.points)

        draw_img = image.copy()
        draw = ImageDraw.Draw(draw_img)

        # çizgiler
        draw.line([tuple(hip), tuple(knee)], fill="red", width=3)
        draw.line([tuple(knee), tuple(ankle)], fill="red", width=3)

        # noktalar
        for p in [hip, knee, ankle]:
            r = 5
            draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill="blue")

        femur = np.array(hip) - np.array(knee)
        tibia = np.array(ankle) - np.array(knee)

        deg = angle(femur, tibia)

        st.image(draw_img, use_container_width=True)

        st.success(f"HKA Açısı: {deg:.2f}°")

        if deg <= 2:
            st.info("🟢 Normal")
        elif deg <= 5:
            st.warning("🟡 Hafif deviasyon")
        elif deg <= 10:
            st.warning("🟠 Orta deviasyon")
        else:
            st.error("🔴 İleri varus/valgus")

        if st.button("Reset"):
            st.session_state.points = []
