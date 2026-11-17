# 表 III 复现仓库

本仓库对应论文 *Accuracy and Applicability of Numerical Parabolic Equation Methods for Underwater Acoustic Propagation* 的 Table III，提供五种 PE 实现的参数、原生输入、起始场、评分参考声压、准确评价点及重新计算脚本。

- 75 组基线配置，另有 N1 的 54 次角度配置。
- 110 个普通 PE 数值和 9 个 N1 区间，另保留 51 个未报告方法格。
- 23 个参考检查条目，包括数值检查及 Analytical / Unverified 标记。
- 相同输入、评价点和参考声压按内容共享，完整历史运行目录不重复收录。

**整理状态**：2026-11-17 按作者要求整理归档数据；只做结构、路径、文件校验和及脚本语法检查，未重新运行求解器、评分脚本或再次比较数值结果。`expected/` 保存原记录，计算入口不使用这些值生成结果。

## 快速开始

Python 3.10 或以上。只计算 PE RMSE 使用 Python 标准库；完整表还需 NumPy、SciPy。

```bash
git clone https://github.com/Zhizhen-W/pe-table3-reproducibility.git
cd pe-table3-reproducibility
python -m pip install -r requirements.txt
python scripts/verify_package.py --checksums
python scripts/reproduce_table3.py
```

生成 `results/table3.csv`、`results/table3.md`、逐项 PE 评分和参考检查表。C3 原归档未保留粗级参考场，因此完整入口会按原实现与参数重新计算 C3 的两级 DGM 场；其余数值参考检查直接读取打包的成对声压。该计算只在读者执行时发生。

```bash
# 仅重新计算 PE 评分，不进行任何参考求解
python scripts/reproduce_table3.py --pe-only

# 只处理一个算例
python scripts/reproduce_table3.py --case C8 --output-dir results/C8
```

## 从一个表格数值找到全部材料

例如 C8、100 Hz、150 m 接收线上的 SSP：

```bash
python scripts/inspect_result.py --case C8 --frequency 100 --depth 150 --method SSP
```

输出该结果的配置、输入、起始场、参考声压、评价点文件和参考检查说明。所有运行路径均指向本仓库；`source_path` 等来源字段相对于原项目根目录 `paper_mainline/`，不要求读者拥有原项目。

| 文件 | 用途 |
|---|---|
| [table3_cells.csv](manifests/table3_cells.csv) | 34 行 × 5 种方法的单元格，关联评分与配置 ID |
| [configurations.json](manifests/configurations.json) | 实际参数、原生输入及运行来源 |
| [pe_scores.json](manifests/pe_scores.json) | 每个评分的准确评价点、测试与参考复声压 |
| [reference_checks.json](manifests/reference_checks.json) | 参考检查两级配置、数据、评价域和聚合方式 |
| [case_map.csv](manifests/case_map.csv) | 论文算例与原项目命名映射 |

压力和评价点 CSV 的第 k 行属于同一个样本。数据保留物理复声压，评分不做增益或相位拟合，也不静默删除非有限值。N1 区间由六个截断角的计算值汇总。

## 原生 PE 输入

```bash
python scripts/stage_inputs.py C8_f100_SSP_2D --output work/C8_f100_SSP_2D
```

此命令仅恢复输入文件，不运行求解器。使用对应版本的外部程序，可根据配置中的运行记录重算。程序接口和构建修改见 [THIRD_PARTY.md](THIRD_PARTY.md)；本版本的统一自动入口覆盖归档声压评分，并未将所有第三方求解器包装为自动安装与重跑流程。

## 阅读说明

- [配置与输入](docs/configuration-guide.md)
- [PE 评分](docs/pe-score-guide.md)
- [参考检查](docs/reference-guide.md)
- [复现范围与限制](docs/reproduction-scope.md)
- [许可证适用范围](LICENSE_SCOPE.md)

C7/C8 的评分参考场与参考收敛检查所用场分开记录。C9 SI 原始生成参数与收敛性仍未核实，保留 Unverified。C1 起始场的归档来源与当前论文概括性文字存在差异，见复现范围说明。

引用时请注明论文和实际使用的固定仓库版本。仓库提供 CITATION.cff；没有预设论文 DOI 或数据 DOI。
