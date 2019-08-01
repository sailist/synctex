# synctex
集成服务端部署tex编译器、文件同步、自动编译、打开网站拓展文件编译

目前该服务部署在我的服务器上，学生服务器，轻点 http://119.23.70.249:5000/

## 特性
- 可以只在服务端部署，可以通过访问网站上传文件进行编译
- 可以同时在本地和服务端部署，通过监听文件变动，会自动进行上传、编译、下载，配合SumatraPDF，可以实现“本地Overleaf”
- 项目下有Linux环境下的部署脚本（目前Ubuntu16.04下无问题），可以一键部署
- 和我的项目MarkTex结合，同时可以直接转换Markdown到PDF

## 使用方法
```bash
git clone https://github.com/sailist/synctex
cd synctex
```

### 部署Linux
如果未部署Texlive，可以通过`installatexlive`目录下的脚本部署

```bash
cd installlatexlive
sudo bash ./install.bash 
```

如果已经部署Texlive，需要安装texliveonfly来确保遇到未安装的包时可以自动安装
```bash
cd installlatexlive
tlmgr install texliveonfly
sudo cp texliveonfly.py /usr/local/texlive/2019/texmf-dist/scripts/texliveonfly/texliveonfly.py
``` 

> 最后一步复制是我更改后的脚本文件，增添了自动删除编译过程文件和多文件同时编译以及在目录下生成编译结果文件的命令，在本项目中需要用到，否则可能运行过程会出错

所有步骤完成后，尝试运行
```bash
cd installlatexlive
texliveonfly test.tex -r True
```
如果能在目录下生成pdf，则说明一切安装成功

### 服务端使用方法
安装依赖：
```bash
pip install flask
```

在确保部署TexLive和texliveonfly成功，并且运行上一步最后的测试无误后，在config.py中，更改服务器的连接url，随后运行
```bash
python3 run_server.py
```

### 客户端使用方法
安装依赖：
```bash
pip install watchdog
```

在config.py中修改连接服务器的ip和端口，然后运行
```bash
python3 run_client.py
```