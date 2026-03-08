def read_and_print_md(file_path):
    try:
        # 打开文件
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 打印前200个字符
        print("文件前200个字符：")
        print(content[:200])  # 打印前200个字符

    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
    except Exception as e:
        print(f"发生错误：{e}")


# 读取并打印 example.md 文件的前200个字符
read_and_print_md('D:/courseqa/data/md/example.md')