# serve_aiohttp.py

from aiohttp import web
import recognize  # 导入我们自己的识别模块


def calculate_expression(expression: str) -> (str, int | None):
    """
    计算数学表达式字符串。

    输入:
        expression (str): 如 "3+6=?" 或 "12*5" 这样的字符串。

    输出:
        一个元组，包含清理后的表达式和计算结果。如果无法计算，结果为 None。
    """
    # 清理字符串，移除所有非运算符和数字的字符，例如'='和'?'
    cleaned_expression = expression.replace('?', '').replace('=', '')
    try:
        # 使用 eval 计算结果。
        # 注意：eval 有安全风险，但在这里是相对安全的，因为输入源是我们自己模型
        # 的输出，并且字符集非常有限。
        result = eval(cleaned_expression)
        return cleaned_expression, int(result)
    except Exception as e:
        print(f"无法计算表达式 '{cleaned_expression}': {e}")
        return cleaned_expression, None


async def init_model(app: web.Application):
    """
    在 aiohttp 应用启动时调用的异步函数。
    负责加载 ONNX 模型并将其存储在应用实例中，以便所有请求共享。
    """
    print("正在加载 ONNX 模型...")
    # 将加载好的模型会话存储在 aiohttp 应用的 'state' 中
    # 这是一种在 aiohttp 中共享资源（如数据库连接池、模型会话）的标准做法
    try:
        app['onnx_session'] = recognize.load_model()
    except Exception as e:
        print(f"致命错误：模型未能加载，应用无法启动。错误: {e}")
        # 在实际生产中，你可能希望在这里让应用启动失败
        app['onnx_session'] = None


async def handle_recognize(request: web.Request):
    """
    处理验证码识别请求的核心句柄。
    """
    try:
        # 从应用实例中获取共享的 ONNX 会话
        onnx_session = request.app.get('onnx_session')

        # 检查模型是否已成功加载
        if not onnx_session:
            return web.json_response(
                {"error": "模型未加载，服务尚未准备好"},
                status=503  # Service Unavailable
            )

        # 1. 解析传入的 JSON 数据
        data = await request.json()
        b64_img = data.get("img")

        if not b64_img:
            return web.json_response(
                {"error": "请求体中缺少 'img' 字段"},
                status=400  # Bad Request
            )

        # 2. 调用识别模块进行识别
        # 注意：这里的 recognize.run_recognition 是一个同步（阻塞）函数。
        # 在高并发场景下，为了不阻塞事件循环，可以考虑使用 run_in_executor。
        # 但对于快速的模型推理，直接调用通常也是可接受的。
        recognized_text = recognize.run_recognition(onnx_session, b64_img)

        # 3. 根据识别结果计算数学公式
        _, value = calculate_expression(recognized_text)

        # 4. 构造并返回成功的JSON响应
        return web.json_response({
            "text": recognized_text,
            "value": value
        })

    except Exception as e:
        # 捕获所有可能的异常
        print(f"请求处理失败: {e}")
        return web.json_response(
            {"error": "处理请求时发生内部错误。"},
            status=500  # Internal Server Error
        )

async def handle_home(request: web.Request):
    s = open('index.html', "r")
    return web.Response(text=s.read(), content_type='text/html')

# --- 主程序入口 ---
if __name__ == "__main__":
    # 创建 aiohttp 应用实例
    app = web.Application()

    # 注册启动事件，在服务启动时调用 init_model 函数
    app.on_startup.append(init_model)

    # 添加路由，将 POST /recognize 请求映射到 handle_recognize 句柄
    app.router.add_post("/recognize", handle_recognize)
    app.router.add_get("/", handle_home)

    # 启动应用服务器
    print("启动 aiohttp 服务器")
    web.run_app(app, host="0.0.0.0", port=8000)
