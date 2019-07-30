# -*- coding: utf-8 -*-
import os,time,config
import tools
from flask import Flask, request, send_from_directory,render_template
from werkzeug.utils import secure_filename

from tools import compile_tex

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif',"tex","ttc"])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd()
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h1>图片上传</h1>
    <form method=post enctype=multipart/form-data>
         <input type=file name=file>
         <input type=submit value=上传>
    </form>
    '''


def allowed_file(filename):
    return True

@app.route('/check/<tid>')
def check_file(tid):
    return f"{tools.check_compile(tid)}"

@app.route("/download/<tid>/<filename>", methods=['GET'])
def download_file(tid,filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录
    directory = os.path.join(config.UPLOAD_ROOT_PATH,tid,filename)
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist("file")
        tid = time.time()
        root_path = os.path.join(config.UPLOAD_ROOT_PATH,f"{tid}")
        tex_file_list = []
        for file in files:
            if file and allowed_file(file.filename):
                relepath,fname = os.path.split(file.filename)
                abspath = os.path.join(root_path,relepath)
                os.makedirs(abspath,exist_ok=True)

                fname = secure_filename(fname)
                absfname = os.path.join(root_path,relepath,fname)
                if absfname.endswith("tex"):
                    tex_file_list.append(absfname)
                print(absfname)
                file.save(absfname)
        compile_tex(tex_file_list, root_path)

        return f"{tid}"
    return html

@app.route('/drag', methods=['GET', 'POST']) # 编译tex的
def upload_dragfile():
    return render_template("uploadFiles.html")

def run(host = "0.0.0.0",port=5000):
    app.run(host=host,port=port)
