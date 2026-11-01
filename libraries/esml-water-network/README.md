# esml-water-network

水网 DTIL 组件库（0.1.0，experimental）。命名空间：`WaterNetwork`。
依赖：`cn.ai4energy.esml:esml-units:0.1.0`。

## 组件

| modelType | 端口 | 方程 |
|---|---|---|
| `Reservoir` | `p` | `p.H = total_head` |
| `Junction` | `p` | `p.Q = base_demand` |
| `Pipe` | `a`/`b` | Hazen-Williams + `Q·(Q²+ε²)^0.426` 零流正则化 |
| `PumpSpeed` | `a`/`b`/`SpeedIn` | `H = u²·H0 − k·Q|Q|`（仿射律） |
| `SpeedCommand` | `Out` | `Out.v = speed` |
| `PRVCheck` | `a`/`b` | 正流 PRV：调节 `b.H=H_set`，`Q<0` 时关闭 |
| `LeakJunction` | `p` | `Q = base_demand + k·ifelse(P>0, P^0.5, 0)` |
| `PDALeakJunction` | `p` | `Q = base·f(P) + k·ifelse(P>0, P^0.5, 0)` |

`PDALeakJunction` 的 `f(P)`：`P<=Pmin` 为 0，`P>=Preq` 为 1，
中间 `((P-Pmin)/(Preq-Pmin))^n_exp`。默认 `Pmin=5 m`、`Preq=30 m`、`n_exp=0.5`。

端口 `Hydraulic` 带 `H`（potential）/`Q`（flow）；`SpeedInput`/`SpeedOutput`
是标量信号口。`PRVCheck` 是**正流**阀：普通 PRV 在泵出口 `H_set` 低于
下游压力时会给负流量（实测 −0.18 m³/s）；`PRVCheck` 增加 `a.Q<0` 的关闭分支。

## 场景

`scenarios/net1-pda.esml` 用本库重搭 Net1 泵供分区（去定水头罐）：

- 9 个 `PDALeakJunction`、12 根 `Pipe`、1 台 `PumpSpeed`、泵出口 `PRVCheck`；
- 基荷 0.0694 m³/s，`k=1e-4`，基线漏损约 8.44 L/s（12.2%）；
- `H_set=306.12 m` 时 74 个未知数、6 次 Newton、单位覆盖 **74/74**，
  泵流量 **0.07784 m³/s**，与 `esml-engine/examples/water-twin/net1_pda_leak.esml`
  逐值一致。

```sh
esml solve libraries/esml-water-network/scenarios/net1-pda.esml -L . --full
```

## 边界

- **单位**：与引擎水网库一致，`H/Q` 声明为 `unit=1`（无量纲），数值按 SI
  使用（m、m³/s）；应用层用 EPANET 标高另算压力（m）。不要把 `unit=1`
  当物理单位；要发布训练集，先补 `Head`/`FlowRate` 类型。
- 本库只覆盖 DTIL 子集，不含 Tank/TankDyn、FCV/PSV/TCV、泵曲线族；
  这些仍在 `esml-engine/library/domains/hydraulic/water_network.comp.esml`。
- `PRVCheck` 的互补式方程是分段/非光滑的；扫参时建议先扫描再二分，
  不要假设 `h(H_set)` 单调。
- 漏损/PDA 系数是合成值，不是现场标定；现场标定见
  `esml-engine/examples/water-twin/` 的下一步（Modbus/OPC UA → `R/k` 辨识）。
