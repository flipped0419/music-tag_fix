# -*- coding: utf-8 -*-
"""
tag_fix.py
基于 mutagen 的标签修复脚本：
 - 从文件名 `song-artist` 提取 Title/Artist（若 Title 为空或为 "kuwo"）
 - 清除所有值为 "kuwo" 的标签字段
 - 默认创建 `<file>.bak` 备份，可通过 `--no-backup` 禁用
 - 支持预览模式 `-n/--dry-run`

用法示例：
  python tag_fix.py -n      # 仅预览
  python tag_fix.py         # 真正修改（会创建 .bak）

"""

from pathlib import Path
import argparse
import shutil
import sys
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from mutagen.asf import ASF
import sys

# 在 Windows/受限控制台中强制 stdout 使用 UTF-8，避免打印文件名时报错
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

EXTS_DEFAULT = ['.mp3', '.flac', '.m4a', '.aac', '.wav', '.wma', '.ogg']


def open_audio(path: Path):
    ext = path.suffix.lower()
    try:
        if ext == '.mp3':
            try:
                tags = EasyID3(str(path))
                return tags, 'easyid3'
            except ID3NoHeaderError:
                # try create tags
                audio = mutagen.File(str(path), easy=True)
                if audio is None:
                    return None, None
                try:
                    audio.add_tags()
                except Exception:
                    pass
                try:
                    tags = EasyID3(str(path))
                    return tags, 'easyid3'
                except Exception:
                    return audio, 'generic'
        elif ext == '.flac':
            audio = FLAC(str(path))
            return audio, 'flac'
        elif ext in ('.m4a', '.mp4'):
            audio = MP4(str(path))
            return audio, 'mp4'
        elif ext == '.ogg':
            audio = OggVorbis(str(path))
            return audio, 'ogg'
        elif ext == '.wma':
            audio = ASF(str(path))
            return audio, 'asf'
        else:
            audio = mutagen.File(str(path), easy=True)
            return audio, 'generic'
    except Exception:
        return None, None


def get_title(audio, fmt):
    if audio is None:
        return None
    try:
        if fmt == 'easyid3':
            return audio.get('title', [None])[0]
        elif fmt in ('flac', 'ogg', 'generic'):
            if audio.tags is None:
                return None
            return audio.tags.get('title', [None])[0]
        elif fmt == 'mp4':
            if not audio.tags:
                return None
            v = audio.tags.get('\u00a9nam')
            return v[0] if v else None
        elif fmt == 'asf':
            if not audio.tags:
                return None
            v = audio.tags.get('Title')
            return v[0] if v else None
        else:
            if hasattr(audio, 'tags') and audio.tags:
                for k in ('title','TITLE','Title'):
                    val = audio.tags.get(k)
                    if val:
                        return val[0] if isinstance(val,(list,tuple)) else val
            return None
    except Exception:
        return None


def set_title_artist(audio, fmt, title, artist):
    if fmt == 'easyid3':
        audio['title'] = title
        if artist is not None:
            audio['artist'] = artist
        audio.save()
    elif fmt in ('flac','ogg','generic'):
        audio['title'] = title
        if artist is not None:
            audio['artist'] = artist
        audio.save()
    elif fmt == 'mp4':
        audio.tags['\u00a9nam'] = [title]
        if artist is not None:
            audio.tags['\u00a9ART'] = [artist]
        audio.save()
    elif fmt == 'asf':
        audio.tags['Title'] = [title]
        if artist is not None:
            audio.tags['Author'] = [artist]
        audio.save()
    else:
        # generic fallback
        try:
            audio.tags['title'] = title
            if artist is not None:
                audio.tags['artist'] = artist
            audio.save()
        except Exception:
            raise


def clear_kuwo_fields(audio):
    removed = []
    if audio is None:
        return removed
    tags = getattr(audio, 'tags', None)
    if not tags:
        return removed
    for key in list(tags.keys()):
        try:
            val = tags.get(key)
            if isinstance(val,(list,tuple)):
                s = ','.join([str(x) for x in val])
            else:
                s = str(val)
            if s.strip().lower() == 'kuwo':
                try:
                    del tags[key]
                    removed.append(key)
                except Exception:
                    pass
        except Exception:
            pass
    return removed


def process_file(p: Path, dry_run=False, no_backup=False):
    audio, fmt = open_audio(p)
    if audio is None:
        print(f"跳过（无法解析）: {p.name}")
        return False
    title = get_title(audio, fmt)
    needs = False
    if not title or str(title).strip() == '':
        needs = True
    elif str(title).strip().lower() == 'kuwo':
        needs = True
    if not needs:
        return False
    # parse filename
    stem = p.stem
    if '-' in stem:
        song, artist = [s.strip() for s in stem.split('-',1)]
        if artist == '':
            artist = None
    else:
        song = stem.strip()
        artist = None
    removed = clear_kuwo_fields(audio)
    print('处理:', p.name)
    print('  原 Title:', title)
    print('  将设置 Title=%r Artist=%r' % (song, artist))
    if removed:
        print('  清除字段:', removed)
    if dry_run:
        print('  [DRY-RUN] 不保存')
        return True
    # backup
    if not no_backup:
        bak = Path(str(p) + '.bak')
        if not bak.exists():
            shutil.copy2(p, bak)
            print('  已创建备份:', bak.name)
    try:
        set_title_artist(audio, fmt, song, artist)
        print('  已保存')
        return True
    except Exception as e:
        print('  写入失败:', e)
        return False


def main():
    parser = argparse.ArgumentParser(description='修复标题/歌手标签（基于文件名 song-artist）')
    parser.add_argument('-n','--dry-run', action='store_true', help='仅预览，不写入')
    parser.add_argument('-nb','--no-backup', action='store_true', help='不创建 .bak')
    parser.add_argument('--path', default='.', help='目标文件夹（默认当前目录）')
    parser.add_argument('--exts', default=','.join([e.lstrip('.') for e in EXTS_DEFAULT]), help='以逗号分隔的扩展列表')
    args = parser.parse_args()
    folder = Path(args.path)
    exts = ['.' + e.strip().lstrip('.') for e in args.exts.split(',') if e.strip()]
    count = 0
    for ext in exts:
        for p in sorted(folder.glob(f'*{ext}')):
            try:
                if process_file(p, dry_run=args.dry_run, no_backup=args.no_backup):
                    count += 1
            except Exception as e:
                print('处理出错', p.name, e)
    print(f'完成：处理 {count} 个文件（dry_run={args.dry_run}）')

if __name__ == '__main__':
    main()
