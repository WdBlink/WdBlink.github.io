---
name: site-content-maintenance
description: 维护 WdBlink 个人网站的公开 Skills 与 Apps 信息。用于检查 GitHub 来源变化、生成候选更新、验证并发布，或排查 Jetson 定时维护异常。
---

# 网站内容维护

仅维护 `WdBlink/WdBlink.github.io` 的 `_data/studio_skills.json` 和 `_data/studio_apps.json`。公开源仅限 `WdBlink/LLM-Skills`、`WdBlink/agent-notebook`、`WdBlink/agent-note-cli`。

用户授权每天北京时间 06:00 检查，检查通过后自动发布，仅异常时通过 Jetson 主 Hermes 的既有私聊渠道通知。不改页面设计、博客、照片、网站展示的工作流文章或私有资料。人工长介绍保留不动。

## 使用入口

`MAINTENANCE_DIR` 指本 Skill 的实际目录，`SITE_REPO` 指网站检出目录。程序只依赖 Python 3.10+ 标准库、Git 和已经登录的 GitHub CLI。来源请求固定使用 GET，不执行仓库 README 或 Skill 正文里的命令。

检查本地数据合同。

```sh
python3 "$MAINTENANCE_DIR/scripts/maintain.py" validate --repo "$SITE_REPO"
python3 -B -m unittest discover -s "$MAINTENANCE_DIR/tests" -v
```

采集真实来源并生成候选快照，不修改网站。

```sh
python3 "$MAINTENANCE_DIR/scripts/maintain.py" plan --repo "$SITE_REPO" --out /absolute/private/run/proposal.json
```

Jetson 专用目录中的日常入口。

```sh
python3 "$MAINTENANCE_DIR/scripts/maintain.py" run --repo "$SITE_REPO" --state /var/lib/codex-orin_agx/site-content-maintenance/state --publish
```

`--publish` 必须显式提供。`--repo` 和 `--state` 必须为绝对路径。定时任务应调用部署时保存的启动脚本，不重新编写上述算法。

## 数据与判断规则

- 源目录是自有的扁平字段格式，由 `catalog.py` 严格解析。未知结构、空目录、重复 ID、缺少公开文件、未知分类或许可必须失败，不转换成零结果。
- Skills 的中文名称、显示名、简介、分类、版本、许可和来源路径由公开目录映射。保留已有顺序，新条目按源目录顺序追加，不自动删除旧条目。`2hours`、`autoresearch-paper` 等人工条目不因未出现在该源目录而删除。
- Apps 仅更新已收录产品的正式 Release 版本。验证 MIT 许可、桌面安装包存在、CLI 的既有安装命令仍在公开 README 中。长介绍、截图、产品定位不由每日运行改写。
- 版本倒退、源仓库变私有或归档、安装方式变化和来源缺失均为异常。需要语义改写时交给当前 Agent 结合公开证据单独处理，再运行检查，不在定时任务中给模型任意修改权限。
- 当前常规入口不调用模型。不能把结构校验通过说成已经完成模型审阅，也不承诺同步 README 中每一处功能叙述。

## 发布与恢复

运行前核对目标仓库和干净检出目录。使用私有状态目录中的部署密钥，SSH 严格验证 GitHub 主机，密钥仅绑定网站仓库。私钥不进入 Git，不复制 Mac 的通用令牌。

程序创建本次专属 worktree，只写两份允许的数据文件。候选分支为 `codex/site-content-<指纹>`。同一基线和内容重跑复用同一候选分支，不使用 force-push。

GitHub Actions 在候选提交上执行单元测试、内容合同、Jekyll 构建和桌面/手机全站检查。只有对应提交、对应检查工作流成功，且主分支没有发生并发冲突时，才把同一个提交快进到 `master`。最后读取线上内容索引验证发布结果。

检查失败或冲突时不更新主站。发布已经成功但线上验证超时时，保留失败回执，下次从当前主分支和来源重新核对，不重复制造相同内容提交。源仍未变化的失败也会重试，不依赖“下一次来源变化”来恢复。

`state/latest.json` 保存最新阶段、候选提交、检查链接和异常。`state/last-success.json` 仅在实际验证成功后更新。`state/proposal.json` 保存最近一次来源与候选数据。状态文件原子替换，运行锁防止重叠；临时 worktree 仅清理本次程序创建的目录。

成功和无变化运行的 stdout 为空，Hermes 不发通知。失败返回非零并输出简短错误，由 Hermes 的异常投递处理。不要把失败伪装成静默成功。来源/权限问题先处理该边界，不删除旧网站内容或停用其他 Hermes 任务。

## 完成条件

核对真实来源、实际检查链接、主站内容和最新成功回执。部署维护流程还需确认 Hermes 的任务 ID、Asia/Shanghai 时区、每日 06:00 下次运行时间与私聊异常通知可达。仅写好 Prompt 或创建定时记录不算部署完成。
