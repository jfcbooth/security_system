" To simulate the test, I am going to scp a large file and limit the transfer rate, listing the files in a directory before and after the transfer"

from os import listdir
from os.path import isfile, join
import time

def get_files(path):
    return [f for f in listdir(path) if isfile(join(path, f))]

if __name__ == "__main__":
    myDir = "/mnt/c/Users/user/Desktop/security_system/unevaluated/"
    while(1):
        print(get_files(myDir))
        time.sleep(5)

