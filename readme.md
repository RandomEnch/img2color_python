# Img2color-python

对于 https://github.com/anzhiyu-c/img2color-go 项目的 python 重构版，删去了MongoDB，使用 Redis 缓存数据，使用 flask 框架

## Vercel部署

1. 点击项目右上角fork叉子

2. 登录[vercel](https://vercel.com/)

3. 在[vercel](https://vercel.com/)导入项目

4. 部署时添加环境变量

5. 国内访问需绑定自定义域名

6. [redis数据库](https://upstash.com/)

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

| 配置项           | 类型   | 说明                                                     |
| ---------------- | ------ | -------------------------------------------------------- |
| REDIS_STR        | string | REDIS连接字符串(redis://default:xxx@xxx.upstash.io:6379) |
| CACHE_ENABLED    | bool   | 是否使用REDIS缓存(True/False)(不设置默认False)           |
| CACHE_EXPIRE     | int    | 缓存过期时间(秒)(可选，默认86400)                        |
| ALLOWED_REFERERS | string | 允许的refer域名，支持正则表达式(逗号分隔)                |

