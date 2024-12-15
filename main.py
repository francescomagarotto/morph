from morph import pack, unpack

if __name__ == '__main__':
    b = pack("1234.99", 'pd+', 2, 10)
    s = unpack(b, 'pd+', 2, False, False)
    print(s)
    print(b)

