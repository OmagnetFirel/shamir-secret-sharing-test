const process = require("process");
const { split, combine } = require("shamir-secret-sharing");

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, "");
    parsed[key] = args[i + 1];
  }
  return parsed;
}

function hexToBytes(hex) {
  hex = hex.replace(/^0x/, "").toLowerCase();
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    out[i / 2] = parseInt(hex.slice(i, i + 2), 16);
  }
  return out;
}

function main() {
  const args = parseArgs();
  const secretHex = args.secret;
  const n = parseInt(args.n, 10);
  const k = parseInt(args.k, 10);

  const secretBytes = hexToBytes(secretHex);

  const result = {
    lang: "js",
    lib: "shamir-secret-sharing"
  };

  const start = process.hrtime.bigint();

  let shares = [];

  // 1) split
  try {
    shares = split(secretBytes, n, k); // retorna Uint8Array[] 
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
      const rec = combine(shares.slice(0, k)); // Uint8Array 
      const recHex = Buffer.from(rec).toString("hex");
      result.ok_combine = recHex.toLowerCase() === secretHex.toLowerCase();
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
        const rec2 = combine(shares.slice(0, k - 1));
        const rec2Hex = Buffer.from(rec2).toString("hex");
        okFail = rec2Hex.toLowerCase() !== secretHex.toLowerCase();
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
  const totalMs = Number(end - start) / 1e6;
  result.time_ms = parseFloat(totalMs.toFixed(3));

  process.stdout.write(JSON.stringify(result) + "\n");
}

main();
