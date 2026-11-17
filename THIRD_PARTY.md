# 程序来源与运行准备

归档声压评分使用本仓库 Python 代码及 NumPy/SciPy。原生求解器运行采用以下版本和接口，通过 `stage_inputs.py` 准备工作目录。

| 实现 | 本研究使用的来源与关键差异 |
|---|---|
| SSP / RAM 1.5 | OALIB RAM 加外部起始场接口及水体吸收剖面支持；部分配置使用不同容量构建 |
| LSS-FD / FOR3D Laurel | 外部起始场与刚性底边界修改；C9 使用单独的三维源代码及容量设置 |
| CT-S / SMPE | 固定上游提交，使用外部起始场 Octave 驱动与兼容文件 |
| SSF / UMPE 1.1 | 固定源码包，使用外部起始场接口与对应的二进制输出读取方式 |
| WAMPE / AMPLE | 固定上游提交及依赖，使用 release_density 修改版本 |
| SCOOTER / FIELDS | 固定 Acoustics Toolbox 包；SCOOTER 后处理使用 FIELDS |
| COUPLE07 | 本仓库保存实际 COUPLE.DAT、评分/检查配置及已提取的复声压 |

程序地址、已知提交号、归档哈希和许可记录见 [sources.json](third_party/sources.json)。

## 收录的扩展

- `third_party/smpe/` 保留已使用的外部起始场代码及 Octave 兼容文件；它们保留 SMPE 源码的 GPL-3.0-or-later 声明，随附 GPL 文本。上游谱方法代码从 sources.json 指定提交取得。
- `third_party/ample/` 保留 MIT 许可、源码修改补丁、上游及模态依赖提交。补丁从归档差异中仅保留 release_density 部分，应用前应先取得记录中的源码版本；依赖保留各自许可证。
- DGM 实现位于 `data/references/implementations/`，为研究项目自身的参考计算代码。C3 参考检查调用该实现计算两级声压场。
- C9 SI 快照的原来源与引用见 `data/references/published_si/PROVENANCE.md`。

RAM/FOR3D 源码的许可记录见 `sources.json`。各第三方程序及依赖遵循其原始发行条款，根目录许可证的适用范围见 [LICENSE_SCOPE.md](LICENSE_SCOPE.md)。

各配置的 `native_commands` 记录程序参数和原项目相对路径。运行时先用 `stage_inputs.py` 恢复输入，再将命令中的程序和路径替换为本机位置，调用对应构建。归档复声压的评分入口为 `scripts/reproduce_table3.py`。
