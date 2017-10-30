# coding=utf-8
import numbers
import math
class CryptSdmobile(object):


    _keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

    def encodes(self,inputs):

        outputs = ""
        i = 0
        while i < len(inputs):
            chr1 = ord(inputs[i])
            i += 1
            try:
                chr2 = ord(inputs[i])
            except:
                chr2 = None
            i += 1
            try:
                chr3 = ord(inputs[i])
            except:
                chr3 = None
            i += 1
            enc1 = chr1 >> 2
            if chr2 is not None and chr3 is None:
                enc2 = ((chr1 & 3) << 4) | (chr2 >> 4)
                enc3 = ((chr2 & 15) << 2)
                enc4 = 64
            elif chr2 is None and chr3 is None:
                enc2 = ((chr1 & 3) << 4)
                enc3 = enc4 = 64
            else:
                enc2 = ((chr1 & 3) << 4) | (chr2 >> 4)
                enc3 = ((chr2 & 15) << 2) | (chr3 >> 6)
                enc4 = chr3 & 63
            outputs = outputs +self._keyStr[enc1] + self._keyStr[enc2] +self._keyStr[enc3] + self._keyStr[enc4]
        return outputs




class BarrettMu(object):
    # global biRadixBase
    biRadixBase = 2
    # global biRadixBits
    biRadixBits = 16
    # global bitsPerDigit
    bitsPerDigit = biRadixBits
    # global biRadix
    biRadix = 1 << 16
    # global biHalfRadix
    biHalfRadix = biRadix >> 1
    # global biRadixSquared
    biRadixSquared = biRadix * biRadix
    # global maxDigitVal
    maxDigitVal = biRadix - 1
    # global maxInteger
    maxInteger = 9999999999999998
    # global maxDigits
    # global ZERO_ARRAY
    # global bigZero
    # global bigOne

    # global highBitMasks
    highBitMasks = [0, 32768, 49152, 57344, 61440, 63488, 64512, 65024, 65280, 65408, 65472, 65504, 65520, 65528, 65532,
                    65534, 65535]

    # global lowBitMasks
    lowBitMasks = [0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535]

    # global hexatrigesimalToChar
    hexatrigesimalToChar = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h",
                            "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

    # global hexToChar
    hexToChar = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]

    def __init__(self,a,ZERO_ARRAY,bigOne):
        self.bigOne = bigOne
        self.ZERO_ARRAY = ZERO_ARRAY
        self.h = len(self.ZERO_ARRAY)
        ZERO_ARRAYS = [0 for aaa in xrange(self.h)]
        self.modulus = self.biCopy(a)
        self.k = self.biHighIndex(self.modulus) + 1
        b = BigInt(None,self.ZERO_ARRAY)
        b.digits[2*self.k] = 1
        self.mu = self.biDivide(b, self.modulus)
        self.bkplus1 = BigInt(None,ZERO_ARRAYS)
        self.bkplus1.digits[self.k + 1] = 1
        self.modulo = self.BarrettMu_modulo
        self.multiplyMod = self.BarrettMu_multiplyMod
        self.powMod = self.BarrettMu_powMod


    def biMultiplyDigit(self,a,g):
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        result = BigInt(None,ZERO_ARRAY)
        f = self.biHighIndex(a)
        e = 0
        for b in xrange(f+1):
            d = result.digits[b] + a.digits[b] * g + e
            result.digits[b] = d & self.maxDigitVal
            e = d >> self.biRadixBits
        result.digits[1 + f] = e
        return result

    def biModuloByRadixPower(self,b,c):
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        a = BigInt(None,ZERO_ARRAY)
        self.arrayCopy(b.digits, 0, a.digits, 0, c)
        return a

    def biMultiply(self,h,g):
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        o = BigInt(None,ZERO_ARRAY)
        b = self.biHighIndex(h)
        m = self.biHighIndex(g)
        for e in xrange(m+1):
            f = 0
            d = e
            for j in xrange(b+1):
                a = o.digits[d] + h.digits[j] * g.digits[e] + f
                o.digits[d] = a & self.maxDigitVal
                f = a >> self.biRadixBits
                d+=1
            o.digits[e + b + 1] = f
        o.isNeg = (h.isNeg != g.isNeg)
        return o

    def biDivideByRadixPower(self,b,c):
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        a = BigInt(None,ZERO_ARRAY)
        self.arrayCopy(b.digits, c, a.digits, 0, len(a.digits) - c)
        return a

    def BarrettMu_modulo(self,h):
        g = self.biDivideByRadixPower(h, self.k - 1)
        e = self.biMultiply(g, self.mu)
        d = self.biDivideByRadixPower(e, self.k + 1)
        c = self.biModuloByRadixPower(h, self.k + 1)
        k = self.biMultiply(d, self.modulus)
        b = self.biModuloByRadixPower(k, self.k + 1)
        a = self.biSubtract(c, b)
        if a.isNeg:
            a = self.biAdd(a, self.bkplus1)
        f = self.biCompare(a, self.modulus) >= 0
        while f:
            a = self.biSubtract(a, self.modulus)
            f = self.biCompare(a, self.modulus) >= 0
        return a


    def BarrettMu_multiplyMod(self,a,c):
        b = self.biMultiply(a, c)
        return self.modulo(b)


    def BarrettMu_powMod(self,c,f):

        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        b = BigInt(None,ZERO_ARRAY)
        b.digits[0] = 1
        d = c
        e = f
        while True:
            if (e.digits[0] & 1) != 0:
                b = self.multiplyMod(b, d)
            e = self.biShiftRight(e, 1)
            if e.digits[0] == 0 and self.biHighIndex(e) == 0:
                break
            d = self.multiplyMod(d, d)
        return b

    def biShiftRight(self,b,h):
        c = int(math.floor(h / self.bitsPerDigit))
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        a = BigInt(None,ZERO_ARRAY)
        self.arrayCopy(b.digits, c, a.digits, 0, len(b.digits) - c)
        f = h % self.bitsPerDigit
        g = self.bitsPerDigit - f
        d = 0
        e = d+1
        while d < len(a.digits)-1:
            a.digits[d] = (a.digits[d] >> f) | ((a.digits[e] & self.lowBitMasks[f]) << g)
            d+=1
            e+=1
        a.digits[len(a.digits) - 1] = a.digits[len(a.digits) - 1]>> f
        a.isNeg = b.isNeg
        return a

    # def biMultiplyDigit(self,a,g):
    #     self.ZERO_ARRAY = [0 for a in xrange(self.h)]
    #     result = BigInt(None,self.ZERO_ARRAY)
    #     f = self.biHighIndex(a)
    #     e = 0
    #     for x in xrange(f):
    #         d = result.digits[x] + a.digits[x] * g + e
    #         result.digits[x] = d & self.maxDigitVal
    #         e = d >> self.biRadixBits
    #     result.digits[1 + f] = e
    #     return result

    def biCompare(self,a,c):
        if a.isNeg != c.isNeg:
            return 1 - 2 * int(a.isNeg)
        b = len(a.digits)-1
        while b>=0:
            if a.digits[b] != c.digits[b]:
                if a.isNeg:
                    return 1 - 2 * int(a.digits[b] > c.digits[b])
                else:
                    return 1 - 2 * int(a.digits[b] < c.digits[b])
            b-=1
        return 0

    def biMultiplyByRadixPower(self,b,c):
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        a = BigInt(None,ZERO_ARRAY)
        self.arrayCopy(b.digits, 0, a.digits, c, len(a.digits) - c)
        return a

    def arrayCopy(self,e,h,c,g,f):
        a = min(h + f, len(e))
        d = h
        b = g
        while d <a:
            c[b] = e[d]
            d+=1
            b+=1

    def biShiftLeft(self,b,h):
        d = math.floor(h / self.bitsPerDigit)
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        a = BigInt(None,ZERO_ARRAY)
        self.arrayCopy(b.digits, 0, a.digits, int(d), int(len(a.digits)- d))
        g = h % self.bitsPerDigit
        c = self.bitsPerDigit - g
        e = len(a.digits) - 1
        f = e - 1
        while e> 0:
            a.digits[e] = ((a.digits[e] << g) & self.maxDigitVal) | ((a.digits[f] & self.highBitMasks[g]) >> (c))
            e-=1
            f-=1
        a.digits[0] = (a.digits[e] << g) & self.maxDigitVal
        a.isNeg = b.isNeg
        return a

    def biCopy(self,b):
        a = BigInt(True,self.ZERO_ARRAY)
        a.digits = b.digits
        a.isNeg = b.isNeg
        return a

    def biHighIndex(self,b):
        a = len(b.digits) - 1
        while a > 0 and b.digits[a] == 0:
            a -=1
        return a

    def biNumBits(self,c):
        f = self.biHighIndex(c)
        e = c.digits[f]
        b = (f + 1) * self.bitsPerDigit
        a = b
        while a > b - self.bitsPerDigit:
            if (e & 32768) != 0:
                break
            e = e << 1
            a -= 1
        return a

    def biAdd(self,b,g):
        if b.isNeg != g.isNeg:
            g.isNeg =  not g.isNeg
            a = self.biSubtract(b, g)
            g.isNeg = not g.isNeg
        else:
            ZERO_ARRAY = [0 for aaa in xrange(self.h)]
            a = BigInt(None,ZERO_ARRAY)
            f = 0
            for x in xrange(len(b)):
                e = b.digits[x] + g.digits[x] + f
                a.digits[x] = e & 65535
                f = int(e >= self.biRadix)
            a.isNeg = b.isNeg
        return a

    def biSubtract(self,b,g):
        if b.isNeg != g.isNeg:
            g.isNeg = not g.isNeg
            a = self.biAdd(b, g)
            g.isNeg = not g.isNeg
        else:
            ZERO_ARRAY = [0 for aaa in xrange(self.h)]
            a = BigInt(None,ZERO_ARRAY)
            e = 0
            for x in xrange(len(b.digits)):
                f = b.digits[x] - g.digits[x] + e
                a.digits[x] = f & 65535
                if a.digits[x] < 0:
                    a.digits[x] += self.biRadix
                e = 0 - int(f < 0)
            if e == -1:
                e = 0
                for x in xrange(len(b.digits)):
                    f = 0 - a.digits[x] + e
                    a.digits[x] = f & 65535
                    if a.digits[x] < 0 :
                        a.digits[x] += self.biRadix
                    e = 0 - int(f < 0)
                a.isNeg = not b.isNeg
            else:
                a.isNeg = b.isNeg
        return a

    def biDivideModulo(self,g,f):
        a = self.biNumBits(g)
        e = self.biNumBits(f)
        d = f.isNeg
        if a < e:
            if g.isNeg:
                o = self.biCopy(self.bigOne)
                o.isNeg = not f.isNeg
                g.isNeg = False
                f.isNeg = False
                m = self.biSubtract(f, g)
                g.isNeg = True
                f.isNeg = d
            else:
                ZERO_ARRAY = [0 for aaa in xrange(self.h)]
                o = BigInt(None,ZERO_ARRAY)
                m = self.biCopy(g)

            return [o, m]
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        o = BigInt(None,ZERO_ARRAY)
        m = g
        k = int(math.ceil(e / float(self.bitsPerDigit)) - 1)
        h = 0
        while f.digits[k] < self.biHalfRadix:
            f = self.biShiftLeft(f, 1)
            h+=1
            e+=1
            k = int(math.ceil(e / float(self.bitsPerDigit)) - 1)
            if k >= len(f.digits):
                break
        m = self.biShiftLeft(m, h)
        a += h
        u = int(math.ceil(a / float(self.bitsPerDigit))) - 1
        B = self.biMultiplyByRadixPower(f, u - k)
        while self.biCompare(m, B) != -1:
            o.digits[u - k]+=1
            m = self.biSubtract(m, B)
        z = u
        while z > k:
            l = 0 if (z >= len(m.digits)) else m.digits[z]
            A = 0 if (z - 1 >= len(m.digits)) else m.digits[z - 1]
            w =0 if (z - 2 >= len(m.digits)) else m.digits[z - 2]
            v =0 if (k >= len(f.digits)) else f.digits[k]
            c =0 if (k - 1 >= len(f.digits)) else f.digits[k - 1]
            if l ==v:
                o.digits[z - k - 1] = self.maxDigitVal
            else:
                o.digits[z - k - 1] = int(math.floor((l * self.biRadix + A) / v))
            s = o.digits[z - k - 1] * ((v * self.biRadix) + c)
            p = (l * self.biRadixSquared) + ((A * self.biRadix) + w)
            while s>p:
                o.digits[z - k - 1]-=1
                s = o.digits[z - k - 1] * ((v * self.biRadix) | c)
                p = (l * self.biRadix * self.biRadix) + ((A * self.biRadix) + w)
            B = self.biMultiplyByRadixPower(f, z - k - 1)
            m = self.biSubtract(m, self.biMultiplyDigit(B, o.digits[z - k - 1]))
            if m.isNeg:
                m = self.biAdd(m, B)
                o.digits[z - k - 1]-=1
            z-=1
        m = self.biShiftRight(m, h)
        o.isNeg = (g.isNeg != d)
        if g.isNeg:
            if d:
                o = self.biAdd(o, self.bigOne)
            else:
                o = self.biSubtract(o, self.bigOne)
            f = self.biShiftRight(f, h)
            m = self.biSubtract(f, m)
        if m.digits[0] == 0 and self.biHighIndex(m) == 0:
            m.isNeg = False
        return [o, m]


    def biDivide(self,a,b):

        return self.biDivideModulo(a, b)[0]


class BigInt(object):

    def __init__(self, a, ZERO_ARRAY):
        if type(a) is bool and a is True:
            self.digits = None
        else:
            self.digits = ZERO_ARRAY
        self.isNeg = False

    # digits = []
    #
    # def BigInt(self, a, ZERO_ARRAY):
    #     if type(a) is bool and a is True:
    #         self.digits = None
    #     else:
    #         self.digits = ZERO_ARRAY[0]
    #     self.isNeg = False
    #     return self

#
# class RSAKeyPair(object):
#
#
#
#
#

class RSAKeyPair(object):

    def __init__(self, b, c, a, h):
        self.setMaxDigits(20)
        self.setMaxDigits(h)
        self.h = h
        self.e = self.biFromHex(b)
        self.d = self.biFromHex(c)
        self.m = self.biFromHex(a)
        self.chunkSize = 2 * self.biHighIndex(self.m)
        self.radix = 16
        self.ZERO_ARRAY = [0 for aaa in xrange(h)]
        self.barrett = BarrettMu(self.m, self.ZERO_ARRAY, self.bigOne)


    #global biRadixBase
    biRadixBase = 2
    #global biRadixBits
    biRadixBits = 16
    #global bitsPerDigit
    bitsPerDigit = biRadixBits
    #global biRadix
    biRadix = 1 << 16
    #global biHalfRadix
    biHalfRadix = biRadix >> 1
    #global biRadixSquared
    biRadixSquared = biRadix * biRadix
    #global maxDigitVal
    maxDigitVal = biRadix - 1
    #global maxInteger
    maxInteger = 9999999999999998
    #global maxDigits
    #global ZERO_ARRAY
    #global bigZero
    #global bigOne

    #global highBitMasks
    highBitMasks = [0, 32768, 49152, 57344, 61440, 63488, 64512, 65024, 65280, 65408, 65472, 65504, 65520, 65528, 65532,
                    65534, 65535]

    #global lowBitMasks
    lowBitMasks = [0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767, 65535]

    #global hexatrigesimalToChar
    hexatrigesimalToChar = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h",
                            "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

    #global hexToChar
    hexToChar = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]



    def biHighIndex(self,b):
        a = len(b.digits) - 1
        while a > 0 and b.digits[a] == 0:
            a = a-1
        return a

    def charToHex(self,k):
        d = 48
        b = d + 9
        e = 97
        h = e + 25
        g = 65
        f = 65 + 25
        a = None
        if k>=d and k<=b:
            a = k-d
        else:
            if k>=g and k<=f:
                a = 10+k -g
            else:
                if k>=e and k<=h:
                    a = 10+k -e
                else:
                    a = 0
        return a

    def hexToDigit(self,d):
        b = 0
        a = min(len(d), 4)
        for x in xrange(a):
            b = b << 4
            b = b | self.charToHex(ord(d[x]))
        return b

    def biFromHex(self,e):
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        b = BigInt(None,ZERO_ARRAY)
        a = len(e)
        d = a
        c = 0
        while d>0:
            if max(d - 4, 0)<min(d, 4):
                if c == 0:
                    ee = e[max(d - 4, 0):(min(d, 4) + 1)]
                else:
                    ee = e[max(d - 4, 0):(min(d, 4))]
            else:
                ee = e[max(d - 4, 0):(max(d - 4, 0)+4)]

            b.digits[c] = self.hexToDigit(ee)
            d-=4
            c+=1

        return b

    def digitToHex(self,c):
        b = 15
        a = ""
        for i in xrange(4):
            a += self.hexToChar[c & b]
            c  = c>>4
        return self.reverseStr(a)

    def reverseStr(self,c):
        a = ""
        b = len(c)-1
        while b>-1:
            a += c[b]
            b-=1
        return a

    def biCompare(self,a,c):
        if a.isNeg != c.isNeg:
            return 1 - 2 * int(a.isNeg)
        b = len(a.digits)-1
        while b>=0:
            if a.digits[b] != c.digits[b]:
                if a.isNeg:
                    return 1 - 2 * int(a.digits[b] > c.digits[b])
                else:
                    return 1 - 2 * int(a.digits[b] < c.digits[b])
        return 0

    def biToString(self,d,f):
        ZERO_ARRAY = [0 for aaa in xrange(self.h)]
        c = BigInt(None,ZERO_ARRAY)
        c.digits[0]=f
        e = BarrettMu(self.m,ZERO_ARRAY,self.bigOne).biDivideModulo(d, c)
        a = self.hexatrigesimalToChar[e[1].digits[0]]
        while self.biCompare(e[0], self.bigZero) == 1:
            e = BarrettMu(self.m,ZERO_ARRAY,self.bigOne).biDivideModulo(e[0], c)
            digit = e[1].digits[0]
            a += self.hexatrigesimalToChar[e[1].digits[0]]
        return ("-" if d.isNeg else "") + self.reverseStr(a)

    def biToHex(self,b):
        a = ""
        d = self.biHighIndex(b)
        c= self.biHighIndex(b)
        while c>-1:
            a += self.digitToHex(b.digits[c])
            c-=1
        return a

    def encryptedString(self,l,o):
        h = []
        b = len(o)
        f = 0
        while f < b:
            h.insert(f,ord(o[f]))
            f+=1
        while len(h) % l.chunkSize != 0:
            try:
                h[f] = 0
            except:
                h.insert(f,0)
            f+=1
        g = len(h)
        p = ""
        f = 0
        while f <g:
            ZERO_ARRAY = [0 for aaa in xrange(self.h)]
            c = BigInt(None,ZERO_ARRAY)
            e = 0
            d = f
            while d < f + l.chunkSize:
                c.digits[e] = h[d]
                d+=1
                c.digits[e] = c.digits[e] + (h[d] << 8)
                d+=1
                e+=1
            n = l.barrett.powMod(c, l.e)
            m = self.biToHex(n) if l.radix == 16 else self.biToString(n, l.radix)
            p += m + " "
            f += l.chunkSize
        return p[0:len(p) - 1]

    def setMaxDigits(self,b):
        ZERO_ARRAY = [0 for aaa in xrange(b)]
        self.bigZero = BigInt(None,ZERO_ARRAY)
        self.bigOne = BigInt(None,ZERO_ARRAY)
        self.bigOne.digits[0]=1

class encryptForm(object):

    def __init__(self,c):
        self.h = c["maxdigits"]
        f = c["e"]
        k = c["n"]
        b = RSAKeyPair(f, "", k,self.h)
        d = b.encryptedString(b, "909876")
        print d
        # return d

if __name__ == "__main__":
    # import rsa,binascii
    #
    # rsaPublickey = int("f0de108649b233163695ce36bc1ae301bfbeee952fc880d8edd7853b64d222746f6e60403e936b87dd0436f25eca51c0c7f7f91318599951dbe165bb4d873261", 16)
    # key = rsa.PublicKey(rsaPublickey, 65537)
    #
    # print key
    #
    # print binascii.b2a_hex(rsa.encrypt("123123",key))

    print encryptForm({"e":"10001","maxdigits":67,"n":"f0de108649b233163695ce36bc1ae301bfbeee952fc880d8edd7853b64d222746f6e60403e936b87dd0436f25eca51c0c7f7f91318599951dbe165bb4d873261"})
