---

# ImageWeb（基于 OpenCV 的图像素描化与卡通化 Web 工具）

一个基于 **OpenCV + Streamlit** 的轻量级图像风格化 Web 应用：支持上传图片并一键生成 **真实素描 / 黑白线稿 / 漫画渲染 / 卡通插画** 等效果，支持**自动推荐参数**、手动滑动调参、实时预览与下载结果图。

---

## 功能特性

* 支持 4 种风格化效果

  * 真实素描（灰度 + 高斯模糊 + 图像相除）
  * 黑白线稿（Laplacian 边缘 + 阈值化）
  * 漫画渲染（自适应阈值边缘 + 细节增强）
  * 卡通插画（自适应阈值边缘 + 双边滤波）
* 自动推荐参数：基于图像 **亮度、对比度、边缘密度** 动态给出推荐值
* 参数可视化调节：侧边栏 slider 调参
* 一键下载：自动生成带参数的文件名，支持下载 PNG

---

## 环境要求

* Python：**3.10**
* 依赖库：见 `requirements.txt`

---

## 本地运行

1. 克隆项目（仓库地址如下）

```text
https://github.com/Quirrelz/ImageWeb
```

2. 进入项目目录，创建并激活虚拟环境（示例：Windows / macOS / Linux 自行选择）

```bash
# 进入项目文件夹
cd ImageWeb

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.\.venv\Scripts\activate

# 激活虚拟环境（macOS/Linux）
# source .venv/bin/activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 启动 Streamlit（在项目文件夹中执行）

```bash
streamlit run web.py
```

启动后终端会输出本地访问地址，并自动在浏览器中打开 Web 页面。

---

## 公网部署（Streamlit Community Cloud）

你可以通过 Streamlit 官方的 Community Cloud 一键部署为公网可访问的 Web：

1. 打开 Streamlit 官网，用 GitHub 账号登录
2. 选择 **New app / Create app**
3. 选择你的 GitHub 仓库与分支（例如 `main`）
4. 入口文件选择：`web.py`
5. 点击 Deploy，等待构建完成后即可获得公网访问链接

> 仓库地址（供复制粘贴）：

```text
https://github.com/Quirrelz/ImageWeb
```
## ✅ 效果展示（Demo Gallery）


| 原图 | 真实素描 | 黑白线稿 | 漫画渲染 | 卡通插画 |
|:---:|:---:|:---:|:---:|:---:|
| <img src="assets/demo/origin.png" height="180"/> | <img src="assets/demo/sketch.jpg" height="180"/> | <img src="assets/demo/lineart.png" height="180"/> | <img src="assets/demo/comic.png" height="180"/> | <img src="assets/demo/cartoon.png" height="180"/> |


---


