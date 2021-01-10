import rsa


def encrypt_msg(text, Ya):
    try:
        print(f" Plain text : {text}")
        return rsa.encrypt(message=text.encode('utf-8'), pub_key=Ya)
    except Exception as error:
        print(f"Error : {error}")


def decrypt_msg(crypto, Xa):
    try:
        return rsa.decrypt(crypto=crypto, priv_key=Xa)
    except Exception as error:
        print(f"Error : {error}")


def getKeys_description(Ya, Xa):
    try:
        print('Private Key')
        print(f"n : {Xa['n']}")
        print(f"e : {Xa['e']}")
        print(f"d : {Xa['d']}")
        print(f"p : {Xa['p']}")
        print(f"q : {Xa['q']}")
        print(f"{'*' * 180}")
        print('Public Key')
        print(f"n : {Ya['n']}")
        print(f"e : {Ya['e']}")
        print(f"{'*' * 180}")
    except Exception as error:
        print(f"Error : {error}")


def generate_keys(size=512):
    return rsa.newkeys(nbits=size, poolsize=8)

if __name__ == "__main__":
    Ya, Xa = generate_keys(512)
    getKeys_description(Ya, Xa)
    message = "Have a nice day"
    print(f"{'*' * 180}")
    cipher_text = encrypt_msg(message, Ya)
    print(f"Encrypted text : {cipher_text}")
    print(f"{'*' * 180}")
    rec_msg = decrypt_msg(cipher_text, Xa)
    print(f"Decrypted text : {rec_msg.decode('utf-8')}")
    print(f"{'*' * 180}")

