import subprocess
import json
import csv
from pathlib import Path

def run_cmd(cmd: str) -> dict:
    """Roda um comando e retorna o JSON do stdout."""
    completed = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    stdout = completed.stdout.strip()
    
    if completed.returncode != 0:
        # Em caso de erro, registra algo padrão
        return {
            "error": True,
            "cmd": cmd,
            "stderr": completed.stderr.strip(),
            "stdout": stdout  # Para debug
        }
    
    # Se stdout está vazio, retorna erro
    if not stdout:
        return {
            "error": True,
            "cmd": cmd,
            "stderr": "Empty stdout - test did not return JSON",
            "stdout": ""
        }
    
    # Espera uma linha JSON válida
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as e:
        return {
            "error": True,
            "cmd": cmd,
            "stderr": f"Invalid JSON: {str(e)}",
            "stdout": stdout[:200]  # Primeiros 200 chars para debug
        }


def main():
    base_dir = Path(__file__).parent
    results_dir = base_dir / "results"
    results_dir.mkdir(exist_ok=True)

    # 1) Carrega config de libs
    with open(base_dir / "libs_config.json", "r", encoding="utf-8") as f:
        configs = json.load(f)

    # 2) Define segredo e parâmetros (poderia ser randômico, aqui fixo)
    secret_hex = "00112233445566778899AABBCCDDEEFF"
    n = 5
    k = 3

    all_results = []

    # 3) Roda cada comando
    for cfg in configs:
        cmd = cfg["cmd"]
        if "{secret}" in cmd:
            cmd = cmd.format(secret=secret_hex, n=n, k=k)
        else:
            cmd = f'{cmd} --secret {secret_hex} --n {n} --k {k}'
        result = run_cmd(cmd)
        # Anexa metadados caso script não retorne
        if "error" in result:
            result.setdefault("lang", cfg.get("lang"))
            result.setdefault("lib", cfg.get("name"))
        all_results.append(result)

    # 4) Salva JSON bruto
    with open(results_dir / "raw_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # 5) Salva CSV resumido
    fieldnames = [
        "lang", "lib",
        "ok_split", "ok_combine", "ok_fail_k_minus_1",
        "shares_count", "time_ms",
        "error", "stderr"
    ]

    with open(results_dir / "benchmarks.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            row = {k: r.get(k, "") for k in fieldnames}
            writer.writerow(row)

if __name__ == "__main__":
    main()
