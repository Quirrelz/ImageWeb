import cv2
import streamlit as st
import numpy as np
from PIL import Image

def cartoonization(img, filter_option):
    # 检查图像的通道数，如果是灰度图就跳过转换
    if len(img.shape) == 3 and img.shape[2] == 3:  # 彩色图（3通道）
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif len(img.shape) == 2:  # 已经是灰度图（1通道）
        gray = img
    else:  # 其他情况，可能是 RGBA 图像，转换为 RGB
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 根据用户选择的卡通效果进行处理
    if filter_option == "铅笔素描":
        value = st.sidebar.slider('调整素描的亮度（值越高，素描越亮）', 0.0, 300.0, 250.0)
        kernel = st.sidebar.slider('调整素描边缘的粗细（值越高，边缘越粗）', 1, 99, 25, step=2)

        gray_blur = cv2.GaussianBlur(gray, (kernel, kernel), 0)
        cartoon_image = cv2.divide(gray, gray_blur, scale=value)

    elif filter_option == "细节增强":
        smooth = st.sidebar.slider('调整图像的平滑度（值越高，图像越平滑）', 3, 99, 5, step=2)
        kernel = st.sidebar.slider('调整图像的锐度（值越低，图像越锐利）', 1, 21, 3, step=2)
        edge_preserve = st.sidebar.slider('调整颜色平滑效果（低：只平滑相似颜色，高：平滑不相似颜色）', 0.0, 1.0, 0.5)

        gray = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

        color = cv2.detailEnhance(img, sigma_s=smooth, sigma_r=edge_preserve)
        cartoon_image = cv2.bitwise_and(color, color, mask=edges)

    elif filter_option == "铅笔边缘":
        kernel = st.sidebar.slider('调整素描的锐度（值越低，图像越锐利）', 1, 99, 25, step=2)
        laplacian_filter = st.sidebar.slider('调整边缘检测的强度（值越高，边缘越明显）', 3, 9, 3, step=2)
        noise_reduction = st.sidebar.slider('调整素描的噪声效果（值越高，噪声越多）', 10, 255, 150)

        gray = cv2.medianBlur(gray, kernel)
        edges = cv2.Laplacian(gray, -1, ksize=laplacian_filter)
        edges_inv = 255 - edges

        dummy, cartoon_image = cv2.threshold(edges_inv, noise_reduction, 255, cv2.THRESH_BINARY)

    elif filter_option == "双边滤波":
        smooth = st.sidebar.slider('调整图像的平滑度（值越高，图像越平滑）', 3, 99, 5, step=2)
        kernel = st.sidebar.slider('调整图像的锐度（值越低，图像越锐利）', 1, 21, 3, step=2)
        edge_preserve = st.sidebar.slider('调整颜色平滑效果（低：只平滑相似颜色，高：平滑不相似颜色）', 1, 100, 50)

        gray = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

        color = cv2.bilateralFilter(img, smooth, edge_preserve, smooth)
        cartoon_image = cv2.bitwise_and(color, color, mask=edges)

    return cartoon_image


###############################################################################

st.write("""
          # 转换您的图片为卡通效果！
          """
         )

st.write("这是一个将您的照片转化为卡通效果的应用。")

file = st.sidebar.file_uploader("请上传一张图片文件", type=["jpg", "png"])

if file is None:
    st.text("您尚未上传图片文件")
else:
    image = Image.open(file)
    img = np.array(image)

    option = st.sidebar.selectbox(
        '您想应用哪种卡通滤镜？',
        ('铅笔素描', '细节增强', '铅笔边缘', '双边滤波'))

    st.text("您的原始图片")
    st.image(image, use_container_width=True)

    st.text("您的卡通化图片")
    cartoon_image = cartoonization(img, option)

    st.image(cartoon_image, use_container_width=True)
