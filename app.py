import streamlit as st
import numpy as np
import cv2
from PIL import Image
from ultralytics import YOLO

st.set_page_config(layout="centered")
st.title("HKA AI (OpenCV + YOLO)")

model = YOLO("yolov8n-pose.pt")

uploaded_file = st.file_uploader("Röntgen yükle", type=["jpg", "jpeg", "png"])

def angle(v1, v2):
    dot = np.dot(v1, v2)
    mag = np.linalg.norm(v1) * np.linalg.norm(v2)
    if mag == 0:
        return 0
    return np.degrees(np.arccos(np.clip(dot/mag, -1, 1)))

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    img = np.array(image)

    st.image(img, caption="Input")

    # 🔥 OpenCV preprocessing (zorladık)
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        st.image(edges, caption="Edges (OpenCV)")
    except Exception as e:
        st.warning(f"OpenCV failed, fallback used: {e}")

    # 🔥 YOLO pose
    results = model(img)

    out = img.copy()

    for r in results:

        if r.keypoints is None:
            st.error("No keypoints detected")
            st.stop()

        kpts = r.keypoints.xy[0].cpu().numpy()

        hip = kpts[11].astype(int)
        knee = kpts[13].astype(int)
        ankle = kpts[15].astype(int)

        cv2.circle(out, tuple(hip), 6, (255,0,0), -1)
        cv2.circle(out, tuple(knee), 6, (0,255,0), -1)
        cv2.circle(out, tuple(ankle), 6, (0,0,255), -1)

        cv2.line(out, tuple(hip), tuple(knee), (255,0,0), 2)
        cv2.line(out, tuple(knee), tuple(ankle), (0,0,255), 2)

        femur = hip - knee
        tibia = ankle - knee

        deviation = angle(femur, tibia)

        st.image(out, caption="AI Output")

        st.success(f"HKA: {deviation:.2f}°")

        if deviation <= 2:
            st.success("Normal")
        elif deviation <= 5:
            st.warning("Borderline")
        elif deviation <= 7:
            st.warning("Clinical")
        else:
            st.error("Severe")
