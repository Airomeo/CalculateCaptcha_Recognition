# recognize.py

import onnxruntime
from PIL import Image
import numpy as np
import base64
import io

# --- 常量定义 (已修正) ---
# 定义验证码的字符集。请根据您模型训练时使用的字符集进行修改。
# 根据模型输出大小80推断，词汇表长度应为16 (可能是15个字符 + 1个CTC blank字符)
# 并且验证码长度为 5 (80 / 16 = 5)。
# 我们在末尾添加一个'#'作为空白字符的占位符。
captcha_array = list('0123456789+-*/=?') # <--- 主要修改点 1：增加了一个字符，使总长度为16
CAPTCHA_VOCAB_LEN = len(captcha_array)   # <--- 主要修改点 2：现在这个值是 16

# ONNX 模型文件路径
ONNX_FILE = 'mathcode.onnx'
# 图像尺寸 (宽度, 高度)
IMG_SIZE = (160, 60)


def load_model(model_path: str = ONNX_FILE) -> onnxruntime.InferenceSession:
    """
    加载 ONNX 模型并返回一个推理会话。
    这个函数应该在服务启动时被调用一次。

    输入:
        model_path (str): ONNX 模型文件的路径。
    
    输出:
        onnxruntime.InferenceSession: ONNX 推理会话对象。
    """
    try:
        print(f"正在从 {model_path} 加载模型...")
        session = onnxruntime.InferenceSession(model_path)
        print("模型加载成功！")
        return session
    except FileNotFoundError:
        print(f"错误: 找不到模型文件 {model_path}")
        raise
    except Exception as e:
        print(f"加载模型时发生未知错误: {e}")
        raise


def preprocess_image(b64_str: str) -> np.ndarray:
    """
    加载 Base64 编码的图像，解码，调整大小，转换为 RGB，归一化并改变维度顺序。
    
    输入:
        b64_str (str): Base64 编码的图像字符串。
    
    输出:
        np.ndarray: 预处理后的图像张量 (Batch, Channel, Height, Width)。
    """
    try:
        img_bytes = base64.b64decode(b64_str)
        img_io = io.BytesIO(img_bytes)
        img = Image.open(img_io).resize(IMG_SIZE).convert('RGB')
    except Exception as e:
        print(f"图像处理失败: {e}")
        raise

    img_np = np.asarray(img, dtype=np.float32) / 255.0
    img_np = img_np.transpose(2, 0, 1)
    return img_np[np.newaxis, :]


def decode_output(output: np.ndarray) -> str:
    """
    解码 ONNX 模型输出的预测结果为验证码文本。
    
    输入:
        output (np.ndarray): 模型的原始输出。
    
    输出:
        str: 识别出的验证码字符串。
    """
    # 打印模型原始输出的形状，有助于调试
    # print(f"模型原始输出形状: {output.shape}") # -> 应该会打印 (1, 80) 或类似的

    # 将输出重塑为 (字符数, 词汇表大小)
    # 这里的 -1 会被自动计算为 5 (因为 80 / 16 = 5)
    output_reshaped = output.reshape(-1, CAPTCHA_VOCAB_LEN)

    # 对每个字符的概率进行 argmax，得到预测的字符索引
    pred_indices = np.argmax(output_reshaped, axis=1)

    # 将索引映射回字符，并拼接成字符串
    recognized_text = ''.join(captcha_array[i] for i in pred_indices)
    
    # 通常CTC blank字符'#'不会被输出，但以防万一可以将其移除
    return recognized_text.replace('#', '')


def run_recognition(session: onnxruntime.InferenceSession, b64_str: str) -> str:
    """
    使用已加载的模型会话执行完整的验证码识别流程。
    
    输入:
        session (onnxruntime.InferenceSession): 预先加载好的 ONNX 推理会话。
        b64_str (str): Base64 编码的图像字符串。
        
    输出:
        str: 识别出的验证码文本。
    """
    try:
        input_tensor = preprocess_image(b64_str)
        input_name = session.get_inputs()[0].name
        model_output = session.run(None, {input_name: input_tensor})[0]
        recognized_text = decode_output(model_output)
        return recognized_text
    except Exception as e:
        print(f"识别过程中发生错误: {e}")
        raise