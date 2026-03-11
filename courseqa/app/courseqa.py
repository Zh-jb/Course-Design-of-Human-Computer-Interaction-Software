import os

def read_and_print_md(file_path):
    '''
    读取.md文件并打印前200个字符
    :param file_path:
    :return:
    '''
    try:
        # 打开文件，读取内容
        with open(file_path,'r',encoding = 'utf-8') as file:
            content = file.read()
        return content
        #打印文件内容前200个字符
        print("文件前200个字符：")
        print(content[:200]) #打印前200个字符

    except FileNotFoundError:
        print(f"错误：找不到文件{file_path}")
        return None

def split_paragraphs(text):
    '''
    将文本按空行拆分为段落列表，并过滤空段落
    :param text:
    :return:
    '''
    raw_paragraphs = text.split("\n\n") #按空行分段
    paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
    return paragraphs

def analyze_paragraphs(paragraphs):
    '''
    输出段落数、最长段落长度，并打印每个段落内容
    :param paragraphs:
    :return:
    '''
    num_paragraphs = len(paragraphs)
    if num_paragraphs == 0:
        print("没有找到有效段落。")
        return

    print(f"段落数：{num_paragraphs}")
    print("\n每个段落内容：")
    for i, p in enumerate(paragraphs, 1):
        print(f"段落{i}:{p}\n")
    #最长段落长度
    longest_length = max(len(p) for p in paragraphs)
    print(f"最长段落长度{longest_length}个字符")
    # 最短段落长度
    shortest_length = min(len(p) for p in paragraphs)
    print(f"最短段落长度{shortest_length}个字符")
    #所有段落的总字符数
    sum_length = sum(len(p) for p in paragraphs)
    print(f"所有段落的总字符数为{sum_length}个字符")
    #平均每段总字符数
    avg_length = sum_length/len(paragraphs)
    print(f"平均每段字符数为{avg_length}个字符")
    para_with_info = [(p, len(p), i + 1) for i, p in enumerate(paragraphs)]
    # 按长度降序排序，取第一个就是最长段落
    longest_para = max(para_with_info, key=lambda x: x[1])
    print("\n 最长段落信息：")
    print(f"段落序号：{longest_para[2]}")
    print(f"段落长度：{longest_para[1]} 个字符")
    print(f"段落完整内容：\n{longest_para[0]}\n")
    # 按长度降序排序
    sorted_para = sorted(para_with_info, key=lambda x: x[1], reverse=True)
    print(" 段落长度排行榜（从长到短）：")
    for rank, (p, length, idx) in enumerate(sorted_para, 1):
        print(f"第{rank}名 - 段落{idx}：{length} 个字符")

def read_and_print_md_row(file_path):
    '''
    按行读取.md文件
    :param file_path:
    :return:
    '''
    # 打开文件，读取内容
    with open(file_path, 'r', encoding='utf-8') as file:
        all_lines = file.readlines()
        #总行数
        print(f"总行数{len(all_lines)}")
        #非空行数
        empty_row_len = len([line for line in all_lines if line.strip()])
        print(f"非空行数{empty_row_len}")
    return all_lines


def main():
    # 定义文件路径
    file_path = r"D:\courseqa\data\md\example.md"
    #调用函数并打印文件内容
    content = read_and_print_md(file_path)
    if content:
        print("文件前200个字符:")
        print(content[:200])
        print("-"*50)

        # 按空行拆分段落
        paragraphs = split_paragraphs(content)
        # 分析段落
        analyze_paragraphs(paragraphs)

    read_and_print_md_row(file_path)



if __name__ == '__main__':
    main()