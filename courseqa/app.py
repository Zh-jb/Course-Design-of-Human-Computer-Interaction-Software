from  fastapi import FastAPI, HTTPException
from datetime import datetime
import os
# ===================== 修改位置1：新增必要导入 =====================
from typing import List, Optional
# ================================================================

from courseqa_core import(
    read_md_file,
    split_paragraphs,
    build_chunks_with_fields,
    merge_all_chunks,
    process_single_md,
    batch_process_md,
    search_count,
    print_search_results,
    search_count_multiple_docs,
    build_tfidf,
    search_tfidf,
    build_bm25,
    search_bm25,
    shorten_text
)
from pydantic import BaseModel

app = FastAPI(
    title = "courseqa API",
    description = "此为第九次课程作业，实现离线检索接入API,演示GET查询、POST查询和POST创建文档",
    version = "1.0.0"
)

chunks = []
tfidf_vectorizer = None
tfidf_matrix = None

# ===================== 修改位置2：QueryRequest 增加 min_score =====================
class QueryRequest(BaseModel):
    query:str
    top_k:int = 5
    min_score: float = 0.0  # 新增：最小相似度过滤
# ==================================================================================

class DocumentRequest(BaseModel):
    filename:str
    content:str

# ===================== 修改位置3：DocumentRequest 批量上传用 =====================
class DocumentBatchRequest(BaseModel):
    docs: List[DocumentRequest]
# ================================================================================

# ===================== 修改位置4：安全文件名函数（防路径穿越） =====================
def safe_filename(filename: str) -> str:
    bad_chars = ["..", "/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
    for c in bad_chars:
        filename = filename.replace(c, "")
    filename = os.path.basename(filename)
    if not filename.endswith(".md"):
        filename += ".md"
    return filename
# ==================================================================================

def load_index():
    global chunks, tfidf_vectorizer, tfidf_matrix
    md_dir = "./data/md"
    all_chunks = []

    # ===================== 修改位置5：修复 merge_all_chunks 参数 =====================
    # 原代码：
    # chunks= merge_all_chunks(md_folder="data/md", output_jsonl="output/all_chunks.jsonl")
    # 修改为（你之前报错就是这里参数名不对）：
    chunks = merge_all_chunks(md_folder="data/md", output_jsonl="output/all_chunks.jsonl")
    # ================================================================================

    if not chunks:
        print("提示：没有加载到任何 chunk，索引未构建。")
        tfidf_vectorizer = None
        tfidf_matrix = None
        return
    
    texts = [chunk["text"] for chunk in chunks]
    tfidf_vectorizer, tfidf_matrix = build_tfidf(texts)

    print(f"索引加载完成，共加载 {len(chunks)} 个 chunk。")

# ===================== 修改位置6：run_search 增加 min_score 过滤 =====================
def run_search(query_text: str, top_k: int, min_score: float = 0.0):
    if tfidf_matrix is None or tfidf_vectorizer is None:
        raise HTTPException(status_code=500, detail="索引未加载")
    query_text = query_text.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="查询词不能为空")
    if top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k 必须大于0")

    results = search_tfidf(
        query=query_text,
        vectorizer=tfidf_vectorizer,
        text_vectors=tfidf_matrix,
        chunks=chunks,
        top_k=top_k
    )

    # 新增：最小分数过滤
    filtered = []
    for item in results:
        if item["score"] >= min_score:
            filtered.append(item)

    hits = []
    for item in filtered:
        preview_text = shorten_text(item["text"], max_chars=200)
        hit = {
            "score": item["score"],
            "doc": item["doc"],
            "pid": item["pid"],
            "text": preview_text
        }
        hits.append(hit)

    return {
        "query": query_text,
        "top_k": top_k,
        "min_score": min_score,  # 返回过滤阈值
        "hit_count": len(hits),
        "hits": hits
    }
# ====================================================================================

@app.get("/")
def root():
    return {"message": "欢迎访问Courseqa课程网页"}

@app.get("/get")
def get():
    return {
        "项目名称":"智慧课程问答系统Courseqa",
        "项目第一阶段":"完成API的基础调用",
    }

@app.get("/health")
def health():
    index_loaded = tfidf_matrix is not None
    return {
        "ok": True,
        "message": "服务正常运行",
        "index_loaded": index_loaded,
        "chunk_count": len(chunks)
    }

@app.get("/info")
def info():
    return {
        "project": "courseqa",
        "lesson": "第8次课",
        "status": "running"
    }

@app.get("/time")
def time():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": now}

@app.get("/hello")
def hello(name:str):
    return {"Hello!":name}

@app.get("/add")
def add(a:int,b:int):
    return {f"{a}+{b}=": a+b}

# ===================== 修改位置7：GET /query 增加 min_score =====================
@app.get("/query")
def get_query(query:str, top_k:int=5, min_score: float=0.0):
    return run_search(query_text=query, top_k=top_k, min_score=min_score)
# ===============================================================================

# ===================== 修改位置8：POST /query 自动读取 min_score =====================
@app.post("/query")
def post_query(query_request: QueryRequest):
    return run_search(
        query_text=query_request.query,
        top_k=query_request.top_k,
        min_score=query_request.min_score
    )
# ===================================================================================

@app.post("/document")
def add_document(doc_request:DocumentRequest):
    # ===================== 修改位置9：安全文件名 + 防覆盖 =====================
    filename = safe_filename(doc_request.filename)
    file_path = os.path.join("./data/md", filename)
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"文件 {filename} 已存在，禁止覆盖")
    
    content = doc_request.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="文档内容不能为空")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    load_index()

    return {
        "ok": True,
        "message": "文档已保存，索引已更新",
        "filename": filename,
        "path": file_path,
        "chunk_count": len(chunks)
    }

# ===================== 修改位置10：批量上传文档 =====================
@app.post("/documents")
def batch_add_docs(batch_req: DocumentBatchRequest):
    saved = []
    total_chunks_before = len(chunks)
    for doc in batch_req.docs:
        safe_name = safe_filename(doc.filename)
        path = os.path.join("./data/md", safe_name)
        if os.path.exists(path):
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc.content.strip())
        saved.append(safe_name)
    load_index()
    return {
        "saved_files": saved,
        "total_added": len(chunks) - total_chunks_before,
        "total_chunks": len(chunks)
    }
# ====================================================================

# ===================== 修改位置11：PUT 更新文档 =====================
@app.put("/documents/{filename}")
def update_document(filename: str, content: str):
    safe_name = safe_filename(filename)
    path = os.path.join("./data/md", safe_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="文件不存在")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    load_index()
    return {"ok": True, "message": "更新成功", "file": safe_name, "chunk_count": len(chunks)}
# ==================================================================

# ===================== 修改位置12：DELETE 删除文档 =====================
@app.delete("/documents/{filename}")
def delete_document(filename: str):
    safe_name = safe_filename(filename)
    path = os.path.join("./data/md", safe_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="文件不存在")
    os.remove(path)
    load_index()
    return {"ok": True, "message": "删除成功", "file": safe_name, "remaining_chunks": len(chunks)}
# ======================================================================

load_index()