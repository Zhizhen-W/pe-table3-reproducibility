# 公开 3D 参考数据来源

- 仓库：https://github.com/kaustikos/MPE （Mode parabolic equations 的 MATLAB 补充材料）
- 提交：`0c48133712c4de74683fcc6960ebb1b02575726a`（2019-11-26，作者 kaustikos）
- 获取日期：2026-10-08，`git clone --depth 1`，脚本见 `scripts/fetch_published_reference.sh`
- 许可证：仓库未包含 LICENSE 文件，再分发许可**未声明**。此处仅保存三份小型数值文件用于学术比对，并注明出处；如需公开发布数据包，应先联系作者或改为下载脚本。

| 文件 | SHA-256 | 内容 |
|---|---|---|
| `cross_wedge_ASA.TL` | `ee2d63b75632aa0121a0c39f4708227ab62af1c397fb414513650e1447b68654` | 跨坡线 y = 0、z_r = 30 m、z_s = 100 m，0–25 km，500 行：x [km]、20log10\|p\|（负值，dB re 1 m）、复压（MATLAB `a+bi` 格式） |
| `TLy_x10km` | `e9211f36b2bd914d23af8f54713ef696a7d7b9a47e6a2e346daf4f27d4e970fb` | x = 10 km 处沿坡剖面（y 坐标偏移 4 km，需减去 20log10(4π)） |
| `TLy_x25km` | `a6e2bcb383dd5769c8892d6c1ec55261c71cc2d173241418ddcf433bfe2e4a57` | x = 25 km 处沿坡剖面（同上） |

## 方法与对应文献

- 仓库 README 说明 `ASA_wedge_kj/` 中保存了“reference solutions”。`CPC_ex2_wedge_raystarter.m` 将 `cross_wedge_ASA.TL` 作为模态抛物方程结果的对照曲线。
- 对应论文：P. S. Petrov 等，预印本 BUW-IMACM 19/30（2019），https://imacm.uni-wuppertal.de/fileadmin/imacm/preprints/2019/imacm_19_30.pdf ，正式版见 J. Sound Vib. 484, 115526 (2020)。预印本 Fig. 6 中的“SI”（source images，源像法）曲线与此文件一致，所用方法为 Tang 等的修正源像法（Acoust. Phys. 64, 225 (2018)）。
- 环境：25 Hz，水体 1500 m/s、1 g/cm³，海底 1700 m/s、1.5 g/cm³，源处水深 200 m，坡度 tan = 0.05。同目录 `kj_wedge_att.txt` 在 h = 200 m 处给出的复模态波数为 k1 = 0.1038243 + 7.315e-6i、k2 = 0.1010523 + 2.806e-5i、k3 = 0.0962253 + 7.393e-5i，与本 case 的 `modes.py` 在 0.5 dB/λ 下的计算值（0.1038240 + 7.298e-6i 等）一致到 1e-5 量级，由此确认海底衰减为 0.5 dB/λ。
- 不确定性：作者未给出源像解的数值收敛误差。本 case 用独立实现的 3D 绝热简正波参考（`src/case08_3d_wedge/adiabatic3d.py`）对其做交叉检验，结果见 README。
