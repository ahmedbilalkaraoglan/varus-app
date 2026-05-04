import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import numpy as np

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

    st.info("👉 3 nokta koy: HIP → KNEE → ANKLE")

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=5,
        stroke_color="red",
        background_image=image,
        height=h,
        width=w,
        drawing_mode="point",
        key="canvas"
    )

    if canvas_result.json_data:

        objects = canvas_result.json_data["objects"]

        if len(objects) >= 3:

            pts = [(o["left"], o["top"]) for o in objects[:3]]

            # sıralama düzeltme
            pts = sorted(pts, key=lambda p: p[1])

            hip, knee, ankle = pts

            img_draw = image.copy()
            draw = ImageDraw.Draw(img_draw)

            draw.line([hip, knee], fill="red", width=3)
            draw.line([knee, ankle], fill="red", width=3)

            for p in pts:
                r = 5
                draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill="blue")

            femur = np.array(hip) - np.array(knee)
            tibia = np.array(ankle) - np.array(knee)

            deg = angle(femur, tibia)

            st.image(img_draw)

            st.success(f"HKA Açısı: {deg:.2f}°")

            if st.button("Reset"):
                st.experimental_rerun()
