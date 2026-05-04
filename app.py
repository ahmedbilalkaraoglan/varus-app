import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
from ultralytics import YOLO
import math

st.set_page_config(layout="centered")
st.title("HKA AI - Final Stable Version")

# 🧠 LAZY LOAD MODEL (CRASH ENGELİ)
@st.cache_resource
def load_model():
    return YOLO("yolov8n-pose.pt")

model = load_model()

uploaded_file = st.file_uploader("Röntgen yükle", type=["jpg", "jpeg", "png"])

def angle(v1, v2):
    dot = np.dot(v1, v2)
    mag = np.linalg.norm(v1) * np.linalg.norm(v2)
    if mag == 0:
        return 0
    return np.degrees(np.arccos(np.clip(dot / mag, -1, 1)))

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    img = np.array(image)

    st.image(image, caption="Input Image")

    results = model(img)

    for r in results:

        if r.keypoints is None:
            st.error("No keypoints detected")
            st.stop()

        kpts = r.keypoints.xy[0].cpu().numpy()

        # COCO keypoints
        hip = kpts[11].astype(int)
        knee = kpts[13].astype(int)
        ankle = kpts[15].astype(int)

        # 🖼 PIL DRAW (CV2 YOK)
        draw_img = image.copy()
        draw = ImageDraw.Draw(draw_img)

        r_point = 5

        # noktalar
        draw.ellipse(
            [hip[0]-r_point, hip[1]-r_point, hip[0]+r_point, hip[1]+r_point],
            fill=(255, 0, 0)
        )
        draw.ellipse(
            [knee[0]-r_point, knee[1]-r_point, knee[0]+r_point, knee[1]+r_point],
            fill=(0, 255, 0)
        )
        draw.ellipse(
            [ankle[0]-r_point, ankle[1]-r_point, ankle[0]+r_point, ankle[1]+r_point],
            fill=(0, 0, 255)
        )

        # çizgiler
        draw.line([tuple(hip), tuple(knee)], fill=(255, 0, 0), width=2)
        draw.line([tuple(knee), tuple(ankle)], fill=(0, 0, 255), width=2)

        # vektörler
        femur = hip - knee
        tibia = ankle - knee

        deviation = angle(femur, tibia)

        st.image(draw_img, caption="AI Output")

        st.success(f"HKA Açısı: {deviation:.2f}°")

        # klinik sınıflama
        if deviation <= 2:
            st.success("Normal")
        elif deviation <= 5:
            st.warning("Borderline")
        elif deviation <= 7:
            st.warning("Klinik anlamlı")
        else:
            st.error("Belirgin deformite")
