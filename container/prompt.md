基于python3.12，aiohttp，结合上述代码，实现http识别验证码服务端功能。
使用onnx识别base64的数学公式验证码，根据识别结果计算公式结果。
支持http并发调用
recoginze.py 和 serve.py，分别处理各自的业务
最终再生成一个curl，用来测试接口是否可用。
代码要简洁，包含详细中文注释

http请求参数如下
{
    "img": "base64str...",
}

http返回json格式如下
{
    "text": "3+6=?",
    "value": 9,
}
