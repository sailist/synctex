import subprocess,threading,sys,os,config
import json

def popenAndCall(args, shell=True,stdout=sys.stdout,cwd=os.getcwd(),onExit=None):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that
    would give to subprocess.Popen.
    """
    def runInThread(onExit):
        proc = subprocess.Popen(args,shell=shell,stdout=stdout,cwd=cwd)
        proc.wait()
        if onExit is not None:
            onExit()
        return
    thread = threading.Thread(target=runInThread, args=(onExit))
    thread.start()
    # returns immediately after the thread starts
    return thread


def compile_tex(tex_files:list,root_path):
    output_path = os.path.join(root_path)
    log_path = os.path.join(root_path,"log")
    os.makedirs(output_path,exist_ok=True)
    os.makedirs(log_path,exist_ok=True)

    for tex_file in tex_files:

        _,fname = os.path.split(tex_file)
        fpre,_ = os.path.splitext(fname)

        open(os.path.join(output_path,f"{fpre}.flag"),"w").close()

        params = ["texliveonfly",]
        relpath = os.path.relpath(tex_file,output_path)
        params.append(relpath)
        params.extend(["-r","True"])
        shell = " ".join(params)
        flog = open(os.path.join(log_path,f"{fpre}.txt"),"w",encoding="utf-8")

        subprocess.Popen(shell, shell=True,stdout=flog,cwd=output_path)

def get_flist2(tid):
    log_file_path = os.path.join(config.UPLOAD_ROOT_PATH, f"{tid}","build.log")

    jstr = json.load(open(log_file_path,"r"))
    pdfs = []
    errfs = []
    for fpath,res in jstr.items():
        path,fname = os.path.split(fpath)
        fpre,_ = os.path.splitext(fname)
        if res == 1:
            errlog_file = os.path.join(config.UPLOAD_ROOT_PATH,f"{tid}",config.LOG_DIR_NAME,f"{fpre}.txt")
            errfs.append(errlog_file)
            if os.path.exists(fpath):
                pdfs.append(fpath)
        else:
            pdfs.append(fpath)

    pdfs = [os.path.relpath(f,config.UPLOAD_ROOT_PATH) for f in pdfs]
    errfs = [os.path.relpath(f,config.UPLOAD_ROOT_PATH) for f in errfs]

    return pdfs,errfs

def get_flist(tid):
    root_path = os.path.join(config.UPLOAD_ROOT_PATH, f"{tid}")
    output_path = os.path.join(root_path, config.BUILD_DIR_NAME)
    log_path = os.path.join(root_path,config.LOG_DIR_NAME)

    fs = os.listdir(output_path)
    pdfs = []
    errfs = []

    for f in fs:
        if f.endswith("pdf"):
            pdfs.append(f)

    for f in fs:
        if f.endswith("res"):
            fpre,_ = os.path.splitext(f)
            pdf = f"{fpre}.pdf"
            if pdf not in pdfs: # 编译未通过
                logf = os.path.join(log_path,f"{fpre}.txt")
                errfs.append(logf)

    pdfs = [os.path.join(output_path,f) for f in pdfs]
    errfs = [os.path.join(log_path,f) for f in errfs]

    pdfs = [os.path.relpath(f,config.UPLOAD_ROOT_PATH) for f in pdfs]
    errfs = [os.path.relpath(f,config.UPLOAD_ROOT_PATH) for f in errfs]

    return pdfs,errfs

def check_compile(tid):
    flag_path = os.path.join(config.UPLOAD_ROOT_PATH,f"{tid}","1")
    return os.path.exists(flag_path)



def convert_markdown(file,output):
    from marktex.texrender.toTex import MarkTex

    doc = MarkTex.convert_file(file,output_dir=output)
    path,fname = os.path.split(file)
    fpre,_ = os.path.splitext(fname)
    doc.generate_tex(fpre)

    texfpath = os.path.join(path,f"{fpre}.tex")
    return texfpath