# 创建应用实例
import sys

from wxcloudrun import app
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 启动Flask Web服务
if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])
