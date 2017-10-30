# coding=utf-8
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from base64 import b64encode
if __name__ == "__main__":

    n = "198616"
    t = MD5.new("login.189.cn").hexdigest()
    u = AES.new(t,AES.MODE_CBC,b'1234567812345678')
    length = 16 - (len(n) % 16)
    n += chr(length) * length
    #n = n[:-n[-1]]
    print b64encode(u.encrypt(n))
    print u
    # return u + ""

