import config,time,zipfile
from io import BytesIO
import threading
import os,json
import requests
from urllib.parse import urljoin
from urllib.request import urlretrieve,urlopen
import requests

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TexDirSyncManager(FileSystemEventHandler):
    '''负责监听文件变动，当文件变动符合上传规则时候，通过TexDirSyncTool
    上传文件，并负责下载
    '''
    modify_recompile_ext = {".tex",".jpg",".eps",".png"}


    def __init__(self,host,root_path) -> None:
        super().__init__()
        self.synctool = TexDirSyncTool(host,root_path)
        self.root_path = root_path
        self.host = host
        self.last_sync_time = time.time()
        self.lock = threading.Lock()

    def on_moved(self, event):
        super().on_moved(event)

    def on_created(self, event):
        super().on_created(event)

    def on_deleted(self, event):
        super().on_deleted(event)

    def on_modified(self, event):
        if time.time()-self.last_sync_time < 2:
            return

        if event.is_directory:
            return
        else:
            path = str(event.src_path)
            if path.endswith("pdf"):
                return

            allfs = []
            _,ext = os.path.splitext(path)
            if ext in TexDirSyncManager.modify_recompile_ext:
                pathiter = os.walk(self.root_path)
                for dir_path,_,fs in pathiter:
                    fs = [os.path.join(dir_path,f) for f in fs if not f.endswith("pdf")]
                    allfs.extend(fs)

            syncthread = threading.Thread(target=self.sync, args=(allfs,))
            syncthread.setDaemon(True)
            syncthread.start()

        super().on_modified(event)


    def sync(self,flist):
        '''新线程同步'''
        compare_result = False
        if self.lock.acquire(blocking=False):
            compare_result = time.time() - self.last_sync_time>config.MIN_GAP
            self.lock.release()

        if compare_result and self.lock.acquire():
            start = time.time()

            print("[info*]synchronizing...")
            self.last_sync_time = time.time()
            print(f"[info*]uploading files...")
            tid = self.synctool.upload(flist)
            i = 0.
            while not self.synctool.check(tid):
                time.sleep(0.5)
                print(f"\r compile {i/2}s",end="\0",flush=True)
                i+=1
            print("\n[info*]compile finished, get files.")

            sssize,ffsize = self.synctool.direct_download(tid)
            end = time.time()
            print(f"[info*]compiled, {sssize} successes, {ffsize} error, use {end-start:.1f}s.")
            self.lock.release()

class TexDirSyncTool():
    '''负责上传、下载、询问，根据状态进行相关处理由TexDirSyncManager完成'''
    def __init__(self,root_url,root_path) -> None:
        '''

        :param root_url:请求的根url，根据config中的设置传入
        :param root_path:监控根路径，要求是绝对路径，用来对服务器说明目录结构
        '''
        self.root_url = root_url
        self.root_path = root_path

    def upload(self,flist:list):
        '''
        :param flist:绝对路径构造的文件
        :return:
        '''

        filenames = [os.path.relpath(f,self.root_path) for f in flist]
        files = [
            ("file",(filename, open(file, "rb")))
                for filename, file in zip(filenames, flist)
        ]
        url = urljoin(self.root_url,"uploads")
        response = requests.post(url,None,files=files)
        if response.status_code == 200:
            tid = response.content.decode()
            return tid
        raise Exception(f"request wrone {response.status_code}")

    def check(self,tid):
        url = urljoin(self.root_url,f"check/{tid}")
        response = requests.get(url)
        if response.status_code == 200:
            return response.content.decode()=="True"
        raise Exception(f"request wrone {response.status_code}")

    def get_flist(self,tid):
        url = urljoin(self.root_url,f"update/{tid}")
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.content.decode())
        raise Exception(f"request wrone {response.status_code}")

    def direct_download(self,tid):
        print(f"[info*]downloading...")
        furl = urljoin(self.root_url,f"directly/{tid}")
        uf = requests.get(furl,stream=True)

        sssize,ffsize = 0,0
        if uf.status_code == 200:
            bf = BytesIO(uf.content)

            with zipfile.ZipFile(bf,"r") as zf:
                save_path = os.path.join(self.root_path, config.BUILD_DIR_NAME)
                log_path = os.path.join(self.root_path,config.LOG_DIR_NAME)
                os.makedirs(save_path, exist_ok=True)
                os.makedirs(log_path, exist_ok=True)
                namelist = zf.namelist()
                for fn in namelist:
                    if fn.endswith("pdf"):
                        zf.extract(fn,save_path)
                        print(f" {os.path.join(save_path,fn)}")
                        sssize+=1
                    else:
                        zf.extract(fn,log_path)
                        print(f" {os.path.join(log_path,fn)}")
                        ffsize+=1

            print(f"[info*]download finished.")
            return sssize,ffsize
        else:
            raise Exception(f"[error*]request failed with status code {uf.status_code}.")

    def download(self,flist):

        for f in flist:
            print(f"[info*]downloading [{f}].")
            furl = urljoin(self.root_url,f"download/{f}")
            _,fname = os.path.split(f)

            save_path = os.path.join(self.root_path,"build")
            os.makedirs(save_path,exist_ok=True)

            storepath = os.path.abspath(os.path.join(save_path,fname))
            urlretrieve(furl,storepath)
            print(f"[info*]download finished, store in [{storepath}].")



class DirManager():
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        self.syncpaths = config.WATCH_DIR
        self.host = config.SERVER_HOST
        self.observers = []
        for path in self.syncpaths:
            print(f"[info*]start observer {path}")
            observer = self.start_watch(path)
            self.observers.append(observer)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for observer in self.observers:
                observer.stop()
                observer.join()

    def start_watch(self,watch_dir):
        host = self.host

        # logging.basicConfig(level=logging.INFO,
        #                     format='%(asctime)s - %(message)s',
        #                     datefmt='%Y-%m-%d %H:%M:%S')

        event_handler = TexDirSyncManager(host, watch_dir)
        observer = Observer()
        observer.schedule(event_handler, r"C:\Documents\Desktop\latex", recursive=True)
        observer.start()
        return observer