# 分层与同层依赖

五层：基础 0、接口 1、域 2、系统 3、场景 4。依赖只允许向下或同层，不允许向上。

域内再分两类：

- **基础域**：`thermal`、`fluid`、`electrical`、`properties`、`control`；
- **应用域**：`hvac`、`renewable`、`storage`、`chemical`。

同层依赖只允许「应用域 → 基础域」，不允许反向，也不允许应用域之间成环。当前同层边与理由：

| 应用域 | 依赖 | 理由 |
|---|---|---|
| hvac | thermal / fluid / electrical | 热泵、冷机、末端同时使用热、流、电接口 |
| renewable | thermal / fluid / electrical | 集热器用热与流，光伏/风机并电 |
| storage | electrical / thermal | 电池、储热各自依赖其接口域 |
| chemical | fluid / thermal | 单元操作依赖流动与传热 |

系统包（`systems-*`）只依赖域包，不被域包依赖。场景包只依赖系统包或域包。
