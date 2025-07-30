from pydantic import BaseModel
from typing import Optional, Any, List, Dict

# Pydantic模型是FastAPI用于数据验证和文档生成的关键部分

class DocumentPatch(BaseModel):
    """
    定义了对文档单个元素进行修改的指令结构。
    这个模型将被用于 /apply-changes/ 端点，以列表形式接收批量修改。
    """
    # 元素的唯一标识符，在提取阶段生成
    element_id: str
    
    # 新的内容，可以是简单的字符串，也可以是更复杂的结构（例如，对于表格单元格）
    new_content: Any

    class Config:
        # Pydantic的配置类
        # str_strip_whitespace = True: 自动去除字符串两端的空白字符
        # from_attributes = True: 允许模型从对象的属性中读取数据
        str_strip_whitespace = True
        from_attributes = True 