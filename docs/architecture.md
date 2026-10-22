# 架构：坐标、注册表与包

## 1. 目标

给每个模型包一个**稳定地址**，让引用、组合与升级不依赖文件路径。

三件事必须同时成立：

1. 坐标唯一：同一个 `groupId:artifactId:version` 只能指向一份内容；
2. 依赖可解析：给定一组坐标，工具能算出完整的包集合；
3. 内容可校验：每个包有指纹，内容变了指纹就变。

## 2. 三层

### 2.1 坐标层

坐标写作：

```text
<groupId>:<artifactId>:<version>
cn.ai4energy.esml:esml-thermal:0.1.0
```

`groupId` 是组织边界，`artifactId` 是包名，`version` 是语义化版本。发布后坐标不可变；改内容必须升版本。

### 2.2 注册表层

`registry/index.tsv` 一行一个发布坐标，记录：

- 坐标、命名空间、包路径；
- 仓库与 commit（本仓包为 `local`）；
- 内容指纹（sha256）；
- 状态（`stable` / `experimental` / `deprecated`）；
- 许可证与依赖。

注册表**只登记**，不复制代码。官方包在本仓；社区包可以在任何 Git 仓。

### 2.3 包层

每个包是一个目录：

```text
libraries/esml-thermal/
  package.esml          元数据：坐标、命名空间、依赖、导出
  README.md
  src/*.comp.esml       模型类型
  examples/             包内示例（可选）
  tests/                包内判据（可选）
```

`package.esml` 的根是 `<package>`，与模型文档的 `<esml>` 根分开；工具按根元素识别，不混用。

## 3. 领域分层

```text
esml-units         单位与量纲
    ↑
esml-connectors    端口类型（流体、热、电、信号）
    ↑
esml-thermal       换热、储热、热工设备
esml-fluid         泵、阀、管、压缩机、透平
esml-electrical    母线、线路、电机、负荷
esml-control       PID、限幅、延时、信号
esml-storage       电池、储热、储氢
esml-renewable     光伏、风电
    ↑
esml-examples-*    场景包（只依赖领域包）
```

依赖只允许**向下**：领域包依赖连接器与单位，场景包依赖领域包；同层包不互相依赖，避免环。确有共享需求时，抽出更底层的包，而不是横向引用。

## 4. 引用与解析

ESML 文档引用包：

```xml
<use library="cn.ai4energy.esml:esml-thermal:0.1.0"/>
```

解析器按注册表定位包，校验指纹，展开导出文件。BOM 提供一组默认版本：

```xml
<use library="cn.ai4energy.esml:esml-thermal"/>   <!-- 版本由 BOM 决定 -->
```

> 无版本引用只在 BOM 作用域内有效；脱离 BOM 必须写全坐标。

## 5. 生命周期

| 阶段 | 动作 | 判据 |
|---|---|---|
| 提案 | 分配命名空间与坐标 | 命名空间未占用；坐标格式合法 |
| 开发 | 本地包 + `experimental` | 包可解析；依赖存在 |
| 发布 | 注册表登记 + tag | 指纹匹配；版本不可变 |
| 弃用 | 状态改 `deprecated` | 给出替代坐标 |
| 删除 | 不删注册行 | 历史坐标仍可解析（只读） |

## 6. 不做什么

- 不做包管理器运行时：解析由工具与引擎完成；
- 不托管社区代码：注册表只记录地址与指纹；
- 不做模型语义检查：那属于编译器的职责，本仓只保证坐标与依赖的一致性。
