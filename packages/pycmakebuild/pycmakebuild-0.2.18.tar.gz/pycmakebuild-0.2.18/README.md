# pycmakebuild

Python CMake 批量构建与自动化工具，支持通过 build.json 配置文件和命令行批量编译多个 CMake 项目，适用于跨平台 C++/第三方库工程的自动化批量编译。

## 功能特性
- 支持 build.json 配置批量管理和编译多个 CMake 项目
- 支持 Debug/Release 等多种构建类型，支持自定义 CMakeLists.txt 子目录
- 支持命令行一键初始化环境、生成模板、批量构建
- 自动推断 CMake 构建参数，兼容 Windows/Linux/Mac
- 支持通过 `python -m pycmakebuild` 或 `pycmakebuild` 命令行调用

## 快速开始

### 1. 安装
```bash
pip install pycmakebuild
```


### 2. 初始化环境和模板
```bash
python -m pycmakebuild --init
```
将在当前目录生成 .env 和 build.json 模板。

### 3. 编辑 build.json
示例：
```json
{
  "sources": [
    {
      "path": "../Log4Qt",
      "name": "log4qt",
      "cmakelists_subpath": ".",
      "other_build_params": ["-DCUSTOM_OPTION=ON"]
    }
  ]
}
```
- `path`: CMake 项目源码路径
- `name`: 目标名称（安装目录名）
- `cmakelists_subpath`: CMakeLists.txt 所在子目录（可选，默认"."）
- `other_build_params`: 传递给 cmake 的额外参数列表（如 ["-DCUSTOM_OPTION=ON"]，可选）

### 4. 批量构建
编译Release版本
```bash
python -m pycmakebuild
```
或编译Debug版本
```bash
python -m pycmakebuild --build=Debug
```
或指定配置文件
```bash
python -m pycmakebuild --build=Release --json mybuild.json
```
会自动检测指定json并批量构建所有配置项目，支持自定义 cmake 参数。

### 5. 批量更新源码（git工程）
```bash
python -m pycmakebuild --clean
```
更新所有 build.json 中配置的项目源码，不会删除安装目录。


## 环境变量加载与自定义

pycmakebuild 不再依赖 python-dotenv，环境变量文件（.env）由工具内置解析，且不会污染系统环境变量。

**环境变量文件格式**：

```
INSTALL_PATH=xxx   # 安装根目录
GENERATOR=xxx      # CMake生成器，如 Ninja、Visual Studio 17 2022 等
ARCH=x64           # 架构，可选 x64/Win32/arm64
BUILD_DIR=build    # 构建输出目录
CORES=32           # 并发核心数
```

**自定义 env 文件**：

可通过 `--env=xxx.env` 指定任意环境变量文件，所有变量仅在 pycmakebuild 内部生效，不影响系统环境。

**示例**：

```shell
pycmakebuild --build=Release --env=myenvfile.env
```

如未指定，默认加载当前目录下的 `.env` 文件。

## 命令行参数
- `--init`  初始化环境和 build.json 模板
- `--build [Debug|Release]`  指定构建类型，支持 --build=Debug 或 --build=Release，默认Release
- `--json <file>`  指定配置json文件，默认为build.json
- `--env <file>`  指定环境变量文件，默认为.env
- `--clean` 清理所有 build.json 配置的项目源码（git clean/pull）
- `--version` 显示版本号


## 依赖
- cmake：Python CMake 封装

## 典型应用场景
- 本地一键环境初始化默认构建环境与批量编译CMake三方库

## License
MIT
