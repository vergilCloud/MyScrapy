import os;

def rename():
    i = 0
    path = (r'E:\workspace\scrapy-project\data\ppp');
    filelist = os.listdir(path)  # 该文件夹下所有的文件（包括文件夹）
    for files in filelist:  # 遍历所有文件
        i = i + 1
        Olddir = os.path.join(path, files);  # 原来的文件路径
        if os.path.isdir(Olddir):  # 如果是文件夹则跳过
            continue;
        filename = os.path.splitext(files)[0];  # 文件名
        filetype = '.txt';  # 文件扩展名 这里以图片为例 可以顺便修改格式
        Newdir = os.path.join(path, str(i+1000000) + filetype);  # 新的文件路径
        os.rename(Olddir, Newdir)  # 重命名

rename()