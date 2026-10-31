# 坐标规范

## 1. 形式

```text
<groupId>:<artifactId>:<version>
```

三段都非空；冒号是唯一分隔符，不允许出现在段内。

## 2. groupId

- 官方：`cn.ai4energy.esml`。
- 社区：作者自有域名反写，例如 `com.example.esml`；不得使用 `cn.ai4energy.esml` 或其子段。
- `groupId` 只标识组织，不携带领域信息；领域放在 `artifactId` 与命名空间。

## 3. artifactId

- 官方：`esml-<name>`，小写 kebab（`esml-thermal`、`esml-examples-thermal`）。
- 社区：`<author>-<name>`，不得以 `esml-` 开头。
- 只允许小写字母、数字与连字符；不得以下划线、点号或连字符开头/结尾。

## 4. version

语义化版本 `MAJOR.MINOR.PATCH`：

- `MAJOR`：坐标语义或导出类型不兼容；
- `MINOR`：新增类型或可选参数；
- `PATCH`：修正实现，不改变导出面。

禁止 `SNAPSHOT`、`latest`、日期版本进入注册表。预发布用 `-rc.N` / `-beta.N`，并在状态列标 `experimental`。

## 5. 不可变性

同一坐标发布后不可修改内容。修正必须升 `PATCH`；破坏性变更升 `MAJOR`。注册表保留旧行，状态可改 `deprecated`，但坐标与指纹不变。

## 6. 命名空间

`package.esml` 里的 `<namespace>` 是模型类型的顶层前缀：

```text
esml-thermal  →  Thermal
Thermal.Pipe
```

- 官方命名空间是 PascalCase，可单段或点分子段：`Units`、`Connectors`、`Thermal`、`Fluid`、`CompressedAir`、`Electrical`、`Control`、`Storage`、`Renewable`、`Examples`、`Examples.Thermal`。
- 官方保留首段集合：`Units`、`Connectors`、`Thermal`、`Fluid`、`Electrical`、`Control`、`Storage`、`Renewable`、`Examples`。
- 社区命名空间至少两段（`Com.Example`），首段不得是官方保留集合中的名字。
- 一个命名空间只能属于一个 `artifactId`；分配记录在 `registry/namespaces.tsv`。

## 7. BOM

BOM 是一组坐标的版本清单：

```xml
<bom groupId="cn.ai4energy.esml" artifactId="esml-bom" version="0.1.0">
  <packages>
    <package coordinate="cn.ai4energy.esml:esml-units:0.1.0"/>
    <package coordinate="cn.ai4energy.esml:esml-connectors:0.1.0"/>
  </packages>
</bom>
```

BOM 自身也有坐标；升级 BOM 是一次显式事件，不允许隐式漂移。
