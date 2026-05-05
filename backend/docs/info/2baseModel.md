在 FastAPI 中，BaseModel（来自 Pydantic 库）是定义数据结构的核心。你可以把它看作是一个自带“说明书”和“自动检查员”的 Python 类。
以你的 AppConfig 为例，BaseModel 提供了以下四个核心功能：
## 1. 数据校验 (Validation)
当你加载配置文件时，BaseModel 会自动检查内容是否符合你定义的类型。

* 如果 log_level 应该是 str 但配置文件里写成了数字 123，Pydantic 会自动尝试将其转换为字符串 "123"。
* 如果无法转换（比如 TokenUsageConfig 需要特定格式但数据对不上），它会直接报错，防止程序带着错误的配置运行。

## 2. 默认值处理 (Default Values)

* 简单默认值: log_level: str = Field(default="info")。如果配置文件里没写这一项，程序会自动赋予它 "info"。
* 复杂对象初始化: default_factory=TokenUsageConfig。这是一个非常专业的写法。因为 TokenUsageConfig 是个类，不能直接写 default=TokenUsageConfig()（这会导致所有实例共享同一个对象）。使用 default_factory 确保每次创建一个新的 AppConfig 时，都会独立生成一个新的 TokenUsageConfig 实例。

## 3. 文档与元数据 (Metadata)

* Field(description="..."): 这些描述不仅是注释，它们会被 FastAPI 自动提取，展示在 /docs (Swagger UI) 界面中。
* 这让其他开发者（或未来的你）一眼就能看出 log_level 到底是干什么用的，以及支持哪些值（如 debug/info）。

## 4. 嵌套结构映射 (Nested Mapping)
BaseModel 最强大的地方在于处理像 TokenUsageConfig 这样的嵌套对象。
假设你的 config.yaml 是这样的：

log_level: "debug"token_usage:
  enabled: true
  limit: 1000

当你执行 AppConfig(**yaml_data) 时，Pydantic 会自动：

   1. 把顶层的 log_level 填好。
   2. 识别出 token_usage 应该对应 TokenUsageConfig 类。
   3. 自动实例化 TokenUsageConfig 并把对应的子项填进去。

------------------------------
## 如何在代码中结合使用？
你可以这样将之前的路径查找逻辑与这个模型结合：

def get_config() -> AppConfig:
    # 假设 candidate_path 是你之前函数找到的路径
    with open(candidate_path, "r") as f:
        data = yaml.safe_load(f)
    
    # 将字典转换为 AppConfig 对象，此时会自动进行校验
    return AppConfig(**data)
# 现在你可以通过点语法安全地访问配置config = get_config()
print(config.log_level) 
print(config.token_usage.limit) # 自动补全和类型提示非常爽

你需要我演示如何将这个 AppConfig 注入到 FastAPI 的路由依赖中，以便在 API 接口里直接调用配置吗？

