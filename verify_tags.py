import os, glob
import mutagen

cwd = r'C:\Users\i\Music\test'
os.chdir(cwd)

bak_files = sorted(glob.glob('*.bak'))
files = [os.path.splitext(b)[0] for b in bak_files]
lines = []
for f in files:
    path = os.path.join(cwd, f)
    if not os.path.exists(path):
        lines.append(f"{f}\tMISSING")
        continue
    audio = mutagen.File(path, easy=True)
    if audio is None:
        lines.append(f"{f}\tUNKNOWN_FORMAT")
        continue
    title = None
    artist = None
    if 'title' in audio:
        title = audio.get('title', [None])[0]
    if 'artist' in audio:
        artist = audio.get('artist', [None])[0]
    lines.append(f"{f}\tTitle={title}\tArtist={artist}")

with open('verify_tags.txt', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))

print('wrote verify_tags.txt')
