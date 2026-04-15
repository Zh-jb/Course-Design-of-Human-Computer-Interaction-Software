import os
from courseqa_core import(read_md_file,split_paragraphs,build_chunks_with_fields,process_single_md,batch_process_md,search_count,print_search_results,search_count_multiple_docs,build_tfidf,search_tfidf,build_bm25,search_bm25)

def get_valid_integer_input(prompt, default, min_val=1):
    """通用整数输入验证函数"""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:  # 空输入使用默认值
                return default
            val = int(user_input)
            if val < min_val:
                print(f"输入值需大于等于{min_val}，将使用默认值 {default}")
                return default
            return val
        except ValueError:
            print(f"输入不是有效整数，将使用默认值 {default}")
            return default

def main():
    DEFAULT_MD = "data/md/example.md"
    DEFAULT_PARA = "output/paras.txt"
    DEFAULT_REPORT = "output/report.txt"
    
    # 交互式设置top_k和preview_chars
    print("===== 参数设置 =====")
    top_k = get_valid_integer_input(f"请输入返回结果数量top_k（默认5）：", 5, 1)
    preview_chars = get_valid_integer_input(f"请输入预览字符数preview_chars（默认50）：", 50, 1)
    print("="*50 + "\n")

    print("===== MD分块导出工具 =====")
    print("1 - 单文件处理（输出jsonl + json）")
    print("2 - 批量处理 + 合并所有文件为一个jsonl")
    print("3 - 查询关键字-在example.md中查找并输出top{}结果".format(top_k))
    print("4 - 在指定路径下多文档中查询关键字并输出top{}结果".format(top_k))
    print("5 - 比较不同检索方法的查询结果".format(top_k))
    print("6 - 退出程序")
    choice = input("请选择（1/2/3/4/5/6，默认1）：").strip() or "1"

    if choice == "1":
        md_path, para_path, report_path = get_user_input(DEFAULT_MD, DEFAULT_PARA, DEFAULT_REPORT)
        process_single_md(md_path, para_path, report_path)
    elif choice == "2":
        batch_process_md()
    elif choice == "3":
        query = input("请输入查询关键字：").strip()
        if not query:
            print("查询关键字不可为空！")
            return
        chunks = build_chunks_with_fields(os.path.basename(DEFAULT_MD), split_paragraphs(read_md_file(DEFAULT_MD)))
        results = search_count(query, chunks, top_k)
        # 重写打印函数，使用自定义preview_chars
        print_search_results_custom(results, preview_chars)
        while True:
            user_input = input("新关键词（exit退出）：").strip()
            if user_input.lower() == "exit":
                print("结束查询")
                break
            results = search_count(user_input, chunks, top_k)
            print_search_results_custom(results, preview_chars)
    elif choice == "4":
        md_folder = input("MD文件夹（默认data/md）：").strip() or "data/md"
        query = input("查询关键词：").strip()
        if not query:
            print("关键词不能为空")
            return
        results = search_count_multiple_docs(query, md_folder, top_k)
        print_search_results_custom(results, preview_chars)
    elif choice == "5":
        query = input("请输入查询关键字：").strip()
        if not query:
            print("不能为空！")
            return

        # 让用户选择查看方式
        print("\n===== 选择查看方式 =====")
        view_choice = input("请选择查看方式（count/tfidf/both，默认both）：").strip().lower() or "both"
        while view_choice not in ["count", "tfidf", "both"]:
            print("输入错误！仅支持 count/tfidf/both")
            view_choice = input("请重新选择（count/tfidf/both，默认both）：").strip().lower() or "both"

        content = read_md_file(DEFAULT_MD)
        paras = split_paragraphs(content)
        doc_name = os.path.basename(DEFAULT_MD)
        chunks = build_chunks_with_fields(doc_name, paras)

        # 根据选择展示结果
        if view_choice in ["count", "both"]:
            print("\n===== COUNT 检索结果 =====")
            res_count = search_count(query, chunks, top_k)
            print_search_results_custom(res_count, preview_chars)

        if view_choice in ["tfidf", "both"]:
            print("\n===== TF-IDF 检索结果 =====")
            texts = [c["text"] for c in chunks]
            vectorizer, text_vectors = build_tfidf(texts)
            res_tfidf = search_tfidf(query, vectorizer, text_vectors, chunks, top_k)
            print_search_results_custom(res_tfidf, preview_chars)

        if view_choice == "both":  # both时额外展示BM25
            print("\n===== BM25 方法检索结果 =====")
            bm25_model = build_bm25(chunks)
            res_bm25 = search_bm25(query, bm25_model, chunks, top_k)
            print_search_results_custom(res_bm25, preview_chars)

    elif choice == "6":
        print("退出程序")
        return
    else:
        print("输入错误，使用默认单文件处理")
        process_single_md(DEFAULT_MD, DEFAULT_PARA, DEFAULT_REPORT)

def print_search_results_custom(results, preview_chars):
    """自定义预览字符数的结果打印函数"""
    if not results:
        print("⚠️ 未找到任何匹配结果")
        return
    for i, item in enumerate(results, start=1):
        print(f"[Top{i}] 分数:{item['score']:.4f} | 来源:{item['doc']} 第{item['pid']}段")
        preview_text = item['text'][:preview_chars] + ("..." if len(item['text']) > preview_chars else "")
        print("内容：" + preview_text)
        print('-'*60)

def get_user_input(default_md, default_para, default_report):
    print("===== 路径设置（回车默认） =====")
    md_path = input(f"MD路径：").strip() or default_md
    para_path = input(f"段落输出：").strip() or default_para
    report_path = input(f"报告路径：").strip() or default_report
    return md_path, para_path, report_path

if __name__ == '__main__':
    os.makedirs("data/md", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    main()