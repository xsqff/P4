from utils.encryption import (
    vigenere_encrypt, vigenere_decrypt,
    shift_encrypt, shift_decrypt, get_alphabet, break_shift_cipher
)


def encrypt_text(text, method, params, operation, language):
    alphabet = get_alphabet(language)
    if method == "vigenere":
        key = params.get("key")
        return vigenere_encrypt(text, key, alphabet) if operation == "encrypt" else vigenere_decrypt(text, key,
                                                                                                     alphabet)
    elif method == "shift":
        shift = params.get("shift")
        return shift_encrypt(text, shift, alphabet) if operation == "encrypt" else shift_decrypt(text, shift, alphabet)
    else:
        raise ValueError("Unknown method")


def break_shift_cipher_wrapper(data):
    method_id = data.get("method_id")
    text = data.get("text")
    language = data.get("language", "en")

    alphabet = get_alphabet(language)
    if method_id == 2:
        possible_texts = break_shift_cipher(text, alphabet)
        return {"possible_texts": possible_texts, "status": 200}
    else:
        return {"error": "Breaking this cipher is not supported", "status": 400}
