import base64
import hashlib
import hmac
import secrets
import sys

HASH_ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 260000
SALT_BYTES = 16


def hash_admin_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = _pbkdf2(password, salt, DEFAULT_ITERATIONS)
    return "$".join(
        [
            HASH_ALGORITHM,
            str(DEFAULT_ITERATIONS),
            _encode(salt),
            _encode(digest),
        ]
    )


def verify_admin_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, digest_text = password_hash.split("$", 3)
        iterations = int(iterations_text)
    except ValueError:
        return False

    if algorithm != HASH_ALGORITHM or iterations < 1:
        return False

    try:
        salt = _decode(salt_text)
        expected_digest = _decode(digest_text)
    except ValueError:
        return False

    actual_digest = _pbkdf2(password, salt, iterations)
    return hmac.compare_digest(actual_digest, expected_digest)


def _pbkdf2(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1]:
        raise SystemExit("Usage: python -m app.modules.admin_auth.passwords '<password>'")

    print(hash_admin_password(sys.argv[1]))


if __name__ == "__main__":
    main()
