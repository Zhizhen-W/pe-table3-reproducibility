# 表 III 的 PE 评分复现

## 范围

本包包含 110 个普通接收线评分及 N1 的 54 次角度评分。54 次角度评分汇总成表中的 9 个区间；另保留 51 个未报告方法单元格。因此 `manifests/table3_cells.csv` 对应 34 行、170 个方法单元格。

计算输入为归档的物理复声压及对应评价坐标。`expected/pe_table3.csv` 保存论文报告值，供结果对照。

## 使用

在仓库根目录运行，Python 3.10 或以上即可，无额外 Python 依赖：

```bash
python scripts/score_pe.py
python scripts/score_pe.py --case C8 --output results/C8_scores.csv --cells-output results/C8_cells.csv
```

默认生成 `results/pe_scores.csv` 和 `results/table3_pe_cells.csv`。前者列出每个普通结果和每个 N1 截断角的未舍入 RMSE，后者按论文顺序生成方法单元格。参考解 D_SPL 列由独立的参考检查入口处理。

## 从表格找到输入与数据

1. 在 `manifests/table3_cells.csv` 选择 `cell_id`。`data_row` 从表 III 第一条数据行开始计数。
2. `score_ids` 对应 `manifests/pe_scores.json` 中的评分条目；N1 每格关联六个条目，破折号不关联运行。
3. `config_ids` 对应 `manifests/configurations.json` 中的实际配置和原生输入。
4. 每个评分条目同时给出 `points_path`、`test_pressure_path` 和 `reference_pressure_path`。三个 CSV 的第 k 条数据行属于同一个评价点。
5. `source_aligned_file` 是原项目根目录 `paper_mainline` 下的相对来源；源文件哈希和打包数据哈希均保留。

评价点文件含 `r_m,y_m,z_m`，所有长度单位均为 m。三维沿主接收线的 `r_m` 对应原数据的沿 x 坐标。压力文件含 `real,imag`，保留归档数字字符串。时间约定、几何扩展、密度和起始场归一化转换已在原项目的对齐阶段完成。

相同字节内容的评价点和参考压力文件按 SHA-256 命名共享；PE 压力按评分 ID 存储，避免将完整历史输出目录重复收录。

## 指标与显示

逐点 SPL 差为 `20 log10(max(|p_test|,1e-30) / max(|p_ref|,1e-30))`，RMSE 为这些差值平方的等权均值再开平方。该幅值下限与原评分实现一致。脚本直接使用给定坐标上的物理声压。

脚本检查三份文件的点数、坐标唯一性与有限性。遇到非有限声压时脚本报错。声源注入点及其他预先规定不参与评分的点，已在归档评价点选择阶段排除。

显示采用原表的两位小数 ROUND_HALF_UP 规则；小于 0.005 dB 的值写为 `<0.01`。N1 区间取六个角度计算值的最小值和最大值。破折号表示该方法结果在表 III 中未报告。

## 算例设置

- C3/C4 的 WAMPE 在 30 Hz 使用 55:5:2000 m，在 90 Hz 使用 52:2:500 m；其他方法的同期取点不同。
- C7 100 Hz 的评分参考场使用 M=300、N=1600；C8 100 Hz 使用 M=300、N=3200。参考检查的两级配置在 `reference_checks.json` 中另列。
- C9 LSS-FD 的 3D 基线使用 0.04° 方位步长。C9 四种方法/模式使用相同的 479 个 SI 评价坐标。
- C9 使用归档 SI 参考场计算误差，参考检查列按原表记为 Unverified。
- N1 使用 20°、30°、40°、50°、60°、70° 六个截断角及原计划中明确列出的共同评价点。

## Python 接口

`compute_scores(repo_root, case=None)` 返回 164 个评分字典（或所选算例），每个包含 `score_id`、`config_id`、算例、频率、深度、模式、方法、角度、点数和 `rmse_db`。

`table_cells(repo_root, scores)` 根据这些计算结果返回表格单元格，显示字段名为 `value`，并给出 `rmse_min_db` 与 `rmse_max_db`。
