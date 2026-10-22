# rw-modding-mcp 本项目部署说明

2026-10-22 已在本机项目中部署，四个工具均完成 stdio 实际调用验证。

## 部署位置与配置

- 上游：https://github.com/GMBOXMOD/rw-modding-mcp
- 本地检出：`文档 (不要打包)/工具/rw-modding-mcp/`
- 上游提交：`014dc92fb37d90c7ec028ff329a4b6843372867b`
- Python：本机 Python 3.12；依赖安装在工具自己的 `.venv/`，MCP SDK 为 2.3.0。
- Java：本机 Java 21；输入是 `E:/RustedWarfare_Reunion/game-lib.jar`。
- 反编译产物：工具的 `tools/jar/src/`，共 1,698 个 Java 文件。
- Codex 项目配置：根目录 `.codex/config.toml`，服务名 `rusted-warfare`。
- 环境变量 `RW_GAME_JAR` 指向本机游戏 JAR，用于键名交叉核对。
- 配置使用绝对路径，迁移项目或更换 Python 安装位置后需调整。

项目级配置按官方 OpenAI 文档配置，仅在受信任项目中加载：
https://developers.openai.com/codex/mcp

重新打开本项目并新建/重启 Codex 会话后加载服务。可在项目根目录运行 `codex mcp get rusted-warfare --json` 查看识别结果。当前会话中的工具列表不会因写入配置而自动增加；本次通过独立 MCP 客户端验证了实际配置。

## 使用范围

| 工具 | 用法 |
|---|---|
| `lookup_key` | 查字段拼写、节、类型、例子及各数据源收录情况 |
| `get_ref` | 查事件、函数、枚举、配对规则等结构化参考 |
| `search_source` | 搜索本机游戏版本的反编译索引，不搜索 MOD 配置 |
| `lint` | 检查指定文件/目录；路径优先使用绝对路径 |

MCP 服务启动目录已设为工作区根目录，因此也可以使用 `GW_BattleUniverse_DLC_0079/...` 等相对路径。上游 `RW_PROJECT_ROOT` 实际表示工具仓库根目录，用来寻找资料和源码；不要将它改成 MOD 根目录。

命令行检查也可直接使用（以下从项目根目录执行）：

```powershell
$env:PYTHONUTF8 = '1'
python '文档 (不要打包)/工具/rw-modding-mcp/bootstrap.py' --check --game 'E:/RustedWarfare_Reunion'
& '文档 (不要打包)/工具/rw-modding-mcp/.venv/Scripts/python.exe' '文档 (不要打包)/工具/验证_rw_mcp.py'
python '文档 (不要打包)/工具/rw-modding-mcp/tools/rw_lint.py' 'GW_BattleUniverse_DLC_0079/Units/BattleUnits/RGM_79'
```

按改动文件或目标包执行 lint。扫描单文件时，未在扫描范围内的宏、继承段和其他实体可能被报告为缺失；应扩大到相关包并人工追踪。全工作区扫描可能混入多包占位覆盖，不能以此判定游戏加载是否正确。

## Battle Universe 的本地适配

上游目录扫描仅纳入 `.ini`、`.template` 和 `mod-info.txt`，会漏掉本项目的 `.gw` 模板。已修改 `tools/rw_lint.py` 的 `collect_files()`，增加 `.gw` 扩展名。没有更改 MOD 文件。

改动保存在同目录 `rw-modding-mcp-gw.patch`。更新上游前检查本地差异，更新后重新确认 `.gw` 是否已被上游支持；不要反复或强行应用补丁。

独立的 `验证_rw_mcp.py` 从实际 `.codex/config.toml` 读取启动参数，检查握手、四个工具名、四项调用、有效 INI、仅含 `.gw` 的目录，以及真实吉姆目录读取。临时样本在系统临时目录中生成并清理。

本次验证结果：

- 上游直接调用自检：22 PASS / 0 FAIL（两个上游作者私有示例目录不存在，按原逻辑跳过）。
- 上游坏样本回归：8 PASS / 0 FAIL。
- 项目 stdio 验证：7 项通过。
- 吉姆目录抽样：扫描 2 个文件，0 个错误、4 个警告；只确认工具可用，没有自动修改或宣称这些警告均为真实缺陷。
- `pip check`：没有依赖冲突。

## 重新部署与更新

工具检出目录整体由项目 `.gitignore` 排除，避免将嵌套仓库、虚拟环境、下载器和游戏源码提交或打包。项目保留配置、补丁、依赖锁定清单和验证脚本。工具遵循上游 MIT 许可；参考表和游戏源码的权利分别归原作者。

新机器可按下面步骤恢复；已有检出目录时先检查本地改动，不要覆盖。

```powershell
$tool = '文档 (不要打包)/工具/rw-modding-mcp'
git clone https://github.com/GMBOXMOD/rw-modding-mcp.git $tool
git -C $tool checkout 014dc92fb37d90c7ec028ff329a4b6843372867b
git -C $tool apply --check ../rw-modding-mcp-gw.patch
git -C $tool apply ../rw-modding-mcp-gw.patch
python -m venv "$tool/.venv"
& "$tool/.venv/Scripts/python.exe" -m pip install --only-binary :all: -r '文档 (不要打包)/工具/rw-modding-mcp-requirements.lock'
python "$tool/bootstrap.py" --decompile --game 'E:/RustedWarfare_Reunion'
```

然后调整 `.codex/config.toml` 中的 Python、项目和游戏路径，运行验证脚本。反编译需 Java 17+；游戏更新后需要用 `--decompile --force --game ...` 重新生成索引并重启 MCP 服务。依赖锁定清单用于复现本次环境，不要在更新上游时无条件升级所有依赖。

## 结果边界

资料表可能有版本差异，lint 不会完整模拟继承、消息时序和游戏行为。保留 `AGENTS.md` 的静态检查与游戏内测试要求。工具报告只是排查线索，不得据此批量删除历史兼容流程或改写公共模板。

本次没有运行 `game_loadtest.py`、没有启动游戏加载测试、没有发布或打包 MOD。
