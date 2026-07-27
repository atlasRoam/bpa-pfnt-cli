# BPA PFNT CLI

一个可直接在Windows上运行的BPA/PFNT命令行分发包，供潮流计算、分析报告、损耗分析、灵敏度分析和科学恢复智能体调用。

本仓库与[PF Convergence Agent](https://github.com/atlasRoam/pf-convergence-agent)分离维护：

- 本仓库提供`bpa_cli.exe`、PFNT运行环境和公开样例；
- 智能体主仓只包含源码，不直接捆绑BPA/PFNT；
- 用户通过环境变量把两个项目连接起来。

## 重要许可证说明

仓库中的MIT许可证仅覆盖atlasRoam拥有版权的CLI包装器、校验脚本、清单和文档。

`runtime/pfnt/`中的PFNT程序、DLL以及部分原始样例属于第三方或遗留资产，**没有被MIT重新授权**。请阅读[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。使用者应自行确认其使用和再分发符合原权利人的条款及当地法律。

## 目录结构

```text
bpa-pfnt-cli/
├── bpa_cli.exe                 # 64位命令行入口
├── runtime/
│   └── pfnt/
│       ├── pfnt.exe            # 32位PFNT计算内核
│       ├── *.dll               # 运行依赖
│       ├── Pfcard.def
│       └── Nametab.mdb
├── samples/
│   ├── ieee90/                 # IEEE 9节点演示数据
│   └── library/                # 遗留样例库
├── MANIFEST.json               # 文件大小和SHA-256清单
├── scripts/verify_distribution.py
└── README.md
```

`runs/`不会提交到GitHub。每次计算产生的DAT、BSE、PFO、日志和分析报告都只保留在用户本机。

# 一、下载

## 方法A：Git克隆

```powershell
git clone https://github.com/atlasRoam/bpa-pfnt-cli.git
cd bpa-pfnt-cli
```

## 方法B：GitHub源码压缩包

在GitHub仓库页面选择：

```text
Code → Download ZIP
```

解压到一个没有中文和特殊符号的短路径，例如：

```text
D:\Tools\bpa-pfnt-cli
```

不建议放入系统目录或需要管理员权限的目录。

# 二、验证下载完整性

需要Python 3.11或更高版本：

```powershell
python .\scripts\verify_distribution.py
```

成功时显示：

```text
distribution-verification: PASS
```

校验失败时不要继续运行。重新下载并确认文件没有被杀毒软件、同步软件或手工操作修改。

# 三、第一次运行

在PowerShell中进入仓库目录：

```powershell
cd D:\Tools\bpa-pfnt-cli
.\bpa_cli.exe --help
```

如果Windows阻止运行：

1. 确认文件来自本仓库；
2. 先完成SHA-256校验；
3. 在文件属性中检查是否存在“解除锁定”；
4. 不要关闭系统安全软件或全局降低安全策略。

# 四、运行公开样例

## 完整分析套件

```powershell
.\bpa_cli.exe suite ".\samples\ieee90\ieee90.dat" --all
```

命令会在`runs/`下新建独立目录，并执行适用于该样例的任务，例如：

- 基础潮流；
- 分析报告；
- 线路损耗；
- 变压器损耗；
- 损耗灵敏度；
- Q–V和P–V分析；
- 节点和线路灵敏度。

最终结果通常包括：

```text
*.dat
*.bse
*.pfo
*.err
*.txt
*.json
*.csv
```

## 自定义求解参数

```powershell
.\bpa_cli.exe suite ".\samples\ieee90\ieee90.dat" `
  --solution "ai=OFF,ltc=ON,decoupled=10,current=0,newton=30,busv=.005,aipower=.005,tx=.005,q=.005,opcut=.0001"
```

常用参数：

| 参数 | 作用 |
|---|---|
| `ai` / `ai_control` | 自动控制方式 |
| `ltc` | 有载调压变压器控制 |
| `decoupled` / `pq` | 解耦迭代次数 |
| `current` | 电流法迭代次数 |
| `newton` | 牛顿法迭代次数 |
| `busv` | 节点电压收敛容差 |
| `aipower` | 自动控制功率容差 |
| `tx` | 变压器控制容差 |
| `q` | 无功容差 |
| `opcut` | 开断判断容差 |

# 五、常用分析命令

## Q–V分析

```powershell
.\bpa_cli.exe suite ".\samples\ieee90\ieee90.dat" `
  --qv "bus=STATIONA,base=230,v=0.98:1.05:0.01"
```

## P–V分析

```powershell
.\bpa_cli.exe suite ".\samples\ieee90\ieee90.dat" `
  --pv "bus=STATIONA,base=230,p=0:100:20"
```

## 线路和变压器损耗

```powershell
.\bpa_cli.exe suite ".\samples\ieee90\ieee90.dat" `
  --line-loss --tx-loss
```

## 损耗灵敏度

```powershell
.\bpa_cli.exe suite ".\samples\ieee90\ieee90.dat" `
  --loss-sensitivity `
  --loss-sensitivity-opts "ltc=ON,ai_control=CON,q_shunt=ADJ,qgen=ADJ,zones=01"
```

## 批量负荷倍率

```powershell
.\bpa_cli.exe suite ".\samples\ieee90\ieee90.dat" `
  --batch-load-scale "p=0.9,1.0,1.1,q=same"
```

## 原始BPA控制语句

```powershell
.\bpa_cli.exe suite ".\samples\ieee90\ieee90.dat" `
  --change-file ".\my_changes.txt"
```

固定列BPA卡片对空格敏感，复杂操作优先放入文件，不建议直接在终端中反复转义。

# 六、连接PF Convergence Agent

先分别克隆两个仓库：

```powershell
git clone https://github.com/atlasRoam/bpa-pfnt-cli.git
git clone https://github.com/atlasRoam/pf-convergence-agent.git
```

设置当前PowerShell会话使用的CLI路径：

```powershell
$env:PFCA_BPA_CLI = (Resolve-Path ".\bpa-pfnt-cli\bpa_cli.exe").Path
```

如果希望以后启动PowerShell时仍然有效：

```powershell
[Environment]::SetEnvironmentVariable(
  "PFCA_BPA_CLI",
  (Resolve-Path ".\bpa-pfnt-cli\bpa_cli.exe").Path,
  "User"
)
```

设置后必须重新打开终端或重新启动桌面程序。

进入智能体源码目录：

```powershell
cd .\pf-convergence-agent
uv sync --extra api --extra analysis --extra dev
npm ci
npm run dev
```

首次使用还需要在软件设置中填写：

- OpenAI兼容的HTTPS接口地址；
- 模型名称；
- API Key。

API Key由Electron `safeStorage`加密保存。主仓没有默认模型供应商，也不会把Key写入源码目录。

随后在软件的算例库中导入你有权使用的DAT文件，新建会话并描述调整约束，例如：

```text
保持拓扑、负荷和发电计划不变，自动诊断并调整到稳定收敛，使用真实BPA/PFNT完成独立复算。
```

# 七、使用自己的DAT

请先复制原文件，始终保留不可修改的原始版本。

建议目录：

```text
D:\Cases\project-name\input.DAT
```

单独使用CLI时：

```powershell
.\bpa_cli.exe suite "D:\Cases\project-name\input.DAT" --all
```

智能体模式下，通过软件算例库导入，不要把真实工程DAT提交到GitHub。

# 八、常见问题

## `bpa_cli.exe`找不到

必须在当前目录加`.\`：

```powershell
.\bpa_cli.exe --help
```

## PFNT启动失败

检查以下文件仍在相对位置：

```text
runtime\pfnt\pfnt.exe
runtime\pfnt\*.dll
runtime\pfnt\Pfcard.def
runtime\pfnt\Nametab.mdb
```

不要单独移动`bpa_cli.exe`。

## 智能体提示找不到BPA CLI

检查：

```powershell
$env:PFCA_BPA_CLI
Test-Path $env:PFCA_BPA_CLI
```

修改用户环境变量后需重新启动软件。

## 运行结果在哪里

默认在当前分发包的：

```text
runs\suite_时间_算例名\
```

`runs/`已被Git忽略，不会上传。

## 中文或长路径异常

遗留PFNT内核对路径兼容性有限，优先使用短英文路径：

```text
D:\Tools\bpa-pfnt-cli
D:\Cases\case1\input.DAT
```

## 能否用于生产系统

这是遗留计算内核和外部CLI包装。正式工程使用前应：

- 在隔离环境验证；
- 与权威基准结果交叉核对；
- 保存输入哈希和输出制品；
- 不直接覆盖原始DAT；
- 根据单位规章完成复核和审批。

# 九、隐私和安全

不要提交：

- 真实电网DAT/BSE/PFO；
- 用户名和绝对工作站路径；
- API Key或模型设置；
- 智能体会话、Checkpoint和Trace；
- `runs/`中的运行产物。

本仓库不包含遥测代码，也不会连接atlasRoam控制的统计服务器。

# 十、相关项目

- [PF Convergence Agent](https://github.com/atlasRoam/pf-convergence-agent)：科学分析、约束调整、反思、回滚和独立复算智能体。
- [BPA PFNT CLI](https://github.com/atlasRoam/bpa-pfnt-cli)：本仓库，提供外部计算入口。
