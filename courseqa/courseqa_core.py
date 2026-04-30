import os
import glob
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

def read_md_file(file_path):
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
    if not text or text.strip() == "":
        return []
    raw_paragraphs = text.split("\n\n")
    paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
    return paragraphs

def get_paragraph_stats(paragraphs, raw_content):
    num_paragraphs = len(paragraphs)
    longest_length = max((len(p) for p in paragraphs), default=0)
    shortest_length = min((len(p) for p in paragraphs), default=0)
    total_char = len(raw_content.replace("\n", "").replace(" ", ""))
    avg_length = round(total_char / num_paragraphs, 2) if num_paragraphs > 0 else 0
    return {
        "num_paras": num_paragraphs,
        "longest_len": longest_length,
        "shortest_len": shortest_length,
        "total_char": total_char,
        "avg_len": avg_length
    }

def write_formatted_paras(paragraphs, output_path):
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
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
    try:
        output_dir = os.path.dirname(report_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
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
        print(f"【错误】写入报告：{report_path} 失败")
        return False
    except Exception as e:
        print(f"【错误】写入报告失败：{e}")
        return False

def build_chunks(doc_name, paragraphs):
    chunks = []
    for pid, text in enumerate(paragraphs, start=1):
        chunk = {
            "doc": doc_name,
            "pid": pid,
            "text": text
        }
        chunks.append(chunk)
    return chunks

def write_chunks_jsonl(chunks, jsonl_path):
    try:
        output_dir = os.path.dirname(jsonl_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                line = json.dumps(chunk, ensure_ascii=False)
                f.write(line + "\n")
        return True
    except Exception as e:
        print(f"【写入jsonl失败】{e}")
        return False

def read_chunks_jsonl(jsonl_path):
    chunks = []
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    chunk = json.loads(line)
                    chunks.append(chunk)
        return chunks
    except Exception as e:
        print(f"【读取jsonl失败】{e}")
        return []

def build_chunks_with_fields(doc_name, paragraphs):
    chunks = []
    for pid, text in enumerate(paragraphs, start=1):
        chunk = {
            "id": f"{doc_name}_{pid}",
            "doc": doc_name,
            "pid": pid,
            "text": text,
            "char_length": len(text),
            "doc_id": doc_name.split(".")[0]
        }
        chunks.append(chunk)
    return chunks

def write_chunks_json(chunks, json_path):
    try:
        output_dir = os.path.dirname(json_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"【写入普通json失败】{e}")
        return False

def merge_all_chunks(md_folder, output_jsonl="output/all_chunks.jsonl"):
    all_chunks = []
    md_files = glob.glob(os.path.join(md_folder, "**/*.md"), recursive=True)
    for file in md_files:
        content = read_md_file(file)
        if not content:
            continue
        paras = split_paragraphs(content)
        doc_name = os.path.basename(file)
        chunks = build_chunks_with_fields(doc_name, paras)
        all_chunks.extend(chunks)

    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"[合并完成] 共 {len(all_chunks)} 个chunk → {output_jsonl}")
    return all_chunks

def print_chunk_summary(chunks):
    print("\n===== Chunk 摘要信息 =====")
    print(f"总条目数：{len(chunks)}")
    if chunks:
        docs = list(set([c["doc"] for c in chunks]))
        print(f"文档数量：{len(docs)}")
        print(f"文档列表：{docs}")
        print(f"单条结构示例：")
        print(json.dumps(chunks[0], ensure_ascii=False, indent=2))
    print("=========================\n")

def get_user_input(default_md, default_para, default_report):
    print("===== 路径设置（回车默认） =====")
    md_path = input(f"MD路径：").strip() or default_md
    para_path = input(f"段落输出：").strip() or default_para
    report_path = input(f"报告路径：").strip() or default_report
    return md_path, para_path, report_path

def process_single_md(md_path, para_output, report_output):
    print(f"\n===== 处理文件：{md_path} =====")
    raw_content = read_md_file(md_path)
    if raw_content is None:
        return False

    paragraphs = split_paragraphs(raw_content)
    if not paragraphs:
        print("无有效段落")
        return True

    stats = get_paragraph_stats(paragraphs, raw_content)
    print(f"有效段落：{stats['num_paras']} | 总字符：{stats['total_char']}")

    doc_name = os.path.basename(md_path)
    
    chunks = build_chunks_with_fields(doc_name, paragraphs)
    
    write_formatted_paras(paragraphs, para_output)
    write_stats_report(stats, md_path, report_output)
    write_chunks_jsonl(chunks, "output/chunks.jsonl")
    write_chunks_json(chunks, "output/chunks.json")

    print_chunk_summary(chunks)
    print("[单文件处理完成] output/ 下已生成 jsonl + json")

def batch_process_md(folder_path="data/md"):
    print("\n===== 批量处理 + 全部合并 =====")
    merge_all_chunks(folder_path)
    print("[批量处理完成] all_chunks.jsonl 已生成")

def search_count(query,chunks,top_k=5):
    query = query.strip()
    if not query:
        print("查询不可为空！")
        return []
    
    if(top_k <=0):
        top_k = 5

    results = []
    for chunk in chunks:
        text = chunk['text']
        score = text.lower().count(query.lower())
        if score>0:
            results.append({
                'score': score,
                'doc' : chunk['doc'],
                'pid' : chunk['pid'],
                'text': chunk['text']
            })
    results.sort(key = lambda x:x['score'],reverse = True)
    return results[:top_k]

def print_search_results(results):
    if not results:
        print("⚠️ 未找到任何匹配结果")
        return
    for i, item in enumerate(results, start=1):
        print(f"[Top{i}] 分数:{item['score']:.4f} | 来源:{item['doc']} 第{item['pid']}段")
        print("内容：" + item['text'][:50] + "...")
        print('-'*60)

def search_count_multiple_docs(query,md_folder,top_k=5):
    all_chunks = []
    md_files = glob.glob(os.path.join(md_folder, "**/*.md"), recursive=True)
    for file in md_files:
        content = read_md_file(file)
        if not content:
            continue
        paras = split_paragraphs(content)
        doc_name = os.path.basename(file)
        chunks = build_chunks_with_fields(doc_name, paras)
        all_chunks.extend(chunks)
    return search_count(query, all_chunks, top_k)

def build_tfidf(texts):
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 1),
        max_features=1000,
        token_pattern=r"(?u)\b\w+\b"
    )
    text_vectors = vectorizer.fit_transform(texts)
    return vectorizer, text_vectors

def search_tfidf(query,vectorizer,text_vectors,chunks,top_k=5):
    query = query.strip()
    if not query:
        print("查询不可为空！")
        return []
    
    if top_k <=0:
        top_k = 5

    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, text_vectors)[0]

    results = []
    for i, score in enumerate(similarities):
        result = {
            "score": float(score),
            "doc": chunks[i]["doc"],
            "pid": chunks[i]["pid"],
            "text": chunks[i]["text"]
        }
        results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def build_bm25(chunks):
    """
    构建BM25模型（对中文按字分词，简单可用）
    """
    texts = [chunk["text"] for chunk in chunks]
    tokenized_texts = [list(text) for text in texts]  # 按字分词
    bm25 = BM25Okapi(tokenized_texts)
    return bm25

def search_bm25(query, bm25_model, chunks, top_k=5):   
    query = query.strip()
    if not query:
        print("查询不可为空！")
        return[]
    #查询也按字拆分
    tokenized_query = list(query)
    scores = bm25_model.get_scores(tokenized_query)
    results = []
    for i,score in enumerate(scores):
        if score>0:
            results.append({
                "score": round(float(score), 4),
                "doc": chunks[i]["doc"],
                "pid": chunks[i]["pid"],
                "text": chunks[i]["text"]
            })
        
    results.sort(key = lambda x:x["score"],reverse = True)
    return results[:top_k]

def shorten_text(text, max_chars=200):
    """
    将文本截断为前 max_chars 个字符，超出部分加省略号。
    """
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."

if __name__ == "__main__":
    print("===== CourseQA Core 测试 =====")
    print("\n===== 测试完成 =====")
    