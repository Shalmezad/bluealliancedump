import hashlib

class StringUtil(object):
    @staticmethod
    def hash_string(string: str):
        """
        Hashes a given string
        """
        hash_object = hashlib.sha256(str.encode(string))
        hex_dig = hash_object.hexdigest()
        return hex_dig