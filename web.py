import cv2
import streamlit as st
import numpy as np
from PIL import Image
import io

# 自动推荐参数函数
def recommend_params(option, img):
    params = {}

    # 计算图像的一些特征
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)  # 计算图像的平均亮度
    contrast = np.std(gray)  # 图像的对比度（标准差）

    # 边缘信息 - 使用 Canny 边缘检测
    edges = cv2.Canny(gray, 100, 200)  # 提取图像的边缘
    edge_density = np.sum(edges) / edges.size  # 边缘密度，越高表示图像细节越多

    # 根据图像的特征动态调整推荐的参数

    def calculate_value(mean_brightness):   
        """根据亮度计算 value 参数"""
        # 平均亮度较低时，增加 value 来提亮素描效果
        if mean_brightness < 128:
            return 250.0 + (128 - mean_brightness)  # 提高亮度
        else:
            return 200.0 - (mean_brightness - 128)  # 降低亮度

    def calculate_kernel(contrast, edge_density):
        """根据对比度和边缘密度计算 kernel 参数"""
        # 较高的对比度和边缘密度可以增强细节，因此使用更大的 kernel
        if contrast > 50 and edge_density > 0.05:
            return 35  # 较大 kernel，保留更多细节
        else:
            return 25  # 较小 kernel，进行平滑处理

    # 根据图像的特征动态计算参数
    value = calculate_value(mean_brightness)
    kernel = calculate_kernel(contrast, edge_density)

    # 动态设置参数
    params["value"] = value
    params["kernel"] = kernel

    # 根据选择的风格进一步调整参数
    if option == "漫画渲染":
        smooth = 5 if contrast < 50 else 10
        edge_preserve = 0.5 if edge_density < 0.05 else 0.8
        params["smooth"] = smooth
        params["edge"] = edge_preserve

    elif option == "黑白线稿":
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_variance = np.var(laplacian)  # Laplacian 方差，越大表示边缘越强
        noise_reduction = 150 if laplacian_variance < 500 else 100
        params["lap"] = 3 if laplacian_variance < 500 else 5
        params["thr"] = noise_reduction

    elif option == "卡通插画":
        edge_preserve = 50 if edge_density < 0.05 else 70
        params["edge"] = edge_preserve

    return params

# 图像处理函数
def apply_filter(img, filter_option, params):
    # 确保 kernel 是正奇数
    kernel = params.get("kernel", 25)  # 默认值 25
    if kernel % 2 == 0:  # 如果是偶数，增加 1
        kernel += 1

    if filter_option == "真实素描":
        value = params["value"]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (kernel, kernel), 0)  # 使用正奇数 kernel
        return cv2.divide(gray, gray_blur, scale=value)

    elif filter_option == "漫画渲染":
        smooth = params["smooth"]
        edge_preserve = params["edge"]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.detailEnhance(img, sigma_s=smooth, sigma_r=edge_preserve)
        return cv2.bitwise_and(color, color, mask=edges)

    elif filter_option == "黑白线稿":
        laplacian_filter = params["lap"]
        noise_reduction = params["thr"]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.medianBlur(gray, kernel)
        edges = cv2.Laplacian(gray2, -1, ksize=laplacian_filter)
        edges_inv = 255 - edges
        _, cartoon_image = cv2.threshold(edges_inv, noise_reduction, 255, cv2.THRESH_BINARY)
        return cartoon_image

    elif filter_option == "卡通插画":
        smooth = params["smooth"]
        edge_preserve = params["edge"]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, smooth, edge_preserve, smooth)
        return cv2.bitwise_and(color, color, mask=edges)

    return img


# 安全的文件名生成函数
def safe_name(s: str) -> str:
    """文件名安全：去掉不适合做文件名的字符"""
    keep = []
    for ch in s:
        if ch.isalnum() or ch in ['_', '-', '.']:
            keep.append(ch)
        else:
            keep.append('_')
    return ''.join(keep)

# Streamlit UI
st.write("# 图像处理：转换您的图片为卡通效果！")
st.write("这是一个将您的照片转化为各种效果的应用，支持自动推荐参数！")

file = st.sidebar.file_uploader("请上传一张图片文件", type=["jpg", "png"])

if file is None:
    st.text("您尚未上传图片文件")
else:
    image = Image.open(file).convert("RGB")  # 强制变成 RGB 三通道
    img_rgb = np.array(image)               # RGB
    img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)  # 转成 OpenCV 习惯的 BGR

    # 风格选择
    option = st.sidebar.selectbox(
        '您想应用哪种图像处理效果？',
        ('真实素描', '漫画渲染', '黑白线稿', '卡通插画')
    )

    # 自动推荐参数
    params = recommend_params(option, img)

    # 在左侧边栏显示推荐的参数，并允许用户调整
    st.sidebar.write(f"推荐的参数：")
    for key, value in params.items():
        # 确保 `min_value`, `max_value`, `value` 和 `step` 的类型一致
        if isinstance(value, float):
            step_value = 0.1
            value = float(value)
            params[key] = st.sidebar.slider(f"{key} 推荐值", min_value=value - 50.0, max_value=value + 50.0, value=value, step=step_value)
        else:
            step_value = 1
            value = int(value)
            params[key] = st.sidebar.slider(f"{key} 推荐值", min_value=value - 50, max_value=value + 50, value=value, step=step_value)

    # 显示已选择的风格和推荐参数
    st.write(f"您选择的风格：{option}")
    st.write("推荐参数：", params)

    # 显示原图
    st.text("您的原始图片")
    st.image(image, width="stretch")

    # “开始生成”按钮
    run = st.sidebar.button('开始生成')

    if run:
        with st.spinner("生成中，请稍等..."):
            processed_image = apply_filter(img, option, params)
            st.text("您的处理后图片")
            if processed_image.ndim == 3:
                show_img = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
            else:
                show_img = processed_image

            st.image(show_img, width="stretch")
            # 生成带参数的文件名
            param_str = "_".join([f"{k}{params[k]:g}" if isinstance(params[k], float) else f"{k}{params[k]}"
                                  for k in params])
            base = f"image_{option}"
            if param_str:
                base += f"_{param_str}"
            file_name = safe_name(base) + ".png"

            # 输出为 PNG 字节流
            buf = io.BytesIO()
            if processed_image.ndim == 3:
                out_img = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
            else:
                out_img = Image.fromarray(processed_image)
            out_img.save(buf, format="PNG")
            buf.seek(0)

            st.download_button(
                label=f"下载效果图（{file_name}）",
                data=buf.getvalue(),
                file_name=file_name,
                mime="image/png"
            )
    else:   
        st.info("请在左侧调好参数后点击【开始生成】")
