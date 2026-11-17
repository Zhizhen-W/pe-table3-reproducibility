# 复现流程与数据对应

## 计算入口

- `scripts/inspect_result.py` 查找指定表格结果对应的配置、输入、声压和评价点。
- `scripts/reproduce_table3.py` 由归档声压及参考输入计算表 III，输出 CSV 和 Markdown 表格。
- `scripts/stage_inputs.py` 将指定配置的原生输入恢复到工作目录，供对应求解器使用。
- `expected/` 保存论文报告值，供结果对照。

## 参考场与评价点

| 算例 | 数据对应关系 |
|---|---|
| C3/C4 WAMPE | 30 Hz 使用 55:5:2000 m，90 Hz 使用 52:2:500 m；坐标见评分清单 |
| C7 100 Hz | PE 评分参考为 M300/N1600；参考检查为 M300、N3200→6400 |
| C8 100 Hz | PE 评分参考为 M300/N3200；参考检查为 M300、N12800→25600 |
| C9 LSS-FD 3D | 方位步长为 0.04° |
| C9 SI | 使用归档文件第三列复声压与 479 个评价坐标；参考检查列为 Unverified |
| N1 | 按六个截断角构建有限模态参考，参考检查列为 Analytical |

C3 的参考检查由 DGM 实现按两级参数生成声压后计算。各项参考检查的取点与聚合方式见[参考检查指南](reference-guide.md)。

## 起始场与程序来源

C1 配置记录 Green 函数起始场来源；C3 记录 COMSOL 场及共轭转换。各配置的 `files` 保存实际注入文件，`starter_sources` 保存生成来源。

`configurations.json` 给出原生输入和运行记录。使用 `stage_inputs.py` 恢复输入后，按记录调用对应程序构建。程序版本、接口扩展及依赖见 [THIRD_PARTY.md](../THIRD_PARTY.md)。
