# -*- coding: utf-8 -*-
import os,time,config
import subprocess
from flask import Flask, request, url_for, send_from_directory,render_template
from werkzeug.utils import secure_filename

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


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
def compile_tex(tex_files:list,root_path):
    output_path = os.path.join(root_path,"build")
    log_path = os.path.join(root_path,"log")
    os.makedirs(output_path,exist_ok=True)
    os.makedirs(log_path,exist_ok=True)

    params = ["texliveonfly",]
    for tex_file in tex_files:
        relpath = os.path.relpath(tex_file,output_path)
        params.append(relpath)
    params.extend(["-r","True"])

    shell = " ".join(params)
    flog = open(os.path.join(log_path,"log.txt"),"w",encoding="utf-8")
    pipe = subprocess.Popen(shell, shell=True,stdout=flog,cwd=output_path)



def check_compile_done():
    pass

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
        compile_tex(tex_file_list,root_path)

        return f"{tid}"
    return html

@app.route('/drag', methods=['GET', 'POST']) # 编译tex的
def upload_dragfile():
    return render_template("uploadFiles.html")

def run(host = "0.0.0.0",port=5000):
    app.run(host=host,port=port)
