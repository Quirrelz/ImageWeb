import cv2
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
from PIL import Image, ImageTk
import numpy as np

# 卡通化处理函数
def cartoonization(img, filter_option):
    if len(img.shape) == 3 and img.shape[2] == 3:  # 彩色图（3通道）
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif len(img.shape) == 2:  # 已经是灰度图（1通道）
        gray = img
    else:  # 其他情况，可能是 RGBA 图像，转换为 RGB
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 根据用户选择的卡通效果进行处理
    if filter_option == "铅笔素描":
        value = 250.0  # 亮度
        kernel = 25  # 边缘粗细

        gray_blur = cv2.GaussianBlur(gray, (kernel, kernel), 0)
        cartoon_image = cv2.divide(gray, gray_blur, scale=value)

    elif filter_option == "细节增强":
        smooth = 5  # 平滑度
        kernel = 3  # 锐度
        edge_preserve = 0.5  # 平滑不相似颜色

        gray = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

        color = cv2.detailEnhance(img, sigma_s=smooth, sigma_r=edge_preserve)
        cartoon_image = cv2.bitwise_and(color, color, mask=edges)

    elif filter_option == "铅笔边缘":
        kernel = 25  # 锐度
        laplacian_filter = 3  # 边缘检测强度
        noise_reduction = 150  # 噪声效果

        gray = cv2.medianBlur(gray, kernel)
        edges = cv2.Laplacian(gray, -1, ksize=laplacian_filter)
        edges_inv = 255 - edges

        dummy, cartoon_image = cv2.threshold(edges_inv, noise_reduction, 255, cv2.THRESH_BINARY)

    elif filter_option == "双边滤波":
        smooth = 5  # 平滑度
        kernel = 3  # 锐度
        edge_preserve = 50  # 颜色平滑效果

        gray = cv2.medianBlur(gray, kernel)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

        color = cv2.bilateralFilter(img, smooth, edge_preserve, smooth)
        cartoon_image = cv2.bitwise_and(color, color, mask=edges)

    return cartoon_image

# 打开文件对话框选择图片
def open_image():
    file_path = filedialog.askopenfilename(
        title="选择图片",
        filetypes=(("所有图片文件", "*.jpg;*.jpeg;*.png;*.bmp;*.gif"), ("JPEG文件", "*.jpg;*.jpeg"), ("PNG文件", "*.png"), ("BMP文件", "*.bmp"), ("GIF文件", "*.gif"))
    )
    if file_path:
        try:
            img = Image.open(file_path)
            img = np.array(img)
            return img, file_path
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片: {e}")
            return None, None
    return None, None

# 保存图像到指定位置
def save_image(image):
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg"), ("BMP文件", "*.bmp")],
        title="保存图片"
    )
    if save_path:
        try:
            result_image = Image.fromarray(image)
            result_image.save(save_path)
            messagebox.showinfo("成功", "图片保存成功！")
        except Exception as e:
            messagebox.showerror("错误", f"保存图片时出错: {e}")

# 显示图片
def show_image(image, label):
    image = Image.fromarray(image)
    image.thumbnail((400, 400))  # 调整图片尺寸以适应窗口
    image_tk = ImageTk.PhotoImage(image)
    label.config(image=image_tk)
    label.image = image_tk

# 主程序
def main():
    root = tk.Tk()
    root.title("卡通化图片处理程序")

    # 标签显示原始图片和卡通化后的图片
    original_label = tk.Label(root)
    original_label.pack()

    cartoon_label = tk.Label(root)
    cartoon_label.pack()

    # 按钮用于上传图片
    def on_upload_button_click():
        img, file_path = open_image()
        if img is not None:
            show_image(img, original_label)

            # 选择卡通滤镜
            filter_option = filter_var.get()

            # 生成卡通化效果图
            cartoon_img = cartoonization(img, filter_option)
            show_image(cartoon_img, cartoon_label)

    upload_button = tk.Button(root, text="上传图片", command=on_upload_button_click)
    upload_button.pack()

    # 滤镜选择
    filter_var = tk.StringVar()
    filter_var.set("铅笔素描")  # 默认滤镜为铅笔素描

    filter_options = ["铅笔素描", "细节增强", "铅笔边缘", "双边滤波"]
    filter_menu = tk.OptionMenu(root, filter_var, *filter_options)
    filter_menu.pack()

    # 按钮用于保存图片
    save_button = tk.Button(root, text="保存图片", command=lambda: save_image(cartoon_label.image))
    save_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
