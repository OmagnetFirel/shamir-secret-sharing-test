# python/test_shamirs.py
import argparse
import json
import time

from shamirs import shares, interpolate  # API da lib atualizada

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--secret", required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--k", type=int, required=True)
    args = parser.parse_args()

    # A lib shamirs trabalha com inteiros; o orchestrator manda hex
    secret_int = int(args.secret, 16)
    n = args.n
    k = args.k

    result = {
        "lang": "python",
        "lib": "shamirs"
    }

    start = time.perf_counter()
    shares_list = []

    # 1) split
    try:
        # shares(secret: int, n: int, k: int) -> list of shares
        shares_list = shares(secret_int, n, k)
        result["ok_split"] = isinstance(shares_list, list) and len(shares_list) == n
        result["shares_count"] = len(shares_list)
    except Exception as e:
        result["ok_split"] = False
        result["shares_count"] = 0
        result["error_split"] = str(e)
        shares_list = []

    # 2) combine com k shares
    try:
        if shares_list and len(shares_list) >= k:
            # interpolate(subset_of_shares) -> int
            reconstructed_secret = interpolate(shares_list[:k])
            result["ok_combine"] = (reconstructed_secret == secret_int)
        else:
            result["ok_combine"] = False
    except Exception as e:
        result["ok_combine"] = False
        result["error_combine"] = str(e)

    # 3) falha com k-1 shares
    try:
        if shares_list and len(shares_list) >= k:
            try:
                reconstructed_with_less = interpolate(shares_list[:k-1])
                result["ok_fail_k_minus_1"] = (reconstructed_with_less != secret_int)
            except Exception:
                # se a lib lançar erro com k-1 shares, também conta como falha correta
                result["ok_fail_k_minus_1"] = True
        else:
            result["ok_fail_k_minus_1"] = False
    except Exception as e:
        result["ok_fail_k_minus_1"] = False
        result["error_fail_k_minus_1"] = str(e)

    total_ms = round((time.perf_counter() - start) * 1000, 3) # Normalize to 3 decimal places
    result["time_ms"] = total_ms

    print(json.dumps(result))

if __name__ == "__main__":
    main()