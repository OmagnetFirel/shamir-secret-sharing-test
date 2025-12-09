const process = require("process");
const secrets = require("secrets.js-grempe"); 

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, "");
    parsed[key] = args[i + 1];
  }
  return parsed;
}

function main() {
  const args = parseArgs();
  const secretHex = args.secret.toLowerCase();
  const n = parseInt(args.n, 10);
  const k = parseInt(args.k, 10);

  const result = {
    lang: "js",
    lib: "secrets.js-grempe"
  };

  const start = process.hrtime.bigint();

  let shares = [];

  // 1) split
  try {
    // secrets.share espera segredo em hex sem prefixo 0x
    shares = secrets.share(secretHex, n, k);
    result.ok_split = Array.isArray(shares) && shares.length === n;
    result.shares_count = shares.length;
  } catch (e) {
    result.ok_split = false;
    result.shares_count = 0;
    result.error_split = String(e);
    shares = [];
  }

  // 2) combine com k shares
  try {
    if (shares.length >= k) {
      const rec = secrets.combine(shares.slice(0, k)).toLowerCase(); // hex
      result.ok_combine = (rec === secretHex);
    } else {
      result.ok_combine = false;
    }
  } catch (e) {
    result.ok_combine = false;
    result.error_combine = String(e);
  }

  // 3) falha com k-1 shares
  try {
    if (shares.length >= k) {
      let okFail;
      try {
        const rec2 = secrets.combine(shares.slice(0, k - 1)).toLowerCase();
        okFail = (rec2 !== secretHex);
      } catch (e) {
        okFail = true;
      }
      result.ok_fail_k_minus_1 = okFail;
    } else {
      result.ok_fail_k_minus_1 = false;
    }
  } catch (e) {
    result.ok_fail_k_minus_1 = false;
    result.error_fail_k_minus_1 = String(e);
  }

  const end = process.hrtime.bigint(); 
  const totalMs = Number(end - start) / 1e6; // Convert to milliseconds
  result.time_ms = parseFloat(totalMs.toFixed(3)); // Normalize to 3 decimal places

  process.stdout.write(JSON.stringify(result) + "\n");
}

main();
