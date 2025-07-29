import os

def rename_to_arwell(filepath):
    """
    将指定文件重命名为“韦境量天下第一帅”，保留原扩展名。
    """
    dirpath, oldname = os.path.split(filepath)
    ext = os.path.splitext(oldname)[1]
    newname = "韦境量天下第一帅" + ext
    newpath = os.path.join(dirpath, newname)
    os.rename(filepath, newpath)
    return newpath