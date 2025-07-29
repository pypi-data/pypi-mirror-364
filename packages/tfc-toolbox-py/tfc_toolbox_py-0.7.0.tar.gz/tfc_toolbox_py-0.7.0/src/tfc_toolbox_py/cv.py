import cv2
import numpy as np


class ImageStitcher:
    """
    This is a class that can stitch two picture.

    It is a simple example:
    ```python
    stitcher = ImageStitcher('image1.jpg', 'image2.jpg')

    # horizontal stitch
    horizontal = stitcher.stitch_horizontal(padding=10)
    stitcher.show_image(horizontal, 'Horizontal Stitch')
    stitcher.save_image(horizontal, 'horizontal_stitch.jpg')
    ```
    """

    def __init__(self, image1_path=None, image2_path=None):
        """
        初始化ImageStitcher类

        参数:
            image1_path: 第一张图片路径
            image2_path: 第二张图片路径
        """
        self.image1 = self._load_image(image1_path) if image1_path else None
        self.image2 = self._load_image(image2_path) if image2_path else None

    @staticmethod
    def _load_image(image_path):
        """加载图片并检查是否成功"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法加载图片: {image_path}")
        return img

    def set_images(self, image1_path, image2_path):
        """设置要拼接的两张图片"""
        self.image1 = self._load_image(image1_path)
        self.image2 = self._load_image(image2_path)

    @staticmethod
    def _ensure_same_channels(img1, img2):
        """确保两张图片通道数相同"""
        if len(img1.shape) == 3 and len(img2.shape) == 2:
            img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
        elif len(img1.shape) == 2 and len(img2.shape) == 3:
            img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
        return img1, img2

    @staticmethod
    def _resize_to_same_height(img1, img2):
        """调整图片到相同高度"""
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        new_height = min(h1, h2)
        img1 = cv2.resize(img1, (int(w1 * new_height / h1), new_height))
        img2 = cv2.resize(img2, (int(w2 * new_height / h2), new_height))
        return img1, img2

    @staticmethod
    def _resize_to_same_width(img1, img2):
        """调整图片到相同宽度"""
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        new_width = min(w1, w2)
        img1 = cv2.resize(img1, (new_width, int(h1 * new_width / w1)))
        img2 = cv2.resize(img2, (new_width, int(h2 * new_width / w2)))
        return img1, img2

    def stitch_horizontal(self, padding=0, padding_color=(0, 0, 0)):
        """
        左右拼接图片

        参数:
            padding: 图片间间距(像素)
            padding_color: 间距颜色(BGR格式)

        返回:
            拼接后的图片
        """
        if self.image1 is None or self.image2 is None:
            raise ValueError("请先设置两张图片")

        img1, img2 = self._ensure_same_channels(self.image1, self.image2)
        img1, img2 = self._resize_to_same_height(img1, img2)

        if padding > 0:
            padding_img = np.zeros((img1.shape[0], padding, 3), dtype=np.uint8)
            padding_img[:] = padding_color
            stitched = np.hstack((img1, padding_img, img2))
        else:
            stitched = np.hstack((img1, img2))

        return stitched

    def stitch_vertical(self, padding=0, padding_color=(0, 0, 0)):
        """
        上下拼接图片

        参数:
            padding: 图片间间距(像素)
            padding_color: 间距颜色(BGR格式)

        返回:
            拼接后的图片
        """
        if self.image1 is None or self.image2 is None:
            raise ValueError("请先设置两张图片")

        img1, img2 = self._ensure_same_channels(self.image1, self.image2)
        img1, img2 = self._resize_to_same_width(img1, img2)

        if padding > 0:
            padding_img = np.zeros((padding, img1.shape[1], 3), dtype=np.uint8)
            padding_img[:] = padding_color
            stitched = np.vstack((img1, padding_img, img2))
        else:
            stitched = np.vstack((img1, img2))

        return stitched

    @staticmethod
    def show_image(image, window_name='Image'):
        """显示图片"""
        cv2.imshow(window_name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def save_image(image, output_path):
        """保存图片"""
        cv2.imwrite(output_path, image)
