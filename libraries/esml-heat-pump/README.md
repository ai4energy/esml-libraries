# esml-heat-pump

热泵/暖通组件库（0.1.0，experimental）。命名空间：`HeatPump`。
依赖：`cn.ai4energy.esml:esml-units:0.1.0`；场景需要 `esml-mmprops` provider。

## 组件

| modelType | 作用 |
|---|---|
| `R134aCycle` | R134a 稳态蒸气压缩循环：`T_evap/T_cond/T2/Q_load` → COP、W、Q_evap |
| `HouseHP` | 建筑单热容 + COP 二次拟合 + 部分负荷修正；`PLR` 可被 control 任务操纵 |

`R134aCycle` 的属性函数：`psat_R134a` / `hg_R134a` / `h_v_R134a` /
`T_sat_R134a` / `hf_R134a`。`T2` 是排气温度参数（默认 `T_cond+25 K`）；
`eta_s` 在应用层用 `T_isentropic_R134a` 后处理，不进稳态方程。

`HouseHP` 的 COP 系数来自 `examples/heat-pump-twin/hp_map.csv` 的 3×3
数据（K 为单位，R²=0.99976）；部分负荷修正 `1+0.1·(1−PLR)` 是合成假设。

## 场景

```sh
export ESML_PROPS_LIB=~/esml-repos/esml-mmprops/target/release/libesml_mmprops_ffi.so
esml solve libraries/esml-heat-pump/scenarios/r134a-cycle.esml -L . --json
esml tasks libraries/esml-heat-pump/scenarios/building-mpc.esml -L . --json
```

实测：

- `r134a-cycle`：12 个未知数、6 次 Newton、单位 12/12；
  COP **3.26771**，W **1530.12 W**，Q_evap **3469.88 W**；
- `building-mpc`：`mpc` 24 区间，−5 °C 稳 20 °C；`mpc_cold` 24 区间，
  −15 °C 容量饱和在 17.07 °C。

## 边界

- 稳态循环，无部分负荷实验、换热器 `UA`、EEV/转速、除霜；
- R410A 是混合物，需要混合物 EOS；R32 缺 `T_isentropic_R32`；
- 属性函数不带单位签名，单位由 `variableTypes` / 场景 `<units>` 声明补齐；
- `HouseHP` 是降阶控制模型，不是详细建筑模型。
