# 程序来源与构建范围

归档声压评分只依赖本仓库 Python 代码及 NumPy/SciPy，不需要安装原生 PE 程序。原生输入恢复入口仅准备工作目录；重新运行求解器需使用对应构建及接口。

| 实现 | 本研究使用的来源与关键差异 |
|---|---|
| SSP / RAM 1.5 | OALIB RAM 加外部起始场接口及水体吸收剖面支持；部分配置使用不同容量构建 |
| LSS-FD / FOR3D Laurel | 外部起始场与刚性底边界修改；C9 使用单独的三维源代码及容量设置 |
| CT-S / SMPE | 固定上游提交，使用外部起始场 Octave 驱动与兼容文件 |
| SSF / UMPE 1.1 | 固定源码包，使用外部起始场接口与对应的二进制输出读取方式 |
| WAMPE / AMPLE | 固定上游提交及依赖，使用 release_density 修改版本 |
| SCOOTER / FIELDS | 固定 Acoustics Toolbox 包；SCOOTER 后处理使用 FIELDS |
| COUPLE07 | 本仓库保存实际 COUPLE.DAT、评分/检查配置及已提取的复声压 |

程序地址、已知提交号、归档哈希和许可记录见 [sources.json](third_party/sources.json)。这些记录来自本地研究档案，未在本次整理中重新下载或重新构建。

## 收录的扩展

- `third_party/smpe/` 保留已使用的外部起始场代码及 Octave 兼容文件；它们保留 SMPE 源码的 GPL-3.0-or-later 声明，随附 GPL 文本。上游谱方法代码从 sources.json 指定提交取得。
- `third_party/ample/` 保留 MIT 许可、源码修改补丁、上游及模态依赖提交。补丁从归档差异中仅保留 release_density 部分，应用前应先取得记录中的源码版本；依赖保留各自许可证。
- DGM 实现位于 `data/references/implementations/`，为研究项目自身的参考计算代码。C3 评分入口会在读者运行时调用它重建原两级场。
- C9 SI 快照的原来源与引用见 `data/references/published_si/PROVENANCE.md`。

RAM/FOR3D 的本地源快照没有明确 LICENSE；本仓库不把它们重新标记为 MIT，也未整体复制其源码。UMPE、COUPLE 和 Acoustics Toolbox 的使用及再分发应遵循各自原始发行条款。根目录 LICENSE 的适用范围见 LICENSE_SCOPE.md。

各配置 native_commands 中的历史命令用于说明程序参数，相对路径表示原项目内位置，不能直接作为本仓库可执行路径。请先用 stage_inputs.py 恢复输入，再调用本机对应构建。自动读取新原生输出、重新评分的跨程序流水线未作为本版本统一入口；归档复声压的重新评分入口完整提供。
