# test.py

import os
import base64
import recognize  # 导入我们自己的识别模块

# --- 常量定义 ---
TEST_DATA_DIR = '../datasets/test'

def calculate_expression(expression: str) -> (str, int | None):
    """
    计算数学表达式字符串。
    (这个辅助函数从 serve.py 复制而来，以便脚本可以独立运行)
    
    输入:
        expression (str): 如 "3+6=?" 或 "12*5" 这样的字符串。
    
    输出:
        一个元组，包含清理后的表达式和计算结果。如果无法计算，结果为 None。
    """
    # 清理字符串，移除所有非运算符和数字的字符，例如'='和'?'
    cleaned_expression = expression.replace('?', '').replace('=', '')
    
    try:
        # 使用 eval 计算结果。
        result = eval(cleaned_expression)
        return cleaned_expression, int(result)
    except Exception:
        # 如果表达式无效（例如，模型识别错误 "3++6"），则返回 None
        return cleaned_expression, None

def run_test_suite():
    """
    执行完整的测试流程。
    """
    # 1. 检查测试目录是否存在
    if not os.path.isdir(TEST_DATA_DIR):
        print(f"错误: 测试目录 '{TEST_DATA_DIR}' 不存在。")
        return

    # 2. 加载 ONNX 模型（整个测试过程只加载一次）
    print("正在加载模型...")
    try:
        onnx_session = recognize.load_model()
    except Exception as e:
        print(f"模型加载失败: {e}")
        return
        
    # 3. 获取所有测试图片文件列表
    try:
        # 筛选出常见的图片文件格式，避免处理 .DS_Store 等隐藏文件
        image_files = [f for f in os.listdir(TEST_DATA_DIR) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        if not image_files:
            print(f"警告: 在 '{TEST_DATA_DIR}' 目录中没有找到图片文件。")
            return
    except FileNotFoundError:
        print(f"错误: 无法访问测试目录 '{TEST_DATA_DIR}'。")
        return

    print(f"\n开始测试 {len(image_files)} 张图片...")
    
    # 初始化成功和失败的计数器
    success_count = 0
    fail_count = 0
    
    # 4. 遍历所有图片文件
    for filename in image_files:
        image_path = os.path.join(TEST_DATA_DIR, filename)
        
        try:
            # 读取图片文件 -> 转换为 Base64 字符串
            with open(image_path, 'rb') as f:
                img_bytes = f.read()
                b64_img = base64.b64encode(img_bytes).decode('utf-8')

            # 调用识别模块进行识别
            recognized_text = recognize.run_recognition(onnx_session, b64_img)
            
            # 计算结果
            _, value = calculate_expression(recognized_text)
            
            # 打印结果
            if value is not None:
                print(f"文件名: {filename:<20} -> 识别结果: '{recognized_text}', 计算值: {value}")
                success_count += 1
            else:
                # 识别的文本无法计算
                print(f"文件名: {filename:<20} -> 识别结果: '{recognized_text}', (计算失败)")
                fail_count += 1

        except Exception as e:
            print(f"文件名: {filename:<20} -> !!! 处理失败: {e}")
            fail_count += 1
            
    # 5. 打印最终总结
    print("\n" + "="*40)
    print("测试完成！")
    print(f"总计: {len(image_files)} 张图片")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    if len(image_files) > 0:
        accuracy = (success_count / len(image_files)) * 100
        print(f"准确率 (成功计算): {accuracy:.2f}%")
    print("="*40)

# --- 主程序入口 ---
if __name__ == "__main__":
    run_test_suite()