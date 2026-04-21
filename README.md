# 标签信息修复 — 使用说明

## 简介
脚本目的：
- 按照文件名格式 `歌曲名-歌手` 将 |/Artist 写入文件；
  - 同时清除部分其它值为 `kuwo` 的元数据字段。
- 由于musicfree下载的音频文件有时候会出现标签错误，显示为空或者kuwo，在其它软件打开音乐时会显示错误的音乐名和歌手，因此创建这个脚本。
- 因为我不会python，所以这个仓库的脚本全部由AI完成，我只修改了readme文件。
- 当音频文件的title为空或其值为 `kuwo`（不区分大小写、允许前后空格）时


## 前提
- 已在系统 PATH 中安装并可从命令行调用 `ffmpeg` 与 `ffprobe`，或将二进制文件放在与脚本相同目录。  
- 只能确定制作时使用的虚拟环境版本(3.13.12)是可用的。

## 支持的文件类型
默认处理的扩展名（可在脚本中修改）：`mp3`, `flac`, `m4a`, `aac`, `wav`, `wma`, `ogg`。
## 测试时使用的文件和修复结果
|文件名|识别歌名|识别歌手|
|:--------------------------------------|:------------------|:---------------------|
Always Online-林俊杰.flac	|Always Online	|林俊杰
Baby-Justin Bieber, Ludacris.flac	|Baby	|Justin Bieber, Ludacris
Dilemma (Explicit)-Nelly, Kelly Rowland.flac	|Dilemma (Explicit)	|Nelly, Kelly Rowland
Good Time-Owl City, Carly Rae Jepsen.flac	|Good Time	|Owl City, Carly Rae Jepsen
Insomnia-Craig David.flac	|Insomnia	|Craig David
Love Story-Taylor Swift.flac	|Love Story	|Taylor Swift
See You Again-Wiz Khalifa, Charlie Puth.flac	|See You Again	|Wiz Khalifa, Charlie Puth
Something Just Like This-The Chainsmokers, Coldplay.flac	|Something Just Like This	|The Chainsmokers, Coldplay
TA-不是花火呀.flac	|TA	|不是花火呀
Take Me Hand-DAISHI DANCE (ダイシ・ダンス), Cécile Corbel.flac	|Take Me Hand	|DAISHI DANCE (ダイシ・ダンス), Cécile Corbel
The Theme From San Andreas-Michael Hunter.flac	|The Theme From San Andreas	|Michael Hunter
ありがとう… (谢谢…)-KOKIA (吉田亚纪子).flac	|ありがとう… (谢谢…)	|KOKIA (吉田亚纪子)
倒带-蔡依林.flac	|倒带	|蔡依林
给你呀 - 蒋小呢_FLAC.flac	|给你呀	|蒋小呢_FLAC
客官不可以-徐良, 小凌.ogg	|客官不可以	|徐良, 小凌
## 行为摘要
- 读取每个文件的 |（优先查找 `TAG:|`，其次查找 `|`）。
- 如果 | 为空或匹配 `kuwo`，脚本会将文件名按第一个 `-` 分割为 `歌曲名`（左侧）和 `歌手`（右侧）；
- 若文件名不含 `-`，则全部作为 |，Artist 留空。  
- 使用 `ffmpeg -c copy` 写入 metadata 到临时文件，再替换原文件。
- 写入成功时（若目标目录没有已存在的备份），脚本会创建同目录的 `.bak` 备份文件（仅在脚本逻辑触发时创建，且不会覆盖已存在的 .bak）。
# 脚本用法说明

本目录包含用于批量修复音频文件标签的 Python 工具与若干辅助脚本。

**主要脚本**
- `tag_fix.py`：基于 `mutagen` 的主修复脚本，
  - 按文件名 `歌曲名-歌手` 填充 |/Artist，默认在写入时创建 `.bak` 备份；
  - 支持 `-n/--dry-run`（仅预览）和 `-nb/--no-backup`（不创建备份）。
- `verify_tags.py`：使用已存在的 `.bak` 列表或文件集合读取写入后的 |/Artist，生成 `verify_tags.txt`（用于核验写入结果）。
- `verify_no_backup_check.py`：对不使用备份写入后的文件进行验证，输出 `verify_no_backup_result.txt`（会比较文件名与实际标签）。

（以上脚本均位于仓库根目录： [tag_fix.py](tag_fix.py), [verify_tags.py](verify_tags.py), [verify_no_backup_check.py](verify_no_backup_check.py)）

## 快速开始
0. 准备所需文件
- 把`tag_fix.py`和`requirements.txt`复制到要处理的歌曲所在目录
1. 安装依赖
```powershell
pip install -r requirements.txt
```
1. 先做预览（dry-run）：(显示要执行的命令，并不会真的修改文件)

```powershell
python tag_fix.py -n
```

3. 确认无误后写入（默认会创建 `.bak`）：

```powershell
python tag_fix.py
```

4. 若不想创建备份（请谨慎）：

```powershell
python tag_fix.py --no-backup
```

## 验证写入结果（可在文件管理器里面按照标题排序直接检查）

- 使用 `verify_tags.py` 对存在 `.bak` 的文件批量检查：

```powershell
python verify_tags.py
# 输出文件：verify_tags.txt
```

- 使用 `verify_no_backup_check.py` 检查无备份写入后的结果：

```powershell
python verify_no_backup_check.py
# 输出文件：verify_no_backup_result.txt
```
## 其他说明
- 备份：默认会为被修改的文件创建 `<file>.bak`，以便回退；若你使用 `--no-backup`，请先做好手动备份或仅在小批量样本上测试。 
- 编码：在 Windows 下控制台显示可能出现编码问题，但 `mutagen` 写入本地文件的标签通常使用 UTF-8/容器支持的编码，不影响文件内数据。

---
更新时间：2026-04-21
