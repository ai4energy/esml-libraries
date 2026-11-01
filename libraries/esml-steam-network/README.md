# esml-steam-network

蒸汽管网组件库（0.1.0，experimental）。命名空间：`SteamNetwork`。
依赖：`cn.ai4energy.esml:esml-units:0.1.0`；场景需要 `esml-mmprops` provider。

## 组件

| modelType | 作用 |
|---|---|
| `SteamHeader3` | 4 MPa 饱和母管 + 3 支路，Darcy 压降 + 可用冷凝热 |
| `SteamHeader3Loss` | 在上者基础上加管损 `Q_loss=UA·(T−T_amb)`、凝结份额 `x_cond`、净热量 `Q_net` |
| `SteamPRV` | 4→1 MPa 等焓节流 + 下游管段；`dT_super` 参数近似等焓 |

属性函数：`Tsat_water` / `hg_water` / `hf_water` / `rho_water` / `h_water`。
蒸汽按饱和处理；管损是等温凝结，不是温降。

## 场景

```sh
export ESML_PROPS_LIB=~/esml-repos/esml-mmprops/target/release/libesml_mmprops_ffi.so
esml solve libraries/esml-steam-network/scenarios/header3-loss.esml -L . --json
esml solve libraries/esml-steam-network/scenarios/prv.esml -L . --json
```

实测：

- `header3-loss`：30 个未知数、16 次 Newton、单位 30/30；
  `Q_loss_total` **137.98 kW**，`x_cond` 1.34%，`Q_net_total` **10.154 MW**；
- `prv`：11 个未知数、6 次 Newton、单位 11/11；
  `T_v` **462.0935 K**，`p_u` **0.9872 MPa**，`Q_u` **4.081 MW**，
  `dh_throttle` **57.4 J/kg**（0.002%）。

## 边界

- 无减温器、汽包水位、两相动态、湿蒸汽干度/疏水；
- 摩擦因子固定 `f=0.02`，不是 Re/粗糙度相关式；
- `PRV` 的 `dT_super` 只对 `p_set=1 MPa` 标定，换压力要重新标定；
- 3 支路固定需求，无负荷曲线/MPC。
