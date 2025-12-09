# python/test_pyshamir.py
import argparse
import json
import time
from pyshamir import split, combine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--secret", required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()

    secret_bytes = bytes.fromhex(args.secret)
    n = args.n
    k = args.k

    result = {
        "lang": "python",
        "lib": "pyshamir"
    }

    start = time.perf_counter()
    shares = []

    try:
        shares = split(secret_bytes, n, k)  
        result["ok_split"] = isinstance(shares, list) and len(shares) == n
        result["shares_count"] = len(shares)
    except Exception as e:
        result["ok_split"] = False
        result["shares_count"] = 0
        result["error_split"] = str(e)
        shares = []

    try:
        if shares and len(shares) >= k:
            rec = combine(shares[:k])
            result["ok_combine"] = (rec == secret_bytes)
        else:
            result["ok_combine"] = False
    except Exception as e:
        result["ok_combine"] = False
        result["error_combine"] = str(e)

    try:
        if shares and len(shares) >= k:
            try:
                rec2 = combine(shares[:k-1])
                result["ok_fail_k_minus_1"] = (rec2 != secret_bytes)
            except Exception:
                result["ok_fail_k_minus_1"] = True
        else:
            result["ok_fail_k_minus_1"] = False
    except Exception as e:
        result["ok_fail_k_minus_1"] = False
        result["error_fail_k_minus_1"] = str(e)

    total_ms = (time.perf_counter() - start) * 1000
    result["time_ms"] = round(total_ms, 3)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
