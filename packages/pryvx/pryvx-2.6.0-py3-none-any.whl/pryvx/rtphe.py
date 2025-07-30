import random
from sympy import mod_inverse, isprime, nextprime
import math
import hashlib
import secrets

def prove_dec(pub, c, m, r):
    """
    Non‑interactive PPK:
        a = g^u · w^n
        e = H(c || a)      (Fiat–Shamir)
        z = u + e·m  (mod n)
        w' = w · r^e (mod n)
        π = (a, z, w')
    """
    n, g = pub ; n2 = n*n
    u  = secrets.randbelow(n)
    w  = secrets.randbelow(n)
    a  = (pow(g, u, n2) * pow(w, n, n2)) % n2

    e  = int.from_bytes(
            hashlib.sha256(str(c).encode() + str(a).encode()).digest(),
            'big') % n

    z  = (u + e * m) % n
    w_ = (w * pow(r, e, n)) % n
    return a, z, w_

def verify_dec(pub, c, m, proof):
    n, g = pub ; n2 = n*n
    a, z, w_ = proof
    e = int.from_bytes(
            hashlib.sha256(str(c).encode() + str(a).encode()).digest(),
            'big') % n
    left  = (pow(g, z, n2) * pow(w_, n, n2)) % n2
    right = (pow(c, e, n2) * a) % n2
    return left == right

def generate_prime(bits=512):
    while True:
        p = nextprime(random.getrandbits(bits))
        if isprime(p):
            return p

def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)

class RTPHE:

    @staticmethod
    def keygen(bits=64):
        p = generate_prime(bits)
        q = generate_prime(bits)
        n = p * q
        lambda_n = lcm(p - 1, q - 1)
        g = n + 1
        mu = mod_inverse((pow(g, lambda_n, n * n) - 1) // n, n)
        public_key = (n, g)
        private_key = (lambda_n, mu)
        return public_key, private_key

    @staticmethod
    def encrypt(public_key, plaintext, r=None):
        n, g = public_key
        if r is None:
            r = random.randint(1, n - 1)
            while math.gcd(r, n) != 1:
                r = random.randint(1, n - 1)
        n2 = n * n
        c = (pow(g, plaintext, n2) * pow(r, n, n2)) % n2
        return c

    @staticmethod
    def encrypt_with_randomness(public_key, plaintext):
        r = random.randint(1, public_key[0] - 1)
        while math.gcd(r, public_key[0]) != 1:
            r = random.randint(1, public_key[0] - 1)
        c = RTPHE.encrypt(public_key, plaintext, r)
        return c, r

    @staticmethod
    def decrypt(public_key, private_key, ciphertext):
        n, g = public_key
        lambda_n, mu = private_key
        n2 = n * n
        x = pow(ciphertext, lambda_n, n2)
        Lx = (x - 1) // n
        plaintext = (Lx * mu) % n

        if plaintext > n // 2:
            plaintext -= n
        return plaintext

    @staticmethod
    def homomorphic_add(c1, c2, public_key):
        n2 = public_key[0] ** 2
        return (c1 * c2) % n2

    @staticmethod
    def homomorphic_add_plaintext(ciphertext, plaintext, public_key):
        n, g = public_key
        n2 = n * n
        c_plain = pow(g, plaintext, n2)
        return (ciphertext * c_plain) % n2

    @staticmethod
    def homomorphic_sub(c1, c2, public_key):
        n2 = public_key[0] ** 2
        c2_inv = mod_inverse(c2, n2)
        return (c1 * c2_inv) % n2

    @staticmethod
    def homomorphic_sub_plaintext(ciphertext, plaintext, public_key):
        n, g = public_key
        n2 = n * n
        c_plain_neg = pow(g, -plaintext % n, n2)
        return (ciphertext * c_plain_neg) % n2

    @staticmethod
    def homomorphic_scalar_mult(ciphertext, scalar, public_key):
        n2 = public_key[0] ** 2
        return pow(ciphertext, scalar, n2)

    @staticmethod
    def homomorphic_div(ciphertext, divisor, public_key):
        n = public_key[0]
        divisor_inv = mod_inverse(divisor, n)
        return RTPHE.homomorphic_scalar_mult(ciphertext, divisor_inv, public_key)

    # ========== 🔐 RANDOMNESS TRACKING HELPERS ==========

    @staticmethod
    def track_randomness_add(r1, r2, n):
        return (r1 * r2) % n

    @staticmethod
    def track_randomness_sub(r1, r2, n):
        return (r1 * mod_inverse(r2, n)) % n

    @staticmethod
    def track_randomness_scalar_mult(r, scalar, n):
        return pow(r, scalar, n)

    @staticmethod
    def track_randomness_scalar_div(r, divisor, n):
        divisor_inv = mod_inverse(divisor, n)
        return pow(r, divisor_inv, n)
