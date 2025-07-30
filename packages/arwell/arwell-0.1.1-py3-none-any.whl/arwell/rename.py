import os

def rename_to_arwell(filepath):
    """
    将指定文件重命名为“韦境量天下第一帅”。
    """
    dirpath = os.path.dirname(filepath)
    new_name = "韦境量天下第一帅" + os.path.splitext(filepath)[1]
    new_path = os.path.join(dirpath, new_name)
    os.rename(filepath, new_path)
    return new_path