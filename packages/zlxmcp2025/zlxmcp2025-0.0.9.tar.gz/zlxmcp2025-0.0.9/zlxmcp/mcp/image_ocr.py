
from fastmcp import FastMCP
import requests, json, base64, os
from typing import Annotated,Union, Literal
from pydantic import Field
from zlxmcp.utils.oss import OSS
from zlxmcp.utils.utils import project_cache_dir
import click

__all__ = [
    "request_upload_slot",
    "generate_data_summary",
]

mcp = FastMCP("ZLX-MCP")

# LLM API configuration
LLM_API_URL = os.getenv("ZLXMCP_IMAGE_OCR_LLM_URL")
LLM_API_KEY = os.getenv("ZLXMCP_IMAGE_OCR_LLM_API_KEY")
LLM_MODEL   = "Qwen/Qwen2.5-VL-72B-Instruct"
PROMPT_TEXT = (
    "下图是一张表格截图，请按以下格式返回 markdown 摘要：\n"
    "1) 表头列表\n2) 行数与列数\n3) 对所有数值列给出均值、最小、最大\n4) 对现有的数据进行分析，给出文字总结\n"
)

FILE_METHOD = os.getenv("FILE_METHOD", "local")
if FILE_METHOD == "oss":
    oss_key = os.getenv("OSS_KEY")
    assert oss_key, "请设置环境变量 OSS_KEY"
    oss = OSS(
        access_key_id=oss_key.split("-")[0],
        access_key_secret=oss_key.split("-")[1],
        bucket_name="-".join(oss_key.split("-")[2:]),
    )


def _download_oss_object(key: str) -> bytes:
    if FILE_METHOD == "oss":
        return oss.download_file(object_name=key)
    # 本地：把 object_key 当作相对路径挂到缓存目录
    local_path = os.path.join(project_cache_dir(), key)  # key = "zlxmcp/data/chart.png"
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"{local_path} 不存在，请先在本地放好测试文件")
    return open(local_path, "rb").read()



def _call_llm_for_summary(img_bytes: bytes) -> str:
    """Call Qwen2.5‑VL with prompt+image and return summary text."""
    img_b64 = base64.b64encode(img_bytes).decode()
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT_TEXT},
                    {"type": "image", "image": img_b64},
                ],
            }
        ],
        "stream": False,
    }
    resp = requests.post(LLM_API_URL, headers=headers, data=json.dumps(payload))
    if resp.status_code != 200:
        raise RuntimeError(f"LLM request failed: {resp.status_code} {resp.text}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def _upload_and_sign_text(text: str, remote_key: str, ttl: int = 3600) -> str:
    """Upload text to OSS and return signed GET URL (or local path)."""
    if FILE_METHOD != "oss":
        local_path = os.path.join(project_cache_dir(), "summary", os.path.basename(remote_key))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(text)
        return f"saved locally at {local_path}"

    oss.put_file(object_name=remote_key, data=text.encode("utf-8"))
    _, url = oss.sign_url(key=remote_key, expires=ttl)
    return url


@mcp.tool()
def request_upload_slot(
    file_name: Annotated[str, Field(description="原始 PNG 文件名，含扩展名 (例如 chart.png)")]
) -> dict:
    """Generate a 10‑minute signed PUT URL so the client can upload the PNG directly to OSS."""
    if FILE_METHOD != "oss":
        raise RuntimeError("FILE_METHOD 必须为 oss 才能使用此接口")
    object_key = f"zlxmcp/data/{file_name}"
    _, put_url = oss.sign_url(key=object_key, expires=600, method="PUT")
    return {"object_key": object_key, "upload_url": put_url}


@mcp.tool()
def generate_data_summary(
    object_key: Annotated[str, Field(description="上传好的 OSS object_key (PNG)")],
    summary_name: Annotated[str, Field(description="生成的 summary 文件名，不含扩展名")]
) -> str:
    """Download PNG → LLM summary → upload .md → return download link."""
    img_bytes = _download_oss_object(object_key)
    summary_text = _call_llm_for_summary(img_bytes)
    remote_key = f"zlxmcp/summary/{summary_name}.md"
    return _upload_and_sign_text(summary_text, remote_key)



@click.command()
@click.option("--host", "-h", default="127.0.0.1", type=str, required=False, help="host")
@click.option("--port", "-p", default=8000, type=int, required=False, help="port")
@click.option("--transport", "-t", default="stdio", type=str, required=False, help="transport")
def image_ocr_mcp_server(
        host: str = None,
        port: Union[int, str] = None,
        transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
) -> None:
    """"""
    if transport == "sse":
        mcp.run(transport=transport, port=port, host=host)
    else:
        mcp.run(transport=transport)


if __name__ == "__main__":
    mcp.run(transport="sse", port=9005)