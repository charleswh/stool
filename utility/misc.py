import subprocess
from functools import reduce


def run_cmd(cmd, show_result=True):
    print(cmd)
    sp = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = sp.communicate(input=None)
    if error == '':
        if show_result:
            print(output)
    else:
        print(error)


def rm_dupl(var:list):
    func = lambda x, y: x if y in x else x + [y]
    return list(reduce(func, [[], ] + var))


if __name__ == '__main__':
    pass
