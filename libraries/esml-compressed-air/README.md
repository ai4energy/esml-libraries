# esml-compressed-air

压缩空气站/管网组件库（M0）。

命名空间：`CompressedAir`。依赖：`cn.ai4energy.esml:esml-units:0.1.0`。

## 组件

| modelType | 端口 | 方程 |
|---|---|---|
| `AirCompressor` | `out` | `p_out = p_max − b·m²`；`W = m·cp·T_in·(r^((γ−1)/γ)−1)/η` |
| `AirHeader3` / `AirHeader6` | 3/6 进 + 1 出 | 质量相加、压力相等 |
| `ReceiverTank` | in/out | `Der(p) = (R_g·T/V)(m_in−m_out)` |
| `AirPipe` | in/out | `Δp = R·m·|m|` |
| `AirSplitter2/3/4` | 1 进 + 2/3/4 出 | 质量相加、压力相等 |
| `AirPass` | 1 进 1 出 | 直通 |
| `AirDemand` | in | `m = demand` |

端口 `AirPort` 只带 `p` 和 `m`，沿用 DTIL 原型的 p/m 约定（不写
`portRole`；与 `examples/compressed-air-twin` 的 CAS 原型逐位一致）。
温度由空压机 `T_in` 与储罐 `T_tank` 参数给出，暂不进端口。

## 示例

`scenarios/three-machine.esml` 用本库重搭 DTIL 原型的三机网络：

```sh
esml solve libraries/esml-compressed-air/scenarios/three-machine.esml \
  -L . --full
```

实测（默认 cp=1005 / γ=1.4 / R=287.047）：

- 61 个未知数，5 次迭代，单位覆盖 61/61；
- 集管 650.005 kPa，末端 552.405 kPa；
- 三机总功率 **2.964 MW**。

与 `esml-engine/examples/compressed-air-twin/sys_compressed_air_twin.esml`
的 67 未知数/2.980 MW 相比，差异来自应用层用 `cp_air`/`gamma_air` 物性函数
覆盖了库参数（+0.5%）；网络方程和端口约定相同。

## 边界

- 本库是压力-流量层；负荷分配、MPC、空气物性不属于库组件，分别在
  `esml-engine/examples/compressed-air-twin/` 的 `load_allocation.py`、
  `tank_mpc.esml`、`dtil_mpc.py` 中。
- 空压机 cp/γ/R 以参数给出（默认 1005 / 1.4 / 287.047），
  DTIL 应用层可用 mmprops 的 `cp_air(T,P)` / `gamma_air(T,P)` 求值后覆盖。
