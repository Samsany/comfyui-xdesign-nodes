# 🖼️ comfyui-xdesign-nodes

自定义 **ComfyUI 插件**，扩展图像加载与遮罩加载节点，支持 **URL**、**Base64** 图像及遮罩的读取和转换，便于在 AI 图像工作流中灵活使用。

---

## ✨ 功能特性

- 🌐 从 URL 加载图像（单张 / 批量）
- 🔢 从 Base64 加载图像（单张 / 批量）
- 🎛️ 提取图像 Alpha、Red、Green、Blue 通道生成遮罩
- 📝 支持透明通道 (Alpha) 和 RGB 通道提取
- 📏 图像与掩码返回统一形状，自动对齐
- ✅ 异常情况返回空白图像，确保流程不中断

---

## 📦 安装方式

```bash
# 克隆项目
git clone https://github.com/yourname/comfyui-xdesign-nodes.git

# 进入插件目录
cd comfyui-xdesign-nodes

# 放置到 ComfyUI 的 custom_nodes 目录下
cp -r comfyui-xdesign-nodes /path/to/comfyui/custom_nodes/

# 查看 README 和节点说明
cat README.md
```

---

## 🚀 节点说明  

### 📂 图像加载节点

| 节点名称                    | 功能                         | 返回类型         |
|:---------------------------|:-----------------------------|:----------------|
| 🌐 LoadImageFromURL          | 加载单个 URL 图片              | IMAGE, MASK      |
| 🔢 LoadImageFromBase64       | 加载单个 Base64 图片           | IMAGE, MASK      |
| 🌐 LoadImageFromURLBatch     | 批量加载 URL 图片              | IMAGE[], MASK[]  |
| 🔢 LoadImageFromBase64Batch  | 批量加载 Base64 图片           | IMAGE[], MASK[]  |

- **IMAGE**：`(1, H, W, 3)` 格式，RGB 图像，数值范围 0~1  
- **MASK**：`(1, H, W, 1)` 格式，灰度图像，数值范围 0~1  

### 🎨 遮罩加载节点

| 节点名称                  | 功能                         | 返回类型 |
|:-------------------------|:-----------------------------|:---------|
| 🌐 LoadMaskFromURL         | 从 URL 加载图片，提取指定通道  | MASK     |
| 🔢 LoadMaskFromBase64      | 从 Base64 加载图片，提取通道   | MASK     |

**支持通道：**
- `alpha` → Alpha 通道  
- `red` → 红色通道  
- `green` → 绿色通道  
- `blue` → 蓝色通道  

**返回：**  
- **MASK**：`(1, H, W, 1)` 格式，单通道掩码，0~1 范围  

---

## 📊 返回数据格式  

| 类型   | 维度                | 描述              |
|:--------|:--------------------|:-----------------|
| IMAGE   | `(1, H, W, 3)`        | RGB 彩色图像       |
| MASK    | `(1, H, W, 1)`        | 单通道灰度遮罩     |

---

## 📌 项目结构  

```
comfyui-xdesign-nodes/
├── __init__.py
├── loaders.py                # 图像/遮罩 加载节点实现
├── README.md
└── ...（更多扩展）
```

---

## 🎯 TODO  

- 📂 LoadImageFromLocalFile 本地图片加载节点  
- 🎛️ ImagePreprocess 节点（resize、crop、blur 支持）  
- 🔀 ImageToBase64 / Base64ToImage 转换节点  
- 🖼️ LoadMaskFromLocalFile 节点  

---

## 📬 联系方式  

如果你有建议、问题或合作意向，欢迎联系我：

- 📧 Email: yourname@example.com  
- 🌐 GitHub: [yourname](https://github.com/yourname)  

---

## 📜 License  

本项目基于 MIT 开源协议发布，详见 [LICENSE](./LICENSE)。