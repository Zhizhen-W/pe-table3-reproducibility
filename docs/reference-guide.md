# 表 III 参考解检查

本目录对应表 III 的 Reference verification 列，共 23 个算例—频率条目。条目与文件的对应关系保存在 `manifests/reference_checks.json`。`expected/reference_checks.csv` 仅保存论文显示值，评分脚本不读取该文件作为计算结果。

## 运行

在仓库根目录执行：

```bash
python scripts/score_references.py --output results/reference_checks.csv
```

只计算一个算例，例如 `--case C8`。入口也提供 `compute_reference_checks(root, case=None)`，返回包含 `D_SPL_db`、`display`、`n_points` 和逐接收线结果的字典列表。

需要 Python、NumPy。C3 还需要 SciPy。C3 的三个频率会在读者执行时进行 DGM 波数积分；其余数值参考检查直接读取已归档的成对复声压，不需要重新运行外部求解器。C1、N1 返回 Analytical，C9 返回 Unverified。

本次仓库整理只读取、选取和压缩归档数据，并检查路径、数组形状和脚本语法；未执行此评分命令、重新运行求解器或再次比较数值结果。

## 数据格式与计算范围

`data/references/checks/*.npz` 保存 `r_m`、`z_m` 和二维复数阵列 `p_coarse`、`p_fine`，数组下标为 `[depth, range]`。坐标是计算评价点，单位为 m。SPL 差按 `20 log10(|p_coarse|/|p_fine|)` 计算，幅值下限与项目指标函数相同，为 `1e-30`。指定评价点有非有限值时脚本报错，不静默删点。

| 算例 | 参考检查与取点 | 聚合规则 |
|---|---|---|
| C2 | 30/90/200 Hz 模态数分别为 128→256、144→288、173→346；192/112/223 点 | 单条 z=100 m 接收线 RMS |
| C3 | DGM 两级窗口为 200/400 km，轮廓参数 15/20，附加波数上限 0.4/0.8 rad/m；30 Hz 为 r=50:5:2000 m，90/200 Hz 为 r=50:2:500 m | z=50 m 接收线 RMS，包含 r0=50 m |
| C4 | 同类 DGM 两级设置；30 Hz 为 r=55:5:2000 m，90/200 Hz 为 r=52:2:500 m | 分别计算 z=50、100 m 两条线的 RMS，再取较大值 |
| C5 | SCOOTER/FIELDS L2→L3；r=1:0.1:100 km，每线 991 点 | 分别计算 z=1000、2500 m 两条线的 RMS，再取较大值 |
| C6 | 25 Hz 为 M60/N400→M90/N800，r=56:6:3998 m；100 Hz 为 M300/N1600→M300/N3200，r=51.5:1.5:3999.5 m | 分别计算 z=30、150 m 两条线的 RMS，再取较大值 |
| C7 | 25 Hz 为 M60/N400→M90/N800；100 Hz 为 M300/N3200→M300/N6400 | r=56:6:3998 m，z=1:1:400 m，263200 点整体 RMS |
| C8 | 25 Hz 为 M60/N400→M90/N800；100 Hz 为 M300/N12800→M300/N25600 | 与 C7 相同的全场评价网格 |

C6 的两条接收线及 C7/C8 的整场数组从原生 COUPLE.CPR 提取。COUPLE 用 float32 存储距离坐标，按原评价脚本吸附回 25 Hz 的 2 m 或 100 Hz 的 0.5 m 输出格点后，选取表列评价坐标；没有对声压做插值。原生 COUPLE 输入位于 `data/references/inputs/`，相同内容的文件只存一份，清单保留每种用途的引用。

C5 数组来自原 `receiver_lines.npz`，转换为论文约定时使用 `-conjugate`。两级使用同一转换，因此声压幅值之比不变。

## C3 原始粗场未保存

C3 原始文件仅保存了细级复声压以及两级差值的结果，没有保存粗级场。细级 CSV 在导出时也采用了有限位数。因此仓库保留细级声压供追溯，并提供原作者编写的 `implementations/dgm_layered_ffp.py` 和每个频率的两级参数。评分入口实际调用该实现重新生成两级场，再计算 SPL RMS；不会从已记录的差值反推或伪造粗场。数值计算只在读者主动执行入口时发生。

`implementations/dgm_lossy.py` 是 C4 归档场使用的有损分层 DGM 实现，作为方法追溯材料保留。C4 默认评分直接使用归档的两级场。

## 评分参考场与收敛检查不同

C7 在 100 Hz 的 PE 评分参考为 M300/N1600，但这里的检查为 N3200→6400。C8 在 100 Hz 的 PE 评分参考为 M300/N3200，但这里的检查为 N12800→25600。清单中 `scoring_configuration` 与 `check_pair` 分开记录；相应 COUPLE 输入分别保留。这些后续检查差值不能直接作为早期评分参考场具有同等误差水平的证明。

C9 的 `published_si/cross_wedge_ASA.TL` 是项目实际使用的公开参考数据快照，原来源、版本和校验和见同目录 `PROVENANCE.md`。PE 评分使用第三列复声压与 479 个实际坐标，不从第二列已舍入的 TL 值重建复声压。该 SI 文件的原始生成离散参数及收敛性尚未核实，因此此处没有生成器或虚构的两级检查。

所有 `source_path` 均相对于原项目 `paper_mainline/`，仅用于来源追溯；运行脚本只读取本复现仓库内的相对路径。
