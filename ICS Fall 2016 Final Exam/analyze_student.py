def analyze(x, num=0, letters=''):
    if len(x)==0:
        return (num, letters)
    else:
        if x[0].isdigit():
            num+=int(x[0])
        else:
            letters+=x[0]
        return analyze(x[1:],num,letters)


if __name__ == "__main__":
    num = 0
    letters = ''
    x = '1a2b3c'
    print(x + ':', analyze(x, num=0, letters=''))
    x = '4Shang56hai'
    print(x + ':', analyze(x, num=0, letters=''))
