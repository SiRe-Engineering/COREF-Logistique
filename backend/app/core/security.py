import hashlib
import hmac
import os
import secrets


ITERATIONS = 310_000


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    sel = os.urandom(16)
    derive = hashlib.pbkdf2_hmac(
        "sha256",
        mot_de_passe.encode("utf-8"),
        sel,
        ITERATIONS,
    )
    return f"pbkdf2_sha256${ITERATIONS}${sel.hex()}${derive.hex()}"


def verifier_mot_de_passe(
    mot_de_passe: str,
    valeur_stockee: str,
) -> bool:
    try:
        algorithme, iterations, sel_hex, derive_hex = valeur_stockee.split("$")
        if algorithme != "pbkdf2_sha256":
            return False

        derive = hashlib.pbkdf2_hmac(
            "sha256",
            mot_de_passe.encode("utf-8"),
            bytes.fromhex(sel_hex),
            int(iterations),
        )
        return hmac.compare_digest(derive.hex(), derive_hex)
    except (ValueError, TypeError):
        return False


def generer_jeton() -> str:
    return secrets.token_urlsafe(48)


def hacher_jeton(jeton: str) -> str:
    return hashlib.sha256(jeton.encode("utf-8")).hexdigest()
