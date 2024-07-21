# Img2color-python

对于 https://github.com/anzhiyu-c/img2color-go 项目的 python 重构版，删去了MongoDB，使用 Redis 缓存数据，使用 flask 框架

## 服务器部署

需要 python 环境 (推荐 >= 3.7.2)

1. 安装依赖

```bash
pip3 install -r ./requirements.txt
```

2. 修改 `config.py` 配置，设置端口和redis数据库以及准许调用api的referer
3. 运行

```bash
python3 ./main.py
```

4. 进行nginx反代、进程守护等操作，绑定域名

## 使用

例如：/api?img=https://img.randomench.top/i/2024/07/21/669d048e7a5c9.jpg

部署后只需要 域名/api 访问

必填参数img: url

| 配置项           | 说明                     |
| ---------------- | ------------------------ |
| REDIS_HOST       | REDIS地址                |
| REDIS_PORT       | REDIS端口                |
| REDIS_DB         | REDIS数据库名            |
| CACHE_ENABLED    | bool值 是否使用REDIS缓存 |
| CACHE_EXPIRE     | int 缓存过期时间（秒）   |
| DEBUG            | bool值，是否开启debug    |
| HOST             | 地址                     |
| PORT             | 端口                     |
| ALLOWED_REFERERS | 允许的refer域名          |

