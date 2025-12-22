import cv2
import streamlit as st
import numpy as np
from PIL import Image
import io

def cartoonization(img, filter_option):
    # 灰度准备
    if len(img.shape) == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif len(img.shape) == 2:
        gray = img
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    params = {}  # 用来记录参数，生成下载文件名

    if filter_option == "真实素描":
        value = st.sidebar.slider('调整素描的亮度（值越高，素描越亮）', 0.0, 300.0, 250.0)
        kernel = st.sidebar.slider('调整素描边缘的粗细（值越高，边缘越粗）', 1, 99, 25, step=2)

        params = {"value": value, "kernel": kernel}

        gray_blur = cv2.GaussianBlur(gray, (kernel, kernel), 0)
        cartoon_image = cv2.divide(gray, gray_blur, scale=value)

    elif filter_option == "漫画渲染":
        smooth = st.sidebar.slider('调整图像的平滑度（值越高，图像越平滑）', 3, 99, 5, step=2)
        kernel = st.sidebar.slider('调整图像的锐度（值越低，图像越锐利）', 1, 21, 3, step=2)
        edge_preserve = st.sidebar.slider('调整颜色平滑效果（低：只平滑相似颜色，高：平滑不相似颜色）', 0.0, 1.0, 0.5)

        params = {"smooth": smooth, "kernel": kernel, "edge": edge_preserve}

        gray2 = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        color = cv2.detailEnhance(img, sigma_s=smooth, sigma_r=edge_preserve)
        cartoon_image = cv2.bitwise_and(color, color, mask=edges)

    elif filter_option == "黑白线稿":
        kernel = st.sidebar.slider('调整素描的锐度（值越低，图像越锐利）', 1, 99, 25, step=2)
        laplacian_filter = st.sidebar.slider('调整边缘检测的强度（值越高，边缘越明显）', 3, 9, 3, step=2)
        noise_reduction = st.sidebar.slider('调整素描的噪声效果（值越高，噪声越多）', 10, 255, 150)

        params = {"kernel": kernel, "lap": laplacian_filter, "thr": noise_reduction}

        gray2 = cv2.medianBlur(gray, kernel)
        edges = cv2.Laplacian(gray2, -1, ksize=laplacian_filter)
        edges_inv = 255 - edges
        _, cartoon_image = cv2.threshold(edges_inv, noise_reduction, 255, cv2.THRESH_BINARY)

    elif filter_option == "卡通插画":
        smooth = st.sidebar.slider('调整图像的平滑度（值越高，图像越平滑）', 3, 99, 5, step=2)
        kernel = st.sidebar.slider('调整图像的锐度（值越低，图像越锐利）', 1, 21, 3, step=2)
        edge_preserve = st.sidebar.slider('调整颜色平滑效果（低：只平滑相似颜色，高：平滑不相似颜色）', 1, 100, 50)

        params = {"smooth": smooth, "kernel": kernel, "edge": edge_preserve}

        gray2 = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, smooth, edge_preserve, smooth)
        cartoon_image = cv2.bitwise_and(color, color, mask=edges)

    return cartoon_image, params


def safe_name(s: str) -> str:
    """文件名安全：去掉不适合做文件名的字符"""
    keep = []
    for ch in s:
        if ch.isalnum() or ch in ['_', '-', '.']:
            keep.append(ch)
        else:
            keep.append('_')
    return ''.join(keep)


st.write("# 转换您的图片为卡通效果！")
st.write("这是一个将您的照片转化为卡通效果的应用。")

file = st.sidebar.file_uploader("请上传一张图片文件", type=["jpg", "png"])

if file is None:
    st.text("您尚未上传图片文件")
else:
    image = Image.open(file).convert("RGB")  # 强制变成 RGB 三通道
    img_rgb = np.array(image)               # RGB
    img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)  # 转成 OpenCV 习惯的 BGR

    option = st.sidebar.selectbox(
        '您想应用哪种卡通滤镜？',
        ('真实素描', '漫画渲染', '黑白线稿', '卡通插画')
    )

    st.text("您的原始图片")
    st.image(image, width="stretch")

    st.text("您的卡通化图片")
    cartoon_image, params = cartoonization(img, option)
    if cartoon_image.ndim == 3:
        show_img = cv2.cvtColor(cartoon_image, cv2.COLOR_BGR2RGB)
    else:
        show_img = cartoon_image

    st.image(show_img, width="stretch")
    # 生成带参数的文件名
    # 例如：cartoon_铅笔素描_value250.0_kernel25.png
    param_str = "_".join([f"{k}{params[k]:g}" if isinstance(params[k], float) else f"{k}{params[k]}"
                          for k in params])
    base = f"cartoon_{option}"
    if param_str:
        base += f"_{param_str}"
    file_name = safe_name(base) + ".png"

    # 输出为 PNG 字节流
    buf = io.BytesIO()
    if cartoon_image.ndim == 3:
        out_img = Image.fromarray(cv2.cvtColor(cartoon_image, cv2.COLOR_BGR2RGB))
    else:
        out_img = Image.fromarray(cartoon_image)

    buf.seek(0)

    st.download_button(
        label=f"下载效果图（{file_name}）",
        data=buf,
        file_name=file_name,
        mime="image/png"
    )
