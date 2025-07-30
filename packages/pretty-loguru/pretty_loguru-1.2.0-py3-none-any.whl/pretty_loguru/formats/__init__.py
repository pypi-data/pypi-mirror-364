# 在 pretty_loguru/formats/__init__.py 中集中處理 FIGlet 檢查:

"""
格式化模組入口

此模組提供 Pretty Loguru 的所有格式化功能，包括區塊格式化、
ASCII 藝術和 FIGlet 文本等。這些功能豐富了日誌的視覺呈現效果。
"""
import sys

# 導入區塊格式化功能
from .block import (
    print_block,
    format_block_message,
    create_block_method,
)

# 導入 ASCII 藝術功能
from .ascii_art import (
    print_ascii_header,
    print_ascii_block,
    create_ascii_methods,
)

# 導入 ASCII 驗證功能
from ..utils.validators import is_ascii_only

# 導入 Rich 組件功能
from .rich_components import (
    print_table,
    print_tree,
    print_columns,
    LoggerProgress,
    create_rich_methods,
)

# 檢查 pyfiglet 是否可用 - 使用更安全的導入方式
_has_figlet = False
try:
    # 嘗試導入 pyfiglet
    import pyfiglet
    _has_figlet = True
except ImportError:
    _has_figlet = False
    # print("Warning: pyfiglet not available. FIGlet features disabled.", file=sys.stderr)
    pass

# 如果 pyfiglet 可用，導入 FIGlet 功能
if _has_figlet:
    try:
        from .figlet import (
            print_figlet_header,
            print_figlet_block,
            get_figlet_fonts,
            create_figlet_methods,
        )
    except Exception as e:
        _has_figlet = False
        print(f"Warning: Failed to initialize FIGlet features: {str(e)}", file=sys.stderr)

# 定義對外可見的功能
__all__ = [
    # 區塊格式化
    "print_block",
    "format_block_message",
    "create_block_method",
    
    # ASCII 藝術
    "print_ascii_header",
    "print_ascii_block",
    "is_ascii_only",
    "create_ascii_methods",
    
    # Rich 組件
    "print_table",
    "print_tree", 
    "print_columns",
    "LoggerProgress",
    "create_rich_methods",
]

# 如果 FIGlet 可用，則添加相關功能
if _has_figlet:
    __all__.extend([
        "print_figlet_header",
        "print_figlet_block",
        "get_figlet_fonts",
        "create_figlet_methods",
    ])

# 提供檢查 FIGlet 是否可用的函數
def has_figlet() -> bool:
    """
    檢查 FIGlet 功能是否可用
    
    Returns:
        bool: 如果 FIGlet 功能可用則返回 True，否則返回 False
    """
    return _has_figlet