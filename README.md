# RustDesk SDK

RustDesk sdk 基于 [RustDesk](https://github.com/rustdesk/rustdesk) 提供rustdesk远程控制的 C ABI，支持在所有编程语言使用，用于在其他语言中嵌入 RustDesk 的功能。

提示：当前 API 处于测试阶段，可能不稳定；严禁将本 SDK 用于任何非法用途。

RustDesk 上游仓库：
```
https://github.com/rustdesk/rustdesk
```

感谢 <a href="https://www.distromate.net/">Distromate 分发助手</a> 提供支持

<a href="https://www.distromate.net/"><img alt="Distromate" src="https://obsidian-static.s3.bitiful.net/2026/01/%E9%A1%B5%E9%9D%A2%201.png" width="250" height=""></a>


## SDK 特性

- 动态库交付：构建 `cdylib`，对外提供 C ABI，便于多语言集成。
- 服务控制：初始化、启动/停止服务、查询运行状态。
- 身份与鉴权：获取设备 ID，读取/更新临时密码，设置永久密码。
- 配置管理：按键读写配置项，获取全部配置的 JSON。
- 连通性检测：rendezvous 服务器信息、NAT 类型检测、连通性测试。
- 开发示例：提供 Python/Tk 示例，便于快速验证集成流程。

## API 使用（Python）

使用 `ctypes` 的最小示例：

```python
import ctypes
import os

dll = ctypes.CDLL(os.path.abspath("target/release/rustdesk_sdk.dll"))

dll.rd_start_server_safe.restype = ctypes.c_bool
dll.rd_get_id.restype = ctypes.c_void_p
dll.rd_free_c_string.argtypes = [ctypes.c_void_p]

if dll.rd_start_server_safe():
    ptr = dll.rd_get_id()
    device_id = ctypes.c_char_p(ptr).value.decode("utf-8")
    dll.rd_free_c_string(ptr)
    print("ID:", device_id)
```

完整示例：
- `examples/rustdesk_sdk_tkinter.py`

## 构建 SDK

```bash
cargo build -p rustdesk_sdk --release
```

产物：
- Windows：`target/release/rustdesk_sdk.dll`
- macOS：`target/release/librustdesk_sdk.dylib`
- Linux：`target/release/rustdesk_sdk.so`

## API

### 生命周期
- `bool rd_global_init()`
  - 初始化 RustDesk 全局状态。
- `bool rd_start_server_safe()`
  - 安全启动（与示例一致）：
    - `global_init()` -> 如果不是 `is_cm` -> `start_server(false, false)`
    - 启动前清除 `stop-service` 选项。
- `bool rd_stop_server()`
  - 设置 `stop-service = "Y"` 并重启 mediator 以停止服务。
- `bool rd_is_server_running()`
  - SDK 侧运行标记。

### 身份与鉴权
- `char* rd_get_id()`
  - 返回设备 ID。
- `char* rd_get_temporary_password()`
  - 返回临时密码。
- `bool rd_update_temporary_password()`
  - 重新生成临时密码。
- `char* rd_get_permanent_password()`
  - 返回永久密码（可能为空）。
- `bool rd_set_permanent_password(const char* password)`
  - 设置永久密码。

### 选项与配置
- `char* rd_get_option(const char* key)`
  - 按 key 获取单个配置项。
- `bool rd_set_option(const char* key, const char* value)`
  - 按 key 设置配置项。
- `char* rd_get_all_options()`
  - 返回所有配置项的 JSON。

常用网络配置项 key：
- `custom-rendezvous-server`（ID 服务器）
- `relay-server`（中继服务器）
- `api-server`
- `key`

### 连通性
- `char* rd_get_rendezvous_server(uint64_t ms_timeout)`
  - 返回 JSON：`{ "server": "...", "servers": [...], "is_public": true/false }`
- `int32_t rd_get_nat_type(uint64_t ms_timeout)`
  - 返回 NAT 类型值，失败返回 -1。
- `bool rd_test_rendezvous_server()`
  - 触发 rendezvous server 测试。

### 内存
- `void rd_free_c_string(char* s)`
  - 释放 SDK 返回的字符串。
