import sys
import webbrowser
from . import rename_to_arwell

def main():
    if len(sys.argv) != 2:
        print("用法: arwell <文件路径>")
        sys.exit(1)
    filepath = sys.argv[1]
    try:
        newpath = rename_to_arwell(filepath)
        print(f"已重命名为: {newpath}")
    except Exception as e:
        print(f"重命名失败: {e}")
        sys.exit(2)

def open_blog():
    """跳转到 jingliangwei.github.io/blog 网页"""
    webbrowser.open("https://jingliangwei.github.io/blog")

if __name__ == "__main__":
    main()
