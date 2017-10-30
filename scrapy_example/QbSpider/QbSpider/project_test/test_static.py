from base64 import b64decode,b64encode
# from os.path import join,dirname
import rsa
from Crypto.PublicKey import RSA
class static(object):


    def rsa_encrypt(self):

        keyDER = b64decode("f0de108649b233163695ce36bc1ae301bfbeee952fc880d8edd7853b64d222746f6e60403e936b87dd0436f25eca51c0c7f7f91318599951dbe165bb4d873261")

        keyPub = RSA.importKey(keyDER)

        nloginpwd = b64encode(rsa.encrypt(b"%s" % "123123", keyPub))

        return nloginpwd


if __name__ == "__main__":

    print static().rsa_encrypt()