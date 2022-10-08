import hashlib
import itertools

from pydatafront.decorator import textea_export

numberOfHashBitsToUse = 6
numberOfDifferentCharactersAsPowerOfTwo = 4
numberOfDifferentCharacters = 16
unicodeStartInDecimal = 65


@textea_export(
    path="doNameObfuscate",
    description="Genshin Impact Name Obfuscate",
    name={
        "treat_as": "config"
    },
    sha1seed={
        "treat_as": "config"
    }
)
def doNameObfuscate(name: str, sha1seed: str) -> str:
    sha1 = hashlib.sha1()
    sha1.update((sha1seed + name).encode("utf-32-le"))
    hashBytes = sha1.digest()
    sb = ""
    laterRound = False
    offset = 0
    for i in range(numberOfHashBitsToUse):
        hashDigit = hashBytes[i]
        if laterRound:
            sb += chr(unicodeStartInDecimal + offset)
        else:
            laterRound = True
        offset = hashDigit % numberOfDifferentCharacters
        sb += chr(unicodeStartInDecimal + offset)
        offset = (hashDigit >> numberOfDifferentCharactersAsPowerOfTwo) % numberOfDifferentCharacters
    return sb

