import hashlib
import base64
import io
import os
import re
import traceback
import httpx
import redis
import numpy as np

from loguru import logger
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app)

CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'False').lower() in ['true', '1', 't']
CACHE_EXPIRE = int(os.getenv('CACHE_EXPIRE', 86400))
REDIS_STR = os.getenv('REDIS_HOST', 'redis://default:********@****.upstash.io:6379')
ALLOW_REFERER = os.getenv('ALLOW_REFERER', '').split(',')

if CACHE_ENABLED:
    redis_client = redis.StrictRedis.from_url(REDIS_STR, decode_responses=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,zh-HK;q=0.7',
    'Cache-Control': 'no-cache',
    'priority': 'u=0, i',
    'Pragma': 'no-cache',
}


def calculate_md5_hash(data):
    md5_hash = hashlib.md5(data.encode('utf-8')).digest()
    return base64.b64encode(md5_hash).decode('utf-8')


def extract_main_color(img_url):
    try:
        if CACHE_ENABLED:
            cached_color = redis_client.get(img_url)
            if cached_color:
                return cached_color
        # md5_hash = calculate_md5_hash(img_url)
        response = httpx.get(img_url, headers=headers, follow_redirects=True)
        if response.status_code != 200 and response.status_code != 304:
            logger.error(f"请求图片 {img_url} 失败，状态码：{response.status_code}")
            return "#FF8C66"

        img = Image.open(io.BytesIO(response.content))
        img = img.resize((50, int(50 * img.size[1] / img.size[0])))

        pixels = np.array(img)
        r, g, b = np.mean(pixels[:, :, 0]), np.mean(pixels[:, :, 1]), np.mean(pixels[:, :, 2])
        main_color = '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))

        if CACHE_ENABLED:
            redis_client.set(img_url, main_color, ex=CACHE_EXPIRE)

        logger.info(f"图片 {img_url} 的主色调为 {main_color}")

        return main_color

    except:
        logger.error(f"处理图片 {img_url} 时出现错误: {traceback.format_exc()}")
        return "#FF8C66"


@app.before_request
def before_request():
    if request.path == '/apis':  # API 接口需要验证 Referer
        referer = request.headers.get('Referer')
        # if not referer:
        #     return jsonify({"error": "无权访问"}), 403

        if not ALLOW_REFERER:
            return

        # 检查 referer 是否符合任一允许的模式（普通字符串或正则表达式）
        allowed = False
        for pattern in ALLOW_REFERER:
            # 若含有正则符号，则认为它是正则表达式
            if '\\' in pattern or '*' in pattern:
                if re.match(pattern, referer):
                    allowed = True
                    break
            else:  # 否则认为它是普通字符串
                if referer.startswith(pattern):
                    allowed = True
                    break

        if not allowed:
            return jsonify({"error": "无权访问"}), 403


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    logger.info(f"{request.method} {request.path}")
    return jsonify({"message": "欢迎使用主色调提取API"})


@app.route('/api', methods=['GET', 'POST'])
def handle_image_color():
    img_url = request.args.get("img") if request.method == 'GET' else request.json.get("img")
    if not img_url:
        logger.info(f"{request.method} {request.path} | 缺少img参数")
        return jsonify({"error": "缺少img参数"}), 400

    try:
        logger.info(f"{request.method} {request.path} | 提取图片 {img_url} 的主色调")
        color = extract_main_color(img_url)
        return jsonify({"RGB": color})
    except Exception as e:
        return jsonify({"error": f"提取主色调失败：{e}", "img_url": img_url, "traceback": traceback.format_exc()}), 500


@app.route('/reload', methods=['POST', 'GET'])
def reload_cache():
    logger.info(f"{request.method} {request.path}")
    try:
        redis_client.flushdb()  # 清空 Redis 缓存
        return jsonify({"message": "缓存已清空"}), 200
    except Exception as e:
        return jsonify({"error": f"清空缓存失败：{e}", "traceback": traceback.format_exc()}), 500


# if __name__ == '__main__':
#     app.run(host=HOST, port=PORT, debug=DEBUG)
