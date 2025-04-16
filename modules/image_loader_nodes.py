import base64
from io import BytesIO

import numpy as np
import requests
import torch
from PIL import Image, ImageFilter


# ===== 基础类 =====
class BaseImageLoader:
    """图像加载器基类，包含公共工具方法"""

    def _extract_components(self, img, use_alpha=True):
        """提取图像和掩码的公共方法"""
        if use_alpha and img.mode == 'RGBA':
            mask = img.split()[-1]
            return img.convert("RGB"), mask
        return img.convert("RGB"), Image.new("L", img.size, 255)

    def _pil_to_tensor(self, image):
        """PIL图像转Tensor（0~1）"""
        return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

    def _create_empty_image(self, size=(512, 512)):
        """生成空图像/掩码"""
        empty_img = np.zeros((*size, 3), dtype=np.float32)
        return torch.from_numpy(empty_img).unsqueeze(0)


# ===== URL 批量加载节点 =====
class LoadImageFromURL(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "urls": ("STRING", {
                    "multiline": True,
                    "default": "https://example.com/image.png"
                }),
                "timeout": ("INT", {"default": 10, "min": 1, "max": 60})
            }
        }

    CATEGORY = "X-Design/Image"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("images", "masks")
    FUNCTION = "load_urls"
    OUTPUT_IS_LIST = (True, True)

    def load_urls(self, urls: str, timeout: int):
        images, masks = [], []
        url_list = [url.strip() for url in urls.split('\n') if url.startswith(('http://', 'https://'))]

        for url in url_list:
            try:
                with requests.get(url, timeout=timeout, stream=True) as response:
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content))
                    image, mask = self._extract_components(img)
                    images.append(self._pil_to_tensor(image))
                    masks.append(self._pil_to_tensor(mask))
            except Exception as e:
                print(f"❌ Failed to load {url}: {e}")
                empty_img = self._create_empty_image()
                images.append(empty_img)
                masks.append(empty_img[:, :, :, 0:1])

        return images, masks


# ===== Base64 批量加载节点 =====
class LoadImageFromBase64(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_data": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "has_alpha": ([True, False], {"default": True})
            }
        }

    CATEGORY = "X-Design/Image"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("images", "masks")
    FUNCTION = "load_base64"
    OUTPUT_IS_LIST = (True, True)

    def load_base64(self, base64_data: str, has_alpha: bool):
        images, masks = [], []
        data_list = [d.strip() for d in base64_data.split('\n') if d.strip()]

        for data in data_list:
            try:
                if data.startswith("data:image"):
                    _, data = data.split(",", 1)
                image_data = base64.b64decode(data)
                img = Image.open(BytesIO(image_data))
                image, mask = self._extract_components(img, has_alpha)
                images.append(self._pil_to_tensor(image))
                masks.append(self._pil_to_tensor(mask))
            except Exception as e:
                print(f"❌ Failed to decode base64: {e}")
                empty_img = self._create_empty_image()
                images.append(empty_img)
                masks.append(empty_img[:, :, :, 0:1])

        return images, masks


# ===== 单个 URL 加载节点 =====
class LoadSingleImageFromURL(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {
                    "multiline": False,
                    "default": "https://example.com/single-image.png"
                }),
                "timeout": ("INT", {"default": 10, "min": 1, "max": 60})
            }
        }

    CATEGORY = "X-Design/Image"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_single_url"
    OUTPUT_IS_LIST = (False, False)

    def load_single_url(self, url: str, timeout: int):
        try:
            with requests.get(url.strip(), timeout=timeout, stream=True) as response:
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                image, mask = self._extract_components(img)
                return self._pil_to_tensor(image), self._pil_to_tensor(mask)
        except Exception as e:
            print(f"❌ Failed to load {url}: {e}")
            empty_img = self._create_empty_image()
            return empty_img, empty_img[:, :, :, 0:1]


# ===== 单个 Base64 加载节点 =====
class LoadSingleImageFromBase64(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_str": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "has_alpha": ([True, False], {"default": True})
            }
        }

    CATEGORY = "X-Design/Image"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_single_base64"
    OUTPUT_IS_LIST = (False, False)

    def load_single_base64(self, base64_str: str, has_alpha: bool):
        try:
            clean_data = base64_str.strip()
            if clean_data.startswith("data:image"):
                _, data = clean_data.split(",", 1)
            else:
                data = clean_data

            image_data = base64.b64decode(data)
            img = Image.open(BytesIO(image_data))
            image, mask = self._extract_components(img, has_alpha)
            return self._pil_to_tensor(image), self._pil_to_tensor(mask)
        except Exception as e:
            print(f"❌ Failed to decode base64: {e}")
            empty_img = self._create_empty_image()
            return empty_img, empty_img[:, :, :, 0:1]


class LoadMaskFromURL(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "https://example.com/image.png"}),
                "timeout": ("INT", {"default": 10, "min": 1, "max": 60}),
                "channel": (["alpha", "red", "green", "blue"], {"default": "alpha"})
            }
        }

    CATEGORY = "X-Design/Mask"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "load_mask"
    OUTPUT_IS_LIST = (False,)

    def load_mask(self, url, timeout, channel):
        try:
            response = requests.get(url.strip(), timeout=timeout)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGBA")

            channels = img.split()
            if channel == "alpha":
                mask = channels[3]
            elif channel == "red":
                mask = channels[0]
            elif channel == "green":
                mask = channels[1]
            elif channel == "blue":
                mask = channels[2]

            return (self._pil_to_tensor(mask),)
        except Exception as e:
            print(f"❌ URL遮罩加载失败: {str(e)}")
            empty_mask = self._create_empty_image(size=(512, 512))[:, :, :, 0:1]
            return (empty_mask,)


class LoadMaskFromBase64(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_str": ("STRING", {"multiline": True}),
                "channel": (["alpha", "red", "green", "blue"], {"default": "alpha"})
            }
        }

    CATEGORY = "X-Design/Mask"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "load_mask"
    OUTPUT_IS_LIST = (False,)

    def load_mask(self, base64_str, channel):
        try:
            clean_data = base64_str.strip()
            if clean_data.startswith("data:image"):
                header, data = clean_data.split(",", 1)
            else:
                data = clean_data

            image_data = base64.b64decode(data)
            img = Image.open(BytesIO(image_data)).convert("RGBA")

            channels = img.split()
            if channel == "alpha":
                mask = channels[3]
            elif channel == "red":
                mask = channels[0]
            elif channel == "green":
                mask = channels[1]
            elif channel == "blue":
                mask = channels[2]

            return (self._pil_to_tensor(mask),)
        except Exception as e:
            print(f"❌ Base64遮罩解码失败: {str(e)}")
            empty_mask = self._create_empty_image(size=(512, 512))[:, :, :, 0:1]
            return (empty_mask,)


class LoadImageFromLocalFile(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {
                    "multiline": False,
                    "default": "/path/to/image.png"
                }),
                "has_alpha": ([True, False], {"default": True})
            }
        }

    CATEGORY = "X-Design/Image"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "load_local_file"
    OUTPUT_IS_LIST = (False, False)

    def load_local_file(self, file_path: str, has_alpha: bool):
        try:
            img = Image.open(file_path)
            image, mask = self._extract_components(img, has_alpha)
            return (
                self._pil_to_tensor(image),
                self._pil_to_tensor(mask)
            )
        except Exception as e:
            print(f"❌ 本地图像加载失败: {str(e)}")
            empty_img = self._create_empty_image()
            return (empty_img, empty_img[:, :, :, 0:1])


class ImagePreprocess(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "resize_width": ("INT", {"default": 512, "min": 1}),
                "resize_height": ("INT", {"default": 512, "min": 1}),
                "crop_left": ("INT", {"default": 0}),
                "crop_top": ("INT", {"default": 0}),
                "crop_right": ("INT", {"default": 0}),
                "crop_bottom": ("INT", {"default": 0}),
                "blur_radius": ("FLOAT", {"default": 0.0, "min": 0.0}),
            }
        }

    CATEGORY = "X-Design/Image"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("processed_image",)
    FUNCTION = "preprocess"
    OUTPUT_IS_LIST = (False,)

    def preprocess(self, image, resize_width, resize_height, crop_left, crop_top, crop_right, crop_bottom, blur_radius):
        pil_image = Image.fromarray((image.squeeze(0).numpy() * 255).astype(np.uint8))

        # 裁剪
        w, h = pil_image.size
        pil_image = pil_image.crop((
            crop_left,
            crop_top,
            w - crop_right,
            h - crop_bottom
        ))

        # 缩放
        pil_image = pil_image.resize((resize_width, resize_height))

        # 模糊
        if blur_radius > 0:
            pil_image = pil_image.filter(ImageFilter.GaussianBlur(blur_radius))

        return (self._pil_to_tensor(pil_image),)


class ImageToBase64(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "format": (["PNG", "JPEG"], {"default": "PNG"})
            }
        }

    CATEGORY = "X-Design/Image"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64_str",)
    FUNCTION = "image_to_base64"
    OUTPUT_IS_LIST = (False,)

    def image_to_base64(self, image, format):
        pil_image = Image.fromarray((image.squeeze(0).numpy() * 255).astype(np.uint8))
        buffered = BytesIO()
        pil_image.save(buffered, format=format)
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return (img_base64,)


class Base64ToImage(BaseImageLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_str": ("STRING", {"multiline": True}),
                "has_alpha": ([True, False], {"default": True})
            }
        }

    CATEGORY = "X-Design/Image"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "base64_to_image"
    OUTPUT_IS_LIST = (False,)

    def base64_to_image(self, base64_str, has_alpha):
        try:
            clean_data = base64_str.strip()
            if clean_data.startswith("data:image"):
                header, data = clean_data.split(",", 1)
            else:
                data = clean_data

            image_data = base64.b64decode(data)
            img = Image.open(BytesIO(image_data))
            image, _ = self._extract_components(img, has_alpha)
            return (self._pil_to_tensor(image),)
        except Exception as e:
            print(f"❌ Base64解码失败: {str(e)}")
            empty_img = self._create_empty_image()
            return (empty_img,)


# ===== 节点注册映射 =====
NODE_CLASS_MAPPINGS = {
    "LoadImageFromURL": LoadSingleImageFromURL,
    "LoadImageFromBase64": LoadSingleImageFromBase64,
    "LoadImageFromURLBatch": LoadImageFromURL,
    "LoadImageFromBase64Batch": LoadImageFromBase64,
    "LoadMaskFromURL": LoadMaskFromURL,
    "LoadMaskFromBase64": LoadMaskFromBase64,
    "LoadImageFromLocalFile": LoadImageFromLocalFile,
    "ImagePreprocess": ImagePreprocess,
    "ImageToBase64": ImageToBase64,
    "Base64ToImage": Base64ToImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageFromURL": "🌐 URL Image Loader",
    "LoadImageFromBase64": "🔢 Base64 Image Loader",
    "LoadImageFromURLBatch": "🌐 URL Image Loader (Batch)",
    "LoadImageFromBase64Batch": "🔢 Base64 Image Loader (Batch)",
    "LoadMaskFromURL": "🌐 Mask Loader from URL",
    "LoadMaskFromBase64": "🔢 Mask Loader from Base64",
    "LoadImageFromLocalFile": "📂 Local Image Loader",
    "ImagePreprocess": "🎛️ Image Preprocess",
    "ImageToBase64": "🔀 Image → Base64",
    "Base64ToImage": "🔀 Base64 → Image",
}