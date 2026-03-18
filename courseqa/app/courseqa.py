import os
import glob

def read_md_file(file_path):
    """
    读取 Markdown 文件内容，处理空文件/全空白文件场景
    参数:
        file_path (str): Markdown 文件路径
    返回:
        str/None: 成功返回文件内容（空文件返回空字符串），失败返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"【错误】文件不存在：{file_path}")
        return None
    except PermissionError:
        print(f"【错误】无权限读取文件：{file_path}")
        return None
    except Exception as e:
        print(f"【错误】读取文件 {file_path} 失败：{str(e)}")
        return None

def split_paragraphs(text):
    """
    按空行拆分文本为段落列表，过滤空段落/全空白段落
    参数:
        text (str): 输入文本（支持空字符串）
    返回:
        list[str]: 清洗后的有效段落列表
    """
    if not text or text.strip() == "":
        return []
    raw_paragraphs = text.split("\n\n")
    paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
    return paragraphs

def get_paragraph_stats(paragraphs, raw_content):
    """
    完整统计段落/文件信息，纯封装无打印，满足任务要求
    参数:
        paragraphs (list[str]): 有效段落列表
        raw_content (str): 原始文件内容（用于统计总字符数）
    返回:
        dict: 统计结果字典，包含所有报告所需字段
    """
    num_paragraphs = len(paragraphs)
    # 统计各长度指标，空段落时默认0
    longest_length = max((len(p) for p in paragraphs), default=0)
    shortest_length = min((len(p) for p in paragraphs), default=0)
    total_char = len(raw_content.replace("\n", "").replace(" ", ""))  # 纯内容总字符（去换行/空格）
    avg_length = round(total_char / num_paragraphs, 2) if num_paragraphs > 0 else 0
    return {
        "num_paras": num_paragraphs,
        "longest_len": longest_length,
        "shortest_len": shortest_length,
        "total_char": total_char,
        "avg_len": avg_length
    }

def write_formatted_paras(paragraphs, output_path):
    """
    按规范格式写入段落文件（升级任务4），自动创建输出目录
    格式：段落X + 长度 + 内容 + 分隔线
    参数:
        paragraphs (list[str]): 有效段落列表
        output_path (str): 段落输出文件路径
    返回:
        bool: 写入成功True，失败False
    """
    try:
        # 自动创建输出目录，处理空目录路径（仅文件名）
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        # 按规范格式写入
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, para in enumerate(paragraphs, 1):
                para_len = len(para)
                f.write(f"段落 {i}\n")
                f.write(f"长度：{para_len}\n")
                f.write(f"内容：\n{para}\n")
                f.write("-" * 50 + "\n\n")
        return True
    except PermissionError:
        print(f"【错误】无权限写入文件：{output_path}")
        return False
    except Exception as e:
        print(f"【错误】写入段落文件 {output_path} 失败：{str(e)}")
        return False

def write_stats_report(stats_dict, file_path, report_path):
    """
    单独封装统计报告写入逻辑（升级任务核心要求），生成report.txt
    参数:
        stats_dict (dict): get_paragraph_stats返回的统计字典
        file_path (str): 原始MD文件路径
        report_path (str): 报告输出文件路径
    返回:
        bool: 写入成功True，失败False
    """
    try:
        output_dir = os.path.dirname(report_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        # f-string格式化输出报告，字段对齐更清晰
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("Markdown文件段落统计报告\n")
            f.write("=" * 60 + "\n")
            f.write(f"原始文件路径：{os.path.abspath(file_path)}\n")
            f.write(f"文件纯内容总字符数：{stats_dict['total_char']}\n")
            f.write(f"有效段落总数：{stats_dict['num_paras']}\n")
            f.write(f"最长段落字符数：{stats_dict['longest_len']}\n")
            f.write(f"最短段落字符数：{stats_dict['shortest_len']}\n")
            f.write(f"平均段落字符数：{stats_dict['avg_len']}\n")
            f.write("=" * 60 + "\n")
        return True
    except PermissionError:
        print(f"【错误】无权限写入报告：{report_path}")
        return False
    except Exception as e:
        print(f"【错误】写入统计报告 {report_path} 失败：{str(e)}")
        return False

def get_user_input(default_md, default_para, default_report):
    """
    获取用户自定义路径，回车使用默认值，做基础路径合法性提示（升级任务2）
    返回:
        tuple: (用户输入MD路径, 段落输出路径, 报告输出路径)
    """
    print("===== 请输入文件路径（直接回车使用默认值） =====")
    md_path = input(f"Markdown文件路径（默认：{default_md}）：").strip()
    para_path = input(f"段落输出路径（默认：{default_para}）：").strip()
    report_path = input(f"统计报告路径（默认：{default_report}）：").strip()
    # 回车使用默认值
    md_path = md_path if md_path else default_md
    para_path = para_path if para_path else default_para
    report_path = report_path if report_path else default_report
    # 基础路径提示（非绝对校验，避免提前拦截合法路径）
    if not md_path.endswith(".md"):
        print(f"【提示】输入的MD路径 {md_path} 非.md后缀，可能不是有效Markdown文件")
    return md_path, para_path, report_path

def process_single_md(md_path, para_output, report_output):
    """
    处理单个MD文件的完整流程：读取→拆分→统计→双文件写入
    作为批量处理的基础单元，解耦单文件/多文件逻辑
    参数:
        md_path (str): 单个MD文件路径
        para_output (str): 该文件的段落输出路径
        report_output (str): 该文件的统计报告路径
    返回:
        bool: 处理成功True，失败False
    """
    print(f"\n===== 开始处理文件：{md_path} =====")
    # 1. 读取文件
    raw_content = read_md_file(md_path)
    if raw_content is None:
        return False
    # 2. 拆分段落（处理空文件/全空白文件）
    paragraphs = split_paragraphs(raw_content)
    if not paragraphs:
        print(f"【提示】文件 {md_path} 无有效段落，跳过文件写入")
        return True
    # 3. 统计信息（纯封装无打印）
    stats = get_paragraph_stats(paragraphs, raw_content)
    # 4. 格式化输出统计信息（基础任务4）
    print(f"【统计结果】")
    print(f"├─ 有效段落数：{stats['num_paras']}")
    print(f"├─ 文件纯内容总字符：{stats['total_char']}")
    print(f"├─ 最长段落长度：{stats['longest_len']}")
    print(f"└─ 平均段落长度：{stats['avg_len']}")
    # 5. 写入段落文件+统计报告
    para_ok = write_formatted_paras(paragraphs, para_output)
    report_ok = write_stats_report(stats, md_path, report_output)
    if para_ok and report_ok:
        print(f"【成功】文件处理完成，结果已写入：")
        print(f"  - 段落文件：{os.path.abspath(para_output)}")
        print(f"  - 统计报告：{os.path.abspath(report_output)}")
        return True
    else:
        print(f"【失败】文件 {md_path} 处理不完整，部分文件未生成")
        return False

def batch_process_md(folder_path, output_root="output/batch"):
    """
    批量处理指定文件夹下的所有.md文件（升级任务5）
    自动为每个MD文件生成独立的para.txt和report.txt，按文件名区分
    参数:
        folder_path (str): MD文件所在文件夹路径
        output_root (str): 批量结果根目录
    返回:
        None
    """
    print(f"\n===== 开始批量处理文件夹：{folder_path} =====")
    # 遍历文件夹下所有.md文件（递归查找，支持子文件夹）
    md_files = glob.glob(os.path.join(folder_path, "**/*.md"), recursive=True)
    if not md_files:
        print(f"【错误】文件夹 {folder_path} 下未找到任何.md文件")
        return
    print(f"共找到 {len(md_files)} 个MD文件，开始逐个处理...")
    # 逐个处理每个MD文件
    for md_file in md_files:
        # 获取文件名（无后缀），用于区分输出文件
        file_name = os.path.splitext(os.path.basename(md_file))[0]
        # 为每个文件生成独立的输出路径
        para_out = os.path.join(output_root, f"{file_name}_paras.txt")
        report_out = os.path.join(output_root, f"{file_name}_report.txt")
        # 调用单文件处理逻辑
        process_single_md(md_file, para_out, report_out)
    print(f"\n===== 批量处理完成，所有结果已保存至：{os.path.abspath(output_root)} =====")

def main():
    """
    主程序：调度核心流程，支持「单文件自定义处理」和「批量处理」切换
    所有业务逻辑解耦到子函数，无堆叠代码
    """
    # 配置默认路径（可根据实际需求修改）
    DEFAULT_MD = r"D:\courseqa\data\md\example.md"
    DEFAULT_PARA = "output/paras.txt"
    DEFAULT_REPORT = "output/report.txt"
    BATCH_FOLDER = r"D:\courseqa\data\md"

    print("===== Python Markdown文件段落处理程序 =====")
    print("请选择处理模式：")
    print("1 - 单文件处理（支持用户自定义路径）")
    print("2 - 批量处理（处理data/md下所有.md文件）")
    choice = input("输入模式编号（1/2，默认1）：").strip() or "1"

    if choice == "1":
        # 单文件处理：获取用户输入→执行处理
        md_path, para_path, report_path = get_user_input(DEFAULT_MD, DEFAULT_PARA, DEFAULT_REPORT)
        process_single_md(md_path, para_path, report_path)
    elif choice == "2":
        # 批量处理：直接调用批量函数
        batch_process_md(BATCH_FOLDER)
    else:
        print("【错误】无效的模式编号，默认执行单文件处理")
        process_single_md(DEFAULT_MD, DEFAULT_PARA, DEFAULT_REPORT)

if __name__ == '__main__':
    main()