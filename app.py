import streamlit as st
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
import math

st.set_page_config(layout="centered")
st.title("HKA AI v2 (YOLO Pose)")

model = YOLO("yolov8n-pose.pt")  # pretrained model

uploaded_file = st.file_uploader("Röntgen yükle", type=["jpg", "jpeg", "png"])

def angle(v1, v2):
    dot = np.dot(v1, v2)
    mag = np.linalg.norm(v1)*np.linalg.norm(v2)
    if mag == 0:
        return 0
    return np.degrees(np.arccos(np.clip(dot/mag, -1, 1)))

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    img = np.array(image)

    st.image(img, caption="Input")

    results = model(img)

    out = img.copy()

    for r in results:

        if r.keypoints is None:
            st.error("No pose detected")
            st.stop()

        kpts = r.keypoints.xy[0].cpu().numpy()

        # COCO keypoints:
        # 11 = left hip
        # 13 = left knee
        # 15 = left ankle

        hip = kpts[11]
        knee = kpts[13]
        ankle = kpts[15]

        hip = hip.astype(int)
        knee = knee.astype(int)
        ankle = ankle.astype(int)

        cv2.circle(out, tuple(hip), 6, (255,0,0), -1)
        cv2.circle(out, tuple(knee), 6, (0,255,0), -1)
        cv2.circle(out, tuple(ankle), 6, (0,0,255), -1)

        cv2.line(out, tuple(hip), tuple(knee), (255,0,0), 2)
        cv2.line(out, tuple(knee), tuple(ankle), (0,0,255), 2)

        femur = hip - knee
        tibia = ankle - knee

        deviation = angle(femur, tibia)

        st.image(out, caption="YOLO AI Output")

        st.success(f"HKA: {deviation:.2f}°")

        if deviation <= 2:
            st.success("Normal")
        elif deviation <= 5:
            st.warning("Borderline")
        elif deviation <= 7:
            st.warning("Clinically significant")
        else:
            st.error("Severe deformity")
