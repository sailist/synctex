# -*- coding: utf-8 -*-
import os,time,config
import tools
import zipfile
from io import BytesIO

from flask import Flask, request, send_from_directory,render_template,send_file,Response,make_response
from flask import jsonify
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

@app.route('/update/<tid>')
def get_flist(tid):
    pdfs,errfs = tools.get_flist(tid)

    return jsonify(dict(
        success=pdfs,
        failed=errfs,
    ))

@app.route('/directly/<tid>',methods=["GET","POST"])
def direct_download(tid):
    pdfs,errfs = tools.get_flist(tid)

    print("hello")
    memory_file = BytesIO()
    zipfname = f"{tid}.zip"
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for _file in pdfs+errfs:
            abs_file = os.path.join(config.UPLOAD_ROOT_PATH,_file)
            _,fname = os.path.split(_file)
            with open(abs_file, 'rb') as fp:
                zf.write(abs_file,fname)

    response = make_response(memory_file.getvalue())
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = f'attachment; filename={tid}.zip'
    return response
    # return send_file(memory_file.getvalue(), attachment_filename=zipfname,mimetype = 'zip', as_attachment=True)




@app.route("/download/<path:filename>", methods=['GET','POST'])
def download_file(filename):
    '''
    :param filename:{tid}/...
    :return:
    '''
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    path,fname = os.path.split(filename)
    directory = os.path.join(config.UPLOAD_ROOT_PATH,path)
    print(directory,fname)
    return send_from_directory(directory, fname, as_attachment=True)

@app.route('/uploads',methods=["POST"])
def uploaded_file():
    files = request.files.getlist("file")
    tid = int(time.time())
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

@app.route('/', methods=['GET', 'POST']) # 编译tex的
def upload_dragfile():
    return render_template("uploadFiles.html")

def run(host = "0.0.0.0",port=5000):
    app.run(host=host,port=port)
