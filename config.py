import os
'''通用参数'''
PROJECT_PATH = os.path.split(os.path.abspath(__file__))[0]
BUILD_DIR_NAME = "build"
LOG_DIR_NAME = "log"


'''服务端参数'''
# 定义服务器上传文件的根目录，默认是项目文件夹下 ./upload
UPLOAD_ROOT_PATH = os.path.join(PROJECT_PATH,"upload")
# 这里需要自行设置
HOST = "0.0.0.0"
IP = 5000

'''客户端参数'''
# 同步最短等待时间，单位为秒
MIN_GAP = 1.5
# 同步的路径（需要绝对路径），每个目录会开一个线程，路径下的所有tex文件都会被编译
# 目前所有的tex文件会被编译后放到根路径的 `build` 文件夹下，因此不要有同名tex文件
# 目前不支持中文文件名（所有tex文件和tex依赖的图片等都不可以，会出错）
# 不建议设置太多路径，线程太多更新可能会较慢。
WATCH_DIR = [
    r"C:\Documents\Desktop\latex",

]
SERVER_HOST = "http://0.0.0.0:5000/"

