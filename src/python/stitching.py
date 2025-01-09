# 图像拼合算法
import cv2
import numpy as np
import base64
from functools import reduce
import json

class StitchingError(Exception):
    """图片拼接过程中的异常"""
    pass

def resize(image, scale_factor):
    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    dim = (width, height)
    resized_image = cv2.resize(image, dim)
    return resized_image

def create_mask(image, isFirst):
    img_width = image.shape[1]
    img_height = image.shape[0]
    rec_height = 300
    x = 0
    y = img_height - rec_height if isFirst is True else 0

    mask = np.zeros_like(image)
    cv2.rectangle(mask, (x, y), (x+img_width, y+rec_height), (255, 255, 255), -1)
    return mask

# 检测平移矩阵的旋转分量是否存在
def is_pure_translation(H, rotation_threshold=0.05):
    rotation_part = H[:2, :2]
    identity = np.eye(2)
    rotation_diff = np.abs(rotation_part - identity)
    
    return np.all(rotation_diff < rotation_threshold)

def stitching(image1, image2):
    # 转换为灰度图像
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    # print(gray1, gray2)

    # 生成特征检测 mask
    gray1_mask = create_mask(gray1, True)
    gray2_mask = create_mask(gray2, False)
    # print(gray1_mask, gray2_mask)

    # 使用 SIFT 检测关键点和描述符
    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(gray1, gray1_mask)
    keypoints2, descriptors2 = sift.detectAndCompute(gray2, gray2_mask)
    # print(keypoints1)
    # print(descriptors1)

    # 使用 BFMatcher 进行特征匹配
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    # print(matches)

    # 按距离排序匹配
    matches = sorted(matches, key=lambda x: x.distance)
    # print(matches)

    # 提取匹配的关键点
    points1 = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    points2 = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    # print(points1, points2)

    # 估计平移矩阵
    H, mask = cv2.estimateAffinePartial2D(points2, points1)
    # print(H, mask)

    # 如果不是垂直or水平方向的平移，则退出
    if not is_pure_translation(H):
        # 抛出异常
        raise StitchingError("拼合过程出现角度偏移，请检查图片是否可以进行合并")

    # 应用平移变换
    height, width = image1.shape[:2]
    result = cv2.warpAffine(image2, H, (width, height + image2.shape[0]))
    result[0:height, 0:width] = image1

    for i in range(result.shape[0]):
        if np.sum(result[result.shape[0]-i-1, :]) != 0:
            result = result[:-i-1, :]
            break

    return result

images = []
# 解析 JavaScript 传入的数组
pics = json.loads(pics_data)
for i in range(len(pics)):
    decodedImg = np.frombuffer(base64.b64decode(pics[i]), np.uint8)
    # 使用cv2解码图片
    image = cv2.imdecode(decodedImg, cv2.IMREAD_COLOR)
    # resize
    image = resize(image, 0.5)
    images.append(image)
result = reduce(stitching, images)

# 将 numpy array 转换为 bytes
_, buffer = cv2.imencode('.png', result)

# 将 bytes 转换为 base64 字符串
img_base64 = base64.b64encode(buffer).decode('utf-8')
img_base64