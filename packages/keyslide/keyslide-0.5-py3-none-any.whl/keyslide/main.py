import sys

rows = ["`1234567890-=",
"qwertyuiop[]\\",
"asdfghjkl;'",
"zxcvbnm,./",
"~!@#$%^&*()_+",
"QWERTYUIOP{}|",
"ASDFGHJKL:",
"ZXCVBNM<>?"]

keysMap = {}
for row in rows:
    i = 0
    length = len(row)
    for letter in row:
        keysMap[letter] = [row, length, i]
        i+=1

def encrypt(text, key):
    output = ""
    for letter in text:
        if letter in keysMap:
            info = keysMap.get(letter)
            output += info[0][(info[2] + key) % info[1]]
        else:
            output+=letter
    return output

def decrypt(text, key):
    return encrypt(text,-key)

def cli_encrypt():
    print(encrypt(sys.argv[1], int(sys.argv[2])))

def cli_decrypt():
    print(decrypt(sys.argv[1], int(sys.argv[2])))