import hashlib
import base64
import io
import traceback

import httpx
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import redis
from PIL import Image
import numpy as np

from config import *

app = Flask(__name__)
CORS(app)

redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.253'
}


def calculate_md5_hash(data):
    md5_hash = hashlib.md5(data.encode('utf-8')).digest()
    return base64.b64encode(md5_hash).decode('utf-8')


def extract_main_color(img_url):
    md5_hash = calculate_md5_hash(img_url)

    if CACHE_ENABLED:
        cached_color = redis_client.get(md5_hash)
        if cached_color:
            return cached_color

    response = httpx.get(img_url, headers=headers)
    if response.status_code != 200:
        print(f"请求图片失败, 状态码: {response.status_code}")
        return

    img = Image.open(io.BytesIO(response.content))
    img = img.resize((50, int(50 * img.size[1] / img.size[0])))

    pixels = np.array(img)
    r, g, b = np.mean(pixels[:, :, 0]), np.mean(pixels[:, :, 1]), np.mean(pixels[:, :, 2])
    main_color = '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))

    if CACHE_ENABLED:
        redis_client.set(md5_hash, main_color, ex=CACHE_EXPIRE)

    return main_color


@app.before_request
def before_request():
    if request.path == '/api':  # api接口需要验证referer
        referer = request.headers.get('Referer')
        if not referer or not any(referer.startswith(allowed) for allowed in ALLOW_REFERER):
            return jsonify({"error": "无权访问"}), 403


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({"message": "欢迎使用主色调提取API"})


@app.route('/api', methods=['GET', 'POST'])
def handle_image_color():
    img_url = request.args.get("img") if request.method == 'GET' else request.json.get("img")
    if not img_url:
        return jsonify({"error": "缺少img参数"}), 400

    try:
        color = extract_main_color(img_url)
        return jsonify({"RGB": color})
    except Exception as e:
        return jsonify({"error": f"提取主色调失败：{e}", "img_url": img_url, "traceback": traceback.format_exc()}), 500


@app.route('/reload', methods=['POST', 'GET'])
def reload_cache():
    try:
        redis_client.flushdb()  # 清空 Redis 缓存
        return jsonify({"message": "缓存已清空"}), 200
    except Exception as e:
        return jsonify({"error": f"清空缓存失败：{e}", "traceback": traceback.format_exc()}), 500


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
