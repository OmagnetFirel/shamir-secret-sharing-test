import shamir
import json
import time

def hex_to_bytes(hex_str):
    return bytes.fromhex(hex_str)

def test_shamir(secret_hex, n, k):
    result = {
        "lang": "python",
        "lib": "shamir",
        "ok_split": False,
        "ok_combine": False,
        "ok_fail_k_minus_1": False,
        "shares_count": n,
        "time_ms": 0.0
    }
    
    try:
        secret_bytes = hex_to_bytes(secret_hex)
        start_time = time.time()
        
        # Split usando byte-level API
        shares = shamir.make_byte_shares(k, n, secret_bytes)
        
        if len(shares) == n:
            result["ok_split"] = True
        
        # Combine com k shares
        recovered_secret = shamir.recover_secret_bytes(shares[:k])
        
        if recovered_secret == secret_bytes:
            result["ok_combine"] = True
        
        # Teste com k-1 shares (deve falhar ou dar diferente)
        try:
            recovered_fail = shamir.recover_secret_bytes(shares[:k-1])
            if recovered_fail != secret_bytes:
                result["ok_fail_k_minus_1"] = True
        except Exception:
            # Se lançar exceção com k-1 shares, comportamento correto
            result["ok_fail_k_minus_1"] = True
        
        end_time = time.time()
        # Normalize to milliseconds with 3 decimal places
        result["time_ms"] = round((end_time - start_time) * 1000, 3)
        
    except Exception as e:
        result["error"] = str(e)
    
    print(json.dumps(result))

if __name__ == "__main__":
    import sys
    
    secret = None
    n = 0
    k = 0
    
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--secret" and i + 1 < len(sys.argv):
            secret = sys.argv[i + 1]
        elif sys.argv[i] == "--n" and i + 1 < len(sys.argv):
            n = int(sys.argv[i + 1])
        elif sys.argv[i] == "--k" and i + 1 < len(sys.argv):
            k = int(sys.argv[i + 1])
    
    test_shamir(secret, n, k)
