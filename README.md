# 表 III 复现仓库

本仓库对应论文 *Accuracy and Applicability of Numerical Parabolic Equation Methods for Underwater Acoustic Propagation* 的 Table III，提供五种 PE 实现的参数、原生输入、起始场、评分参考声压、准确评价点及重新计算脚本。

- 75 组基线配置，另有 N1 的 54 次角度配置。
- 110 个普通 PE 数值和 9 个 N1 区间，另保留 51 个未报告方法格。
- 23 个参考检查条目，包括数值检查及 Analytical / Unverified 标记。
- 相同输入、评价点和参考声压按内容共享。

当前版本为 [v1.0.1](https://github.com/Zhizhen-W/pe-table3-reproducibility/releases/tag/v1.0.1)。`expected/` 保存论文报告值，供结果对照。

## 快速开始

Python 3.10 或以上。只计算 PE RMSE 使用 Python 标准库；完整表还需 NumPy、SciPy。

```bash
git clone https://github.com/Zhizhen-W/pe-table3-reproducibility.git
cd pe-table3-reproducibility
python -m pip install -r requirements.txt
python scripts/verify_package.py --checksums
python scripts/reproduce_table3.py
```

生成 `results/table3.csv`、`results/table3.md`、逐项 PE 评分和参考检查表。C3 的参考检查由 DGM 实现生成两级场后计算；其余数值参考检查读取归档的成对声压。

```bash
# 计算 PE 评分
python scripts/reproduce_table3.py --pe-only

# 只处理一个算例
python scripts/reproduce_table3.py --case C8 --output-dir results/C8
```

## 从一个表格数值找到全部材料

例如 C8、100 Hz、150 m 接收线上的 SSP：

```bash
python scripts/inspect_result.py --case C8 --frequency 100 --depth 150 --method SSP
```

输出该结果的配置、输入、起始场、参考声压、评价点文件和参考检查说明。运行路径相对于本仓库；`source_path` 等来源字段相对于原项目根目录 `paper_mainline/`，用于追溯原始记录。

| 文件 | 用途 |
|---|---|
| [table3_cells.csv](manifests/table3_cells.csv) | 34 行 × 5 种方法的单元格，关联评分与配置 ID |
| [configurations.json](manifests/configurations.json) | 实际参数、原生输入及运行来源 |
| [pe_scores.json](manifests/pe_scores.json) | 每个评分的准确评价点、测试与参考复声压 |
| [reference_checks.json](manifests/reference_checks.json) | 参考检查两级配置、数据、评价域和聚合方式 |
| [case_map.csv](manifests/case_map.csv) | 论文算例与原项目命名映射 |

压力和评价点 CSV 的第 k 行属于同一个样本。评分直接使用物理复声压；样本检查规则见 PE 评分指南。N1 区间由六个截断角的计算值汇总。

## 原生 PE 输入

```bash
python scripts/stage_inputs.py C8_f100_SSP_2D --output work/C8_f100_SSP_2D
```

此命令将所选配置的输入恢复到指定工作目录。随后按配置中的运行记录调用对应版本的求解器。程序来源、接口和构建修改见 [THIRD_PARTY.md](THIRD_PARTY.md)。

## 阅读说明

- [配置与输入](docs/configuration-guide.md)
- [PE 评分](docs/pe-score-guide.md)
- [参考检查](docs/reference-guide.md)
- [复现流程与数据对应](docs/reproduction-scope.md)
- [许可证适用范围](LICENSE_SCOPE.md)

各算例的起始场、评价坐标及参考配置见[复现流程与数据对应](docs/reproduction-scope.md)。

引用信息见 `CITATION.cff`，请注明论文和实际使用的仓库版本。
