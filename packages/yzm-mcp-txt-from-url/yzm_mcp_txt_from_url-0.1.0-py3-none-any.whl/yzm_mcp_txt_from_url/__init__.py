from mcp.server.fastmcp import FastMCP
import requests
from io import StringIO
import os

# 创建MCP服务
mcp = FastMCP("TextFileReaderService")

@mcp.tool()
def read_text_file_from_url(url: str) -> str:
    """
    下载TXT文件并返回其内容。
    :param url: TXT文件的临时下载链接
    :return: 文件中的文本内容
    """
    try:
        # 发送GET请求下载文件
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功

        # 使用StringIO来读取文本内容
        text_io = StringIO(response.text)
        content = text_io.read()

        return content
    except requests.RequestException as e:
        return f"Error downloading file: {e}"
    except Exception as e:
        return f"Error reading file: {e}"



def main() -> None:
    mcp.run(transport='stdio')
