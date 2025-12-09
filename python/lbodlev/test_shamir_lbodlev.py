#!/usr/bin/env python3
import sys
import json
import time
import argparse
import warnings
import io
import contextlib

warnings.filterwarnings('ignore')

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
        from Shamir import Shamir
        
        start = time.time()
        
        # Split
        with contextlib.redirect_stdout(io.StringIO()):
            shamir = Shamir(secret=secret_bytes, n=args.n, k=args.k, feldman_support=False)
            shares = shamir.get_shares()  # Lista de strings Base64
            public_data = shamir.get_public()  # Pega parâmetros públicos (q, k)
        
        result["shares_count"] = len(shares)
        result["ok_split"] = (len(shares) == args.n)
        
        # Combine with k shares
        with contextlib.redirect_stdout(io.StringIO()):
            recoverer = Shamir()
            recoverer.set_public(public_data)
            recoverer.set_shares(shares[:args.k])
            recovered = recoverer.recover()
        
        result["ok_combine"] = (recovered == secret_bytes)
        
        # Try with k-1 shares
        with contextlib.redirect_stdout(io.StringIO()):
            recoverer_fail = Shamir()
            recoverer_fail.set_public(public_data)
            recoverer_fail.set_shares(shares[:args.k-1])
            
            try:
                recovered_fail = recoverer_fail.recover()
                result["ok_fail_k_minus_1"] = (recovered_fail != secret_bytes)
            except Exception:
                result["ok_fail_k_minus_1"] = True
        
        end = time.time()
        # Normalize to milliseconds with 3 decimal places
        result["time_ms"] = round((end - start) * 1000, 3)
        
    except Exception as e:
        result["error"] = str(e)
    
    print(json.dumps(result))


if __name__ == "__main__":
    main()
