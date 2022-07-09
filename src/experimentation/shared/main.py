import os
import shutil

# https://stackoverflow.com/a/9559881/2923526
def rm_rf(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)
