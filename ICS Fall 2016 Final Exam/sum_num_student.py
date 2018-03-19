def sum_num(n):
    result=0
    if len(str(n))>1:
        N=int(str(n)[1:])
        result+=int(str(n)[0])+sum_num(N)
    elif len(str(n))==1:
        result=n       
    return result


if __name__ == "__main__":
    print(345, ": ", sum_num(345))
    print(89, ": ", sum_num(89))
