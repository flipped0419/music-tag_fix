import os
from pathlib import Path
import mutagen

cwd = Path(r'C:\Users\i\Music\test')
exts = ['.mp3','.flac','.m4a','.aac','.wav','.wma','.ogg']

def parse_expected(stem):
    if '-' in stem:
        song, artist = [s.strip() for s in stem.split('-',1)]
        if artist == '':
            artist = None
    else:
        song = stem.strip()
        artist = None
    return song, artist

lines = []
for ext in exts:
    for p in sorted(cwd.glob(f'*{ext}')):
        try:
            audio = mutagen.File(str(p), easy=True)
            title = None
            artist = None
            if audio:
                try:
                    title = audio.get('title', [None])[0]
                except Exception:
                    title = None
                try:
                    artist = audio.get('artist', [None])[0]
                except Exception:
                    artist = None
            # mp4 / aac fallback
            if (title is None or artist is None) and hasattr(audio, 'tags') and audio.tags:
                try:
                    v = audio.tags.get('\u00a9nam')
                    if v and title is None:
                        title = v[0]
                except Exception:
                    pass
                try:
                    v2 = audio.tags.get('\u00a9ART')
                    if v2 and artist is None:
                        artist = v2[0]
                except Exception:
                    pass

            expected_title, expected_artist = parse_expected(p.stem)
            ok_title = (title == expected_title)
            ok_artist = (artist == expected_artist or (expected_artist is None and (artist is None or artist == '')))
            lines.append(f"{p.name}\tTitle={title}\tArtist={artist}\tOK_Title={ok_title}\tOK_Artist={ok_artist}")
        except Exception as e:
            lines.append(f"{p.name}\tERROR:{e}")

outp = cwd / 'verify_no_backup_result.txt'
with open(outp, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))

print('wrote', outp.name)
