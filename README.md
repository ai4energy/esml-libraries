# ESML Libraries

ESML 的开放模型库与坐标注册系统。

模型不是一段脚本，而是可以被引用、组合、版本化的**包**。本仓用一套 Maven 风格的坐标（`groupId:artifactId:version`）给每个模型包一个稳定地址，用注册表记录「有哪些包、依赖谁、哪个版本、校验和是多少」，用 BOM 锁定一组兼容版本。

## 三层

| 层 | 回答什么 | 位置 |
|---|---|---|
| 坐标 | 这个包叫什么、哪个版本 | `docs/coordinates.md` |
| 注册 | 这个包在哪、依赖谁、是否可信 | `registry/index.tsv` |
| 包 | 里面有什么模型、导出什么类型 | `libraries/<artifactId>/` |

## 目录

```text
docs/            架构、坐标、注册、治理
registry/        坐标索引与命名空间分配
bom/             版本清单（BOM）
libraries/       官方模型包
tools/           注册表校验与依赖解析
```

## 快速开始

```sh
python3 tools/validate_registry.py
python3 tools/resolve.py cn.ai4energy.esml:esml-thermal:0.1.0
```

在 ESML 文档里引用包：

```xml
<use library="cn.ai4energy.esml:esml-thermal:0.1.0"/>
```

## 官方与社区

- **官方包**：`groupId = cn.ai4energy.esml`，`artifactId` 以 `esml-` 开头，代码在本仓 `libraries/`，命名空间由维护者分配。
- **社区包**：使用作者自己的 `groupId`，代码可在任何 Git 仓；通过 PR 在注册表登记坐标、仓库、commit 与校验和，不复制代码进本仓。

## 原创边界

本仓的坐标、注册表、包结构、端口语义与模型均为原创实现；不复制任何现有建模库的源码、注释或命名体系。外部项目只作为「领域分层」的一般经验参考，不进入本仓的包、文档或模型命名。

## 许可

官方包 MIT；社区包必须是 OSI 认可的许可证，并登记在注册表中。

## 边界

本仓只组织开放模型与坐标，不包含求解器或编译器。
