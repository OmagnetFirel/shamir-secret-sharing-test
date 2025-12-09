const sss = require('shamirs-secret-sharing');
const { performance } = require('perf_hooks');
const process = require("process");

// Função auxiliar para parsear argumentos --key value
function getArgs() {
    const args = {};
    process.argv.slice(2).forEach((val, index, array) => {
        if (val.startsWith('--')) {
            const key = val.substring(2);
            const value = array[index + 1];
            args[key] = value;
        }
    });
    return args;
}

const args = getArgs();
const secretHex = args.secret;
const n = parseInt(args.n);
const k = parseInt(args.k);

// Prepara o objeto de resultado
const result = {
    lang: "js",
    lib: "shamirs-secret-sharing",
    ok_split: false,
    ok_combine: false,
    ok_fail_k_minus_1: false,
    shares_count: 0,
    time_ms: 0
};

try {
    const secretBuffer = Buffer.from(secretHex, 'hex');

    const start = process.hrtime.bigint();

    const shares = sss.split(secretBuffer, { shares: n, threshold: k });
    
    result.shares_count = shares.length;
    result.ok_split = (shares.length === n);

    const subsetK = shares.slice(0, k);
    const recovered = sss.combine(subsetK);
    const recoveredBuffer = Buffer.from(recovered);

   
    if (recoveredBuffer.equals(secretBuffer)) {
        result.ok_combine = true;
    }

    const subsetKMinus1 = shares.slice(0, k - 1);
    try {
        const recoveredFail = sss.combine(subsetKMinus1);
        const recoveredFailBuffer = Buffer.from(recoveredFail);

        if (!recoveredFailBuffer.equals(secretBuffer)) {
            result.ok_fail_k_minus_1 = true;
        } else {
            result.ok_fail_k_minus_1 = false; 
        }
    } catch (e) {
        result.ok_fail_k_minus_1 = true;
    }

    const end = process.hrtime.bigint();
    const totalMs = Number(end - start) / 1e6;
    result.time_ms = parseFloat(totalMs.toFixed(3));

} catch (e) {
    result.error = e.message;
}

console.log(JSON.stringify(result));
