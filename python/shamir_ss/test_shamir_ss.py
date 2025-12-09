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
    
    # Converte hex para string (a lib trabalha com text)
    secret_hex = args.secret
    secret_bytes = bytes.fromhex(secret_hex)
    
    result = {
        "lang": "python",
        "lib": "shamir-ss",
        "ok_split": False,
        "ok_combine": False,
        "ok_fail_k_minus_1": False,
        "shares_count": 0,
        "time_ms": 0
    }
    
    try:
        from shamir_ss import generate_text_shares, reconstruct_text_secret
        
        start = time.time()
        
        # Split: usa hex string como "text"
        shares = generate_text_shares(secret_hex, args.k, args.n)
        
        result["shares_count"] = len(shares)
        result["ok_split"] = (len(shares) == args.n)
        
        # Combine with k shares
        recovered_hex = reconstruct_text_secret(shares[:args.k])
        recovered_bytes = bytes.fromhex(recovered_hex)
        
        result["ok_combine"] = (recovered_bytes == secret_bytes)
        
        # Try with k-1 shares (should fail or produce different result)
        try:
            recovered_fail_hex = reconstruct_text_secret(shares[:args.k-1])
            recovered_fail_bytes = bytes.fromhex(recovered_fail_hex)
            result["ok_fail_k_minus_1"] = (recovered_fail_bytes != secret_bytes)
        except Exception:
            # Se lançar exceção, é comportamento correto
            result["ok_fail_k_minus_1"] = True
        
        end = time.time()
        # Normalize to milliseconds with 3 decimal places
        result["time_ms"] = round((end - start) * 1000, 3)
        
    except Exception as e:
        result["error"] = str(e)
    
    print(json.dumps(result))


if __name__ == "__main__":
    main()
