# 注册表规范

## 1. 文件

- `registry/index.tsv`：发布坐标索引，一行一个坐标。
- `registry/namespaces.tsv`：命名空间分配，一行一个前缀。

两文件都是 UTF-8、Tab 分隔、首行表头；不允许空行与重复行。

## 2. index.tsv 列

| 列 | 含义 |
|---|---|
| `groupId` | 组织坐标 |
| `artifactId` | 包名 |
| `version` | 语义化版本 |
| `namespace` | 顶层命名空间 |
| `path` | 本仓相对路径；社区包写 `-` |
| `repository` | Git 地址；本仓写 `local` |
| `commit` | 发布 commit；本仓写 `-` |
| `sha256` | 包指纹 |
| `status` | `stable` / `experimental` / `deprecated` |
| `license` | SPDX 标识 |
| `dependencies` | 逗号分隔的完整坐标；无依赖写 `-` |
| `replacement` | 弃用时的替代坐标；否则 `-` |

## 3. 包指纹

指纹覆盖包目录内所有文件：按相对路径排序，依次拼接「路径 + `\0` + 内容 + `\0`」，取 SHA-256。`package.esml` 与 `src/` 都计入；`README.md` 与 `tests/` 也计入（发布内容的一部分）。

生成与校验：

```sh
python3 tools/validate_registry.py --write-digests
python3 tools/validate_registry.py
```

## 4. 注册流程

### 官方包（本仓）

1. 在 `libraries/` 建目录，写 `package.esml` 与 `src/`；
2. 在 `registry/namespaces.tsv` 分配命名空间；
3. 在 `registry/index.tsv` 增加一行，`repository=local`；
4. 运行 `--write-digests` 生成指纹；
5. PR 评审：坐标、命名空间、依赖方向、包可解析。

### 社区包（外部仓）

1. 作者在自己仓发布 tag，记录 commit；
2. PR 到本仓注册表，填 `repository`、`commit`、`sha256`、许可证、依赖；
3. CI 校验：坐标格式、版本、依赖存在、仓库可访问、指纹匹配；
4. 合并后即可被 `<use library="…">` 解析。

社区包不复制进本仓；注册表只记录地址与指纹。撤回注册不删除行，状态改 `deprecated`。

## 5. 校验判据

`tools/validate_registry.py` 检查：

- 坐标三段非空、字符集合法、版本符合语义化；
- 同一坐标只出现一次；
- 命名空间已分配且未被其他包占用；
- 本仓包路径存在、`package.esml` 坐标一致；
- 指纹匹配（除非显式 `--write-digests`）；
- 依赖坐标都在注册表中；
- 依赖不形成环；
- 状态与替代坐标自洽。

任何一条失败，退出码非零。

## 6. 解析

`tools/resolve.py` 给定一组坐标（或 BOM），输出：

- 依赖闭包（含传递依赖）；
- 每个包的本地路径或仓库地址；
- 冲突（同一 artifact 多个版本）。
