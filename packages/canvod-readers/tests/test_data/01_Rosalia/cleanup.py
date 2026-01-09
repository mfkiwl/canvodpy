#%%
import shutil
from pathlib import Path

root = Path().cwd()
pattern_retain = '*.25o'

#%%
files = [x for x in list(root.rglob('**/*')) if x.is_file()]
#%%
to_retain = sorted(
    [x for x in files if str(x).endswith('.25o') or str(x).endswith('.py')])

print(to_retain)

# for f in files:
#     if f not in to_retain:
#         try:
#             print(f'Removing {f}')
#             # if f.is_dir():
#             #     shutil.rmtree(f)
#             # else:
#             f.unlink()
#         except Exception as e:
#             print(f'Error removing {f}: {e}')

retain = [
    '001a',
    '001b',
    '001c',
]

for f in files:
    if not any(x in str(f) for x in retain):
        try:
            print(f'Removing {f}')
            # if f.is_dir():
            #     shutil.rmtree(f)
            # else:
            f.unlink()
        except Exception as e:
            print(f'Error removing {f}: {e}')
