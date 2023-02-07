from bitstream import BitStream
import subprocess
import sys
import pickle



class dxcode:

    def __init__(self, cryptText="encrypted/test.p"):
        self.xcode = "/home/jelle/bin/xcode"
        self.xcodeOptions = "-d encrypted/"
        self.cryptText = cryptText
        self.cryptBuffer = b""
        self.testBuffer = b""
        self.testCryptText = "encrypted/test.p"
        self.testPlainText = "test.p"
        self.plainBuffer = b"0987654321"
        self.plainText = "test.p"
        self.progress = 8
        self.length = 0
        self.key = b""

    def readCryptText(self):
        """read the cryptText file and puts it in the cryptBuffer"""
        with open(self.cryptText, "rb") as c:
            cryptBuffer = c.read(1)
            if cryptBuffer[0] == 0x13:
                self.cryptBuffer = c.read()
                self.length = len(self.cryptBuffer) #should have the first byte removed
            else:
                sys.stderr.write(f"{self.cryptText} is not an xcode encrypted file.")

    def readTest(self, fileName):
        """read the cryptText file and puts it in the cryptBuffer"""
        with open(fileName, "rb") as c:
            testBuffer = c.read(1)
            if testBuffer[0] == 0x13:
                self.testBuffer = c.read()
            else:
                sys.stderr.write(f"{fileName} is not an xcode encrypted file.")


    def readPlain(self):
        """reads the plaintext from file"""
        with open(self.plainText, "rb") as pf:
            self.plainBuffer = pf.read()

    def writePlain(self, fileName):
        # debug
        # print(f"filename: {fileName} plain content:{self.plainBuffer}")
        with open(fileName, "wb") as pf:
            pf.write(self.plainBuffer)

    def determineKey(self):
        '''compare (XOR) the crypttext with the testtext, '''
        self.key = self.byte_xor(self.plainBuffer, self.testBuffer)


    def runXcode(self, fileName):
        command = f"wsl /home/jelle/bin/xcode -d encrypted/ {fileName}"
        subprocess.call(command, shell=False)

    def byte_xor(self, ba1, ba2):
        """ XOR two byte strings """
        # return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])
        _l = []
        for _a, _b in zip(ba1, ba2):
            _l.append(_a ^ _b)

        # print(f"ba1:{ba1} ^ ba2:{ba2} = _l{_l}")
        return bytes(_l)

    def solveForKey(self, key):
        fixedKey = key
        self.plainBuffer = b'v\x05\x057:\x01y\x0b' #b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        self.length = len(key)
        alternate = f"{self.plainText}{self.progress % 2}"
        self.writePlain(alternate)
        self.runXcode(fileName=alternate)
        keyEvolution = []
        diffList = []
        for i in range(self.length):
            self.readTest(f"encrypted/{alternate}")
            self.determineKey()
            # self.key = self.byte_xor(self.testBuffer, self.cryptBuffer)
            # self.plainBuffer += b"0"
            difference = self.byte_xor(fixedKey, self.key)
            keyEvolution.append(BitStream(self.key))
            diffList.append(BitStream(difference))
            # print(f"difference:{BitStream(difference)}")
            self.plainBuffer = self.byte_xor(self.plainBuffer, difference)
            self.plainBuffer = self.plainBuffer + b"0"
            # print(f"testBuffer:{self.testBuffer} ^ difference:{self.key} = new {self.plainBuffer}")
            self.writePlain(alternate)
            self.runXcode(alternate)

        # print(f"  {BitStream(self.testBuffer)} \n^ {BitStream(self.key)} \n= {BitStream(self.plainBuffer)}")
        for bs in keyEvolution:
            print(bs)
        # print(keyEvolution)
        for ds in diffList:
            print(ds)

    def run(self):
        # read the cryptText so we know the size
        self.readCryptText()
        # alternate = f"{self.plainText}{self.progress%2}"
        alternate = f"{self.plainText}{self.progress % 2}"
        self.writePlain(alternate)
        self.runXcode(fileName=alternate)
        # print(f"alternate={alternate}")

        for i in range(self.length):
            self.readTest(f"encrypted/{alternate}")
            self.determineKey()
            # self.key = self.byte_xor(self.testBuffer, self.cryptBuffer)
            # self.plainBuffer += b"0"
            self.plainBuffer = self.byte_xor(self.cryptBuffer, self.key)
            self.plainBuffer = self.plainBuffer + b"0"
            # print(f"testBuffer:{self.testBuffer} ^ difference:{self.key} = new {self.plainBuffer}")
            self.writePlain(alternate)
            self.runXcode(alternate)

        print(f"{self.testBuffer} ^ {self.key} = {self.plainBuffer}")

    def fakeCrypt(self, testBuffer):
        # self.readCryptText()
        self.cryptBuffer = testBuffer
        self.length = len(testBuffer)
        alternate = f"{self.plainText}{self.progress % 2}"
        self.writePlain(alternate)
        self.runXcode(fileName=alternate)
        # print(f"alternate={alternate}")

        for i in range(self.length):
            self.readTest(f"encrypted/{alternate}")
            self.determineKey()
            # self.key = self.byte_xor(self.testBuffer, self.cryptBuffer)
            # self.plainBuffer += b"0"
            self.plainBuffer = self.byte_xor(self.cryptBuffer, self.key)
            self.plainBuffer = self.plainBuffer + b"0"
            # print(f"testBuffer:{self.testBuffer} ^ difference:{self.key} = new {self.plainBuffer}")
            self.writePlain(alternate)
            self.runXcode(alternate)

        print(f"{self.testBuffer} ^ {self.key} = {self.plainBuffer}")
        return self.plainBuffer

    def listFakeKeys(self):
        testArray = bytearray(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff")
        print(testArray)
        collect = []
        for i in range(8, len(testArray)):
            for s in range(8):
                plop = 128 >> s
                copyArray = testArray.copy()
                testArray[i] = plop ^ testArray[i]
                collect.append((self.fakeCrypt(bytes(testArray)),self.key,testArray))
                testArray = copyArray

        self.slaOp(collect)

    def deelTwee(self):

        collect = list(self.load_object())
        lastKey = BitStream(b"\x00" * 64)
        cryptString = "crypt:"
        plainString = f"plain:"
        keyString = f"key : "
        zoDan = [0] * 256
        i = 64
        fkey = b""
        for plain, nkey, crypt in collect:
            cbs = BitStream(bytes(crypt))
            pbs = BitStream(plain)
            key = BitStream(nkey)
            if i < 65:
                fkey = nkey
            cryptString = "crypt:"
            plainString = f"plain:"
            keyString   = f"key  :"

            for j in range(len(cbs)):
                c = cbs.read(n=1, type=bool)[0]
                k = key.read(n=1, type=bool)[0]
                p = pbs.read(n=1, type=bool)[0]
                lk = lastKey.read(n=1, type=bool)[0]
                # key.write(keyBit)

                cryptString += "1" if c else "0"
                plainString += "1" if p else "0"


                if i == j:
                    keyString = keyString + "X"
                elif i > 0 and k == lk:
                    keyString = keyString + "."
                elif k:
                    keyString = keyString + "0"
                    if j > i:
                        try:
                            zoDan[j-i] += 1
                        except IndexError:
                            print(f"j:{j} - i:{i} = {j - i}")
                            zoDan[j-i] = 1
                else:
                    keyString = keyString + "1"
                    if j > i:
                        try:

                            zoDan[j - i] += 1
                        except IndexError:
                            print(f"j:{j} - i:{i} = {j - i}")
                            zoDan[j - i] = 1

            i += 1
            lastKey = BitStream(nkey)
            # lastKey = BitStream(fkey)


            # print(cryptString)
            print(keyString)
            # print(plainString)
        print(zoDan)

    def slaOp(self, obj):
        try:
            with open("data.pickle", "wb") as f:
                pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

        except Exception as ex:
            print("Error during pickling object (Possibly unsupported):", ex)

    def load_object(self):
        try:
            with open("data.pickle", "rb") as f:
                return pickle.load(f)

        except Exception as ex:
            print("Error during unpickling object (Possibly unsupported):", ex)



if __name__ == '__main__':
    test = dxcode("encrypted/test.p")
    # test.run()
    # test.solveForKey(b'v\x05\x057:\x01y\x0b\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
    # test.fakeCrypt(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')

    # test.listFakeKeys()
    test.deelTwee()