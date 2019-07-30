#!/usr/bin/env bash
wget "http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz"
tar -xvf install-tl-unx.tar.gz
cd install-tl-20190728/
echo 'i'|sudo ./install-tl
cd ../
export PATH=/usr/local/texlive/2019/bin/x86_64-linux:$PATH
bash -c 'echo "export PATH=/usr/local/texlive/2019/bin/x86_64-linux:$PATH">>~/.bashrc'
sudo tlmgr install texliveonfly
sudo cp texliveonfly.py /usr/local/texlive/2019/texmf-dist/scripts/texliveonfly/texliveonfly.py
echo "Install Finished!"