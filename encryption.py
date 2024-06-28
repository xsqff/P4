import string

ALPHABETS = {
    "en": string.ascii_uppercase + string.digits + ".,(...)",
    "ru": "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ0123456789.,(...)"
}

def get_alphabet(language):
    if language in ALPHABETS:
        return ALPHABETS[language]
    else:
        raise ValueError("Unsupported language")

def vigenere_encrypt(plain_text, key, alphabet):
    plain_text = ''.join(filter(lambda x: x in alphabet, plain_text.upper()))
    key = key.upper()
    cipher_text = []

    key_index = 0
    for char in plain_text:
        if char in alphabet:
            plain_index = alphabet.index(char)
            key_char = key[key_index % len(key)]
            key_index += 1
            key_index_val = alphabet.index(key_char)
            cipher_index = (plain_index + key_index_val) % len(alphabet)
            cipher_text.append(alphabet[cipher_index])
        else:
            cipher_text.append(char)

    return ''.join(cipher_text)

def vigenere_decrypt(cipher_text, key, alphabet):
    cipher_text = ''.join(filter(lambda x: x in alphabet, cipher_text.upper()))
    key = key.upper()
    plain_text = []

    key_index = 0
    for char in cipher_text:
        if char in alphabet:
            cipher_index = alphabet.index(char)
            key_char = key[key_index % len(key)]
            key_index += 1
            key_index_val = alphabet.index(key_char)
            plain_index = (cipher_index - key_index_val) % len(alphabet)
            plain_text.append(alphabet[plain_index])
        else:
            plain_text.append(char)

    return ''.join(plain_text)

def shift_encrypt(plain_text, shift, alphabet):
    plain_text = ''.join(filter(lambda x: x in alphabet, plain_text.upper()))
    cipher_text = []

    for char in plain_text:
        if char in alphabet:
            plain_index = alphabet.index(char)
            cipher_index = (plain_index + shift) % len(alphabet)
            cipher_text.append(alphabet[cipher_index])
        else:
            cipher_text.append(char)

    return ''.join(cipher_text)

def shift_decrypt(cipher_text, shift, alphabet):
    cipher_text = ''.join(filter(lambda x: x in alphabet, cipher_text.upper()))
    plain_text = []

    for char in cipher_text:
        if char in alphabet:
            cipher_index = alphabet.index(char)
            plain_index = (cipher_index - shift) % len(alphabet)
            plain_text.append(alphabet[plain_index])
        else:
            plain_text.append(char)

    return ''.join(plain_text)

def break_shift_cipher(cipher_text, alphabet):
    results = []
    cipher_text = ''.join(filter(lambda x: x in alphabet, cipher_text.upper()))

    for shift in range(len(alphabet)):
        decrypted_text = []
        for char in cipher_text:
            if char in alphabet:
                cipher_index = alphabet.index(char)
                plain_index = (cipher_index - shift) % len(alphabet)
                decrypted_text.append(alphabet[plain_index])
            else:
                decrypted_text.append(char)
        results.append(''.join(decrypted_text))

    return results
