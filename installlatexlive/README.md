在Linux下部署Latex，使用手动安装方式，在Ubuntu16.04下亲测好使

运行方式
```bash
sudo ./install.bash
```

目录下的texliveonfly.py是我修改过的，可以支持多文件参数传递，并且添加了编译完成后自动删除编译过程文件的参数，具体使用方式：

```bash
texliveonfly file1.tex file2.tex 
texliveonfly file1.tex file2.tex -r True
texliveonfly file1.tex file2.tex -r True -c pdflatex
...其余命令使用方式通过参数--help查看
```
> -r为编译完成后自动删除过程文件，默认为False
> -c为指定编译器，为了支持中文我更改了默认选项，默认为xelatex