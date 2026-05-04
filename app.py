import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import math

st.set_page_config(layout="centered")
st.title("Hip-Knee-Ankle (HKA) Mekanik Aks Analizi")

uploaded_file = st.file_uploader("Görüntü yükle", type=["jpg", "jpeg", "png"])

def angle_with_vertical(v):
    vertical = (0, -1)
    dot = v[0]*vertical[0] + v[1]*vertical[1]
    mag = math.hypot(*v)

    if mag == 0:
        return 0

    cos_theta = dot / mag
    cos_theta = max(min(cos_theta, 1), -1)

    return abs(math.degrees(math.acos(cos_theta)))

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")

    MAX_WIDTH = 700
    w, h = image.size

    if w > MAX_WIDTH:
        ratio = MAX_WIDTH / w
        w, h = int(w * ratio), int(h * ratio)
        image = image.resize((w, h))

    st.image(image)

    st.info("👉 3 nokta koy: Hip → Knee → Ankle")

    canvas = st_canvas(
        background_image=image,
        height=h,
        width=w,
        drawing_mode="point",
        stroke_width=2,
        key="canvas",
    )

    if canvas.json_data:

        objects = canvas.json_data["objects"]

        if len(objects) >= 3:

            pts = [(o["left"], o["top"]) for o in objects[:3]]
            pts = sorted(pts, key=lambda p: p[1])

            hip, knee, ankle = pts

            img_draw = image.copy()
            draw = ImageDraw.Draw(img_draw)

            draw.line([hip, knee], fill="red", width=3)
            draw.line([knee, ankle], fill="red", width=3)

            for p in pts:
                r = 4
                draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill="blue")

            femur = (knee[0]-hip[0], knee[1]-hip[1])
            tibia = (ankle[0]-knee[0], ankle[1]-knee[1])

            femur_angle = angle_with_vertical(femur)
            tibia_angle = angle_with_vertical(tibia)

            deviation = abs(femur_angle - tibia_angle)

            st.success(f"HKA Deviasyonu: {deviation:.2f}°")

            # 🧠 KLİNİK SINIFLAMA (YENİ)
            if deviation <= 2:
                st.success("🟢 Normal (0–2°)")

            elif deviation <= 5:
                st.warning("🟡 Borderline / Hafif sapma (2–5°)")

            elif deviation <= 7:
                st.warning("🟠 Klinik anlamlı deformite (5–7°)")

            else:
                st.error("🔴 Belirgin deformite (>7°)")

            st.image(img_draw, caption="Analiz Görüntüsü")