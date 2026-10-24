# esml-tclab

TCLab 双热容集总热模型：2 加热器 + 2 温度传感器。

命名空间：`TCLab`。依赖：cn.ai4energy.esml:esml-units:0.1.0, cn.ai4energy.esml:esml-connectors:0.1.0。

导出 `TCLab.TCLab2Lumped`：11 参数（U / A / As / mCp / alpha1 / alpha2 / eps / sigma / Ta / Q1 / Q2）、
2 状态（T1 / T2）、2 方程（两条能量平衡）。方程逐字取自 APMonitor 的 ArduinoModeling2
教学模型（Hedengren, BYU；Park et al., *Computers & Chemical Engineering* 135 (2020) 106736）。

## 单位元数据修正

上游组件把 `U` / `As` 的单位标成 `W_per_K`，但模型里 `U` 是**按面积**用的
（`U·A·(Ta − T1)`，`<parameter>` 自己的描述写着「U (W/m²·K)」）。于是
`U·A·(Ta−T1)` 的量纲是 W·m²，跟 `α1·Q1`（W）加不到一起，右端与左端 `D(T1)`（K/s）
差一个 m² ⇒ `esml simulate` 报两条 I27 量纲不符。

本包把两个类型的单位改成 `W_per_m2_K`（base `W*m^-2*K^-1`），σ 的单位改成
`stefan_boltzmann_unit`（base `W*m^-2*K^-4`）。**方程、参数值、初始条件一字未动**，
改的只是类型元数据 ⇒ I27 消失。

## 复跑

```sh
# 结构判据
esml check -L ~/esml-libraries libraries/esml-tclab/src/tclab.comp.esml

# 量纲判据：simulate 的输出里不应有 I27
esml simulate libraries/esml-tclab/src/tclab.comp.esml --system Demo \
  -L ~/esml-libraries --tspan 0,600 --steps 60

# 负控：把 W_per_m2_K 的 base 改成 W/K ⇒ simulate 恰好回两条 I27
```

## 边界

本包只放**模型语义**。SIL 标定点（`As=0`、`eps=0`、`sigma=0`、`Q1=10`）
留在引擎侧的 `examples/sil-calibration/tclab.esml`，不进库。`<system name="Demo">`
是本包的自证壳（通用演示点，不是标定点）。

消费方用 `<use library="cn.ai4energy.esml:esml-tclab:0.1.0"/>` 引用后，
实例取的是 **modelType 的声明默认值**，**不是** `Demo` 的 `<set>`（`<set>` 是
系统局部的，不跨系统传播）。默认值 `eps=0.9` / `sigma=5.67e-8` 是**非线性**默认，
`Q1=0`；要复现 SIL 标定轨迹（退成一阶单热容）必须显式覆写这 4 个：

```xml
<esml xmlns="https://www.ai4energy.cn/esml/v1" schema="esml/v1" name="MyTclab">
  <use library="cn.ai4energy.esml:esml-tclab:0.1.0"/>
  <systems name="s">
    <system name="S">
      <instances><instance name="g" type="TCLab2Lumped"/></instances>
      <sets>
        <scope instance="g">
          <set path="As"    value="0.0"/>
          <set path="eps"   value="0.0"/>
          <set path="sigma" value="0.0"/>
          <set path="Q1"    value="10.0"/>
        </scope>
      </sets>
    </system>
  </systems>
</esml>
```

实测：`esml simulate` 在 `tspan=0,1200 / steps=2400` 上给出
`1200.000000  3.06125213e2  2.96150000e2`，与引擎侧
`examples/sil-calibration/tclab.esml --system S` **逐位一致**，且 **0 条 I27**。

