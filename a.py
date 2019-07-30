import subprocess


shell = "texliveonfly example.tex"
pipe = subprocess.Popen(shell, shell=True)


