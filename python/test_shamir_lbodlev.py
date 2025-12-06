#!/usr/bin/env python3
import sys
import json
import time
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret', required=True, help='Secret in hex')
    parser.add_argument('--n', type=int, required=True, help='Total shares')
    parser.add_argument('--k', type=int, required=True, help='Threshold')
    args = parser.parse_args()
    
    secret_bytes = bytes.fromhex(args.secret)
    
    result = {
        "lang": "python",
        "lib": "shamir-lbodlev",
        "ok_split": False,
        "ok_combine": False,
        "ok_fail_k_minus_1": False,
        "shares_count": 0,
        "time_ms": 0
    }
    
    try:
        from shamir import Shamir
        
        start = time.time()
        
        # Split: disable Feldman VSS for pure SSS
        shamir = Shamir(secret=secret_bytes, n=args.n, k=args.k, feldman_support=False)
        shares = shamir.get_shares()
        
        result["shares_count"] = len(shares)
        result["ok_split"] = (len(shares) == args.n)
        
        # Combine with k shares
        recoverer = Shamir()
        for i in range(args.k):
            recoverer.add_share(shares[i])
        recovered = recoverer.recover()
        
        result["ok_combine"] = (recovered == secret_bytes)
        
        # Try with k-1 shares (should fail or produce different result)
        recoverer_fail = Shamir()
        for i in range(args.k - 1):
            recoverer_fail.add_share(shares[i])
        
        try:
            recovered_fail = recoverer_fail.recover()
            # If it doesn't raise error, check if result is different
            result["ok_fail_k_minus_1"] = (recovered_fail != secret_bytes)
        except Exception:
            # If it raises error, that's correct behavior
            result["ok_fail_k_minus_1"] = True
        
        end = time.time()
        result["time_ms"] = round((end - start) * 1000, 2)
        
    except Exception as e:
        result["error"] = str(e)
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
