# 📦 `ErisPulse.__main__` 模块

*自动生成于 2025-07-22 16:35:31*

---

## 模块概述

ErisPulse SDK 命令行工具

提供ErisPulse生态系统的包管理、模块控制和开发工具功能。

💡 **提示**：

1. 需要Python 3.8+环境
2. Windows平台需要colorama支持ANSI颜色

---

## 🛠️ 函数

### `main`

CLI入口点

💡 **提示**：

1. 创建CLI实例并运行
2. 处理全局异常

---

## 🏛️ 类

### `CommandHighlighter`

高亮CLI命令和参数

💡 **提示**：

使用正则表达式匹配命令行参数和选项


### `PackageManager`

ErisPulse包管理器

提供包安装、卸载、升级和查询功能

💡 **提示**：

1. 支持本地和远程包管理
2. 包含1小时缓存机制


#### 🧰 方法

##### `__init__`

初始化包管理器

---

##### 🔹 `async` `_fetch_remote_packages`

从指定URL获取远程包数据

:param url: 远程包数据URL
:return: 解析后的JSON数据，失败返回None

⚠️ **可能抛出**: `ClientError` - 网络请求失败时抛出
⚠️ **可能抛出**: `JSONDecodeError` - JSON解析失败时抛出

---

##### 🔹 `async` `get_remote_packages`

获取远程包列表，带缓存机制

:param force_refresh: 是否强制刷新缓存
:return: 包含模块和适配器的字典

:return:
    dict: {
        "modules": {模块名: 模块信息},
        "adapters": {适配器名: 适配器信息},
        "cli_extensions": {扩展名: 扩展信息}
    }

---

##### `get_installed_packages`

获取已安装的包信息

:return: 已安装包字典，包含模块、适配器和CLI扩展

:return:
    dict: {
        "modules": {模块名: 模块信息},
        "adapters": {适配器名: 适配器信息},
        "cli_extensions": {扩展名: 扩展信息}
    }

---

##### `_is_module_enabled`

检查模块是否启用

:param module_name: 模块名称
:return: 模块是否启用

⚠️ **可能抛出**: `ImportError` - 核心模块不可用时抛出

---

##### `_run_pip_command`

执行pip命令

:param args: pip命令参数列表
:param description: 进度条描述
:return: 命令是否成功执行

---

##### `install_package`

安装指定包

:param package_name: 要安装的包名
:param upgrade: 是否升级已安装的包
:return: 安装是否成功

---

##### `uninstall_package`

卸载指定包

:param package_name: 要卸载的包名
:return: 卸载是否成功

---

##### `upgrade_all`

升级所有已安装的ErisPulse包

:return: 升级是否成功

⚠️ **可能抛出**: `KeyboardInterrupt` - 用户取消操作时抛出

---

### `ReloadHandler`

文件系统事件处理器

实现热重载功能，监控文件变化并重启进程

💡 **提示**：

1. 支持.py文件修改重载
2. 支持配置文件修改重载


#### 🧰 方法

##### `__init__`

初始化处理器

:param script_path: 要监控的脚本路径
:param reload_mode: 是否启用重载模式

---

##### `start_process`

启动监控进程

---

##### `_terminate_process`

终止当前进程

:raises subprocess.TimeoutExpired: 进程终止超时时抛出

---

##### `on_modified`

文件修改事件处理

:param event: 文件系统事件

---

##### `_handle_reload`

处理重载逻辑

:param event: 文件系统事件
:param reason: 重载原因描述

---

### `CLI`

ErisPulse命令行接口

提供完整的命令行交互功能

💡 **提示**：

1. 支持动态加载第三方命令
2. 支持模块化子命令系统


#### 🧰 方法

##### `__init__`

初始化CLI

---

##### `_create_parser`

创建命令行参数解析器

:return: 配置好的ArgumentParser实例

---

##### `_load_external_commands`

加载第三方CLI命令

:param subparsers: 子命令解析器

⚠️ **可能抛出**: `ImportError` - 加载命令失败时抛出

---

##### `_print_version`

打印版本信息

---

##### `_print_installed_packages`

打印已安装包信息

:param pkg_type: 包类型 (modules/adapters/cli/all)
:param outdated_only: 是否只显示可升级的包

---

##### `_print_remote_packages`

打印远程包信息

:param pkg_type: 包类型 (modules/adapters/cli/all)

---

##### `_is_package_outdated`

检查包是否过时

:param package_name: 包名
:param current_version: 当前版本
:return: 是否有新版本可用

---

##### `_resolve_package_name`

解析简称到完整包名

:param short_name: 模块/适配器简称
:return: 完整包名，未找到返回None

---

##### `_setup_watchdog`

设置文件监控

:param script_path: 要监控的脚本路径
:param reload_mode: 是否启用重载模式

---

##### `_cleanup`

清理资源

---

##### `run`

运行CLI

⚠️ **可能抛出**: `KeyboardInterrupt` - 用户中断时抛出
⚠️ **可能抛出**: `Exception` - 命令执行失败时抛出

---


*文档最后更新于 2025-07-22 16:35:31*