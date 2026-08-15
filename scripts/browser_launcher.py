"""Edge 浏览器自动检测与启动工具

核心功能：自动检测 Edge 是否已运行且 CDP 可用，若未运行则自动启动。

三种场景：
1. ✅ Edge 已运行 + CDP 已开启 → 直接连接（当前方式）
2. ✅ Edge 未运行 → 自动启动并开启 CDP（使用默认 profile，保留登录态）
3. ⚠️ Edge 已运行但 CDP 未开启 → 无法通过 CDP 连接，回退到 Extension 模式

用法：
    from browser_automation.scripts.browser_launcher import ensure_edge, get_edge_ws_url

    ws_url = get_edge_ws_url()  # 自动处理检测和启动
    # 然后用 ws_url 连接 CDP
"""
import os
import time
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── 路径常量 ──
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
DEVTOOLS_PORT_FILE = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\Edge\User Data\DevToolsActivePort"
)
DEFAULT_USER_DATA_DIR = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\Edge\User Data"
)
CDP_PORT = 9222
MAX_WAIT_SECONDS = 30


def is_edge_running() -> bool:
    """检查 Edge 进程是否在运行"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq msedge.exe", "/NH"],
            capture_output=True, text=True, timeout=5
        )
        # 输出中包含 msedge.exe 行数即进程数
        lines = [l for l in result.stdout.splitlines() if "msedge.exe" in l]
        return len(lines) > 0
    except Exception:
        return False


def is_cdp_available() -> bool:
    """检查 Edge 的 CDP 端口是否可用（DevToolsActivePort 文件有效）"""
    if not os.path.exists(DEVTOOLS_PORT_FILE):
        return False
    try:
        with open(DEVTOOLS_PORT_FILE) as f:
            lines = f.read().strip().splitlines()
        return len(lines) >= 2 and lines[0].strip().isdigit() and lines[1].strip().startswith("/")
    except Exception:
        return False


def get_edge_ws_url() -> str:
    """从 DevToolsActivePort 读取 WebSocket URL"""
    with open(DEVTOOLS_PORT_FILE) as f:
        lines = f.read().strip().splitlines()
        port = lines[0].strip()
        ws_path = lines[1].strip()
    return f"ws://127.0.0.1:{port}{ws_path}"


def launch_edge_with_cdp() -> bool:
    """启动 Edge 并开启远程调试（使用默认 profile，保留全部登录态）

    启动策略：
    - 使用默认 User Data 目录 → 保留所有 Cookie、历史记录、扩展、设置
    - 指定 `--remote-debugging-port=9222` → 开启 CDP
    - 打开 `about:blank` → 不干扰用户（不自动加载任何页面）
    - 使用 `--no-first-run` → 跳过首次运行向导
    - 使用 `--new-window` → 在新窗口中打开

    Returns:
        True 表示启动成功，False 表示失败
    """
    if not os.path.exists(EDGE_PATH):
        logger.error(f"Edge 未找到: {EDGE_PATH}")
        return False

    try:
        subprocess.Popen(
            [
                EDGE_PATH,
                f"--user-data-dir={DEFAULT_USER_DATA_DIR}",
                f"--remote-debugging-port={CDP_PORT}",
                "--no-first-run",
                "--new-window",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        logger.info("Edge 已启动（默认 profile，CDP 端口 9222）")
        return True
    except Exception as e:
        logger.error(f"启动 Edge 失败: {e}")
        return False


def ensure_edge() -> str:
    """确保 Edge 可连接，返回 WebSocket URL

    自动决策树：
    1. CDP 可用 → 直接返回 WebSocket URL
    2. Edge 未运行 → 自动启动 Edge + CDP → 等待就绪 → 返回 WebSocket URL
    3. Edge 运行但 CDP 不可用 → 抛出异常，建议使用 Extension 模式

    Returns:
        WebSocket URL (如 ws://127.0.0.1:9222/devtools/browser/xxxx)

    Raises:
        RuntimeError: 无法连接或启动 Edge
    """
    # 情况 1: CDP 已经可用
    if is_cdp_available():
        ws_url = get_edge_ws_url()
        logger.info(f"Edge CDP 已就绪: {ws_url}")
        return ws_url

    # 情况 2: Edge 未运行，启动它
    if not is_edge_running():
        logger.info("Edge 未运行，正在自动启动...")
        if not launch_edge_with_cdp():
            raise RuntimeError("无法启动 Edge 浏览器")

        # 等待 DevToolsActivePort 出现
        for i in range(MAX_WAIT_SECONDS):
            time.sleep(1)
            if is_cdp_available():
                ws_url = get_edge_ws_url()
                logger.info(f"Edge 已启动并就绪: {ws_url}")
                return ws_url

        raise RuntimeError(
            f"Edge 启动后 {MAX_WAIT_SECONDS} 秒内 CDP 未就绪，请检查 Edge 安装"
        )

    # 情况 3: Edge 运行但 CDP 不可用
    raise RuntimeError(
        "Edge 已运行但未开启远程调试。\n"
        "请使用以下方式之一：\n"
        "1. 关闭所有 Edge 窗口后重试（会自动以 CDP 模式启动）\n"
        "2. 使用 playwright-mcp --extension 模式（无需 CDP）"
    )


# ── 快捷入口 ──
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        url = ensure_edge()
        print(f"✅ WebSocket URL: {url}")
    except RuntimeError as e:
        print(f"❌ {e}")