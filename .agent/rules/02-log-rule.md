---
trigger: always_on
---

# 日志规范 (Logging Rules)

## 1. 核心原则：为机器而记，为人而读

* **双重目标**: 日志既要便于日志系统解析，也要让开发人员能够快速理解
* **禁止 `print()`**: 在任何业务逻辑或请求处理中，**严禁**使用 `print()`。**必须**使用标准 `logging` 模块
* **JSON 格式**:
  * **强制要求**: 所有生产环境日志输出**必须**为 JSON 格式
  * **开发环境**: 可使用 `python-json-logger` 的彩色控制台输出便于调试
  * **禁止非结构化日志**: 禁止在日志消息中拼接动态内容

## 2. 结构化日志规范

* **正确做法**: 必须使用 `extra` 参数或日志记录器的 `bind` 方法添加上下文
* **示例对比**:

    ```python
    # 错误 ❌ - 字符串拼接
    logging.info(f"User {user_id} from {ip_address} performed {action}")
    
    # 可接受 ✅ - 但不够结构化
    logging.info("User action performed", extra={
        "user_id": user_id, 
        "ip_address": ip_address,
        "action": action
    })
    
    # 最佳实践 ✅ - 语义化字段命名
    logging.info("user_action_performed", extra={
        "user_id": user_id,
        "client_ip": ip_address,
        "action_type": action,
        "event_timestamp": datetime.utcnow().isoformat()
    })
    ```

## 3. 日志级别使用规范

* **`DEBUG`**:
  * **用途**: 开发调试，包含变量值、SQL查询、内部状态
  * **生产环境**: 默认关闭，按需动态开启
  * **示例**: `"Executing SQL: SELECT ..."`, `"Cache miss for key: ..."`

* **`INFO`**:
  * **用途**: 业务流程关键节点，用于追踪用户旅程和系统流程
  * **要求**: 必须包含业务标识符 (user_id, order_id等)
  * **示例**: `"order_created"`, `"payment_processed"`, `"user_registered"`

* **`WARNING`**:
  * **用途**: 可恢复的异常情况，需要监控但不需要立即干预
  * **要求**: 必须包含原因和影响范围
  * **示例**: `"rate_limit_exceeded"`, `"cache_fallback_used"`

* **`ERROR`**:
  * **用途**: 操作失败但应用仍可运行
  * **要求**: 必须包含完整错误上下文和堆栈跟踪
  * **示例**: `"payment_gateway_timeout"`, `"database_connection_failed"`

* **`CRITICAL`**:
  * **用途**: 系统级故障，需要立即人工干预
  * **示例**: `"database_unavailable"`, `"disk_space_exhausted"`

## 4. 上下文管理与追踪

* **请求上下文**:

    ```python
    # 使用上下文管理器或装饰器自动添加请求ID
    @log_request_context
    def process_order(request):
        logging.info("order_processing_started")  # 自动包含 request_id
    ```

* **关键追踪字段**:
  * **请求ID**: 必须包含 `request_id` 或 `trace_id`
  * **会话ID**: 建议包含 `session_id` 用于用户会话追踪
  * **组件标识**: 包含 `service_name`, `module_name` 等系统标识
  * **时间戳**: 使用ISO格式的 `timestamp` 字段

* **性能监控字段** (可选但推荐):

    ```python
    logging.info("api_request_completed", extra={
        "duration_ms": 150,
        "response_size": 2048,
        "status_code": 200
    })
    ```

## 5. 安全与敏感信息

* **绝对禁止**:
  * 密码、API密钥、Token、私钥
  * 信用卡号、银行账户信息
  * 完整的个人身份信息 (身份证号、手机号、地址)

* **脱敏规则**:

    ```python
    # 错误 ❌
    logging.info("user_updated", extra={"email": "user@example.com"})
    
    # 正确 ✅ - 部分脱敏
    logging.info("user_updated", extra={
        "user_id": "usr_123",
        "email_domain": "example.com"  # 仅记录域名
    })
    
    # 正确 ✅ - 哈希处理
    logging.info("user_accessed", extra={
        "user_id_hash": hashlib.sha256(user_id.encode()).hexdigest()[:8]
    })
    ```

* **自动过滤**: 推荐使用日志过滤器和处理器自动脱敏敏感字段

## 6. 性能与运维考虑

* **日志量控制**:
  * 避免在循环中记录高频日志
  * 使用采样率 (sampling) 处理高频调试日志
  * 设置合理的日志级别，避免生产环境输出DEBUG日志

* **错误日志完整性**:

    ```python
    # 错误 ❌ - 缺少上下文
    try:
        process_payment()
    except PaymentError:
        logging.error("Payment failed")
    
    # 正确 ✅ - 完整错误信息
    try:
        process_payment(order_id=order_id)
    except PaymentError as e:
        logging.error(
            "payment_processing_failed",
            extra={
                "order_id": order_id,
                "error_type": type(e).__name__,
                "error_message": str(e)
            },
            exc_info=True  # 包含堆栈跟踪
        )
    ```
