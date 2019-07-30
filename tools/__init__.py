import subprocess,threading,sys,os,config

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
    output_path = os.path.join(root_path,config.BUILD_DIR_NAME)
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
        pipe = subprocess.Popen(shell, shell=True,stdout=flog,cwd=output_path)

def get_flist(tid):
    root_path = os.path.join(config.UPLOAD_ROOT_PATH, f"{tid}")
    output_path = os.path.join(root_path, config.BUILD_DIR_NAME)
    fs = os.listdir(output_path)
    pdfs = [os.path.join(output_path,f) for f in fs if f.endswith("pdf")]

    return pdfs

def check_compile(tid):
    root_path = os.path.join(config.UPLOAD_ROOT_PATH,f"{tid}")
    output_path = os.path.join(root_path,config.BUILD_DIR_NAME)
    fs = os.listdir(output_path)
    pdfs = [f for f in fs if f.endswith("pdf")]
    flafs = [f for f in fs if f.endswith("flag")]
    return len(pdfs) == len(flafs)