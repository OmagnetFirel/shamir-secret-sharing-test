const { split, join } = require('shamir');
const crypto = require('crypto');
const process = require("process");

// Função auxiliar para argumentos
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

const result = {
    lang: "js",
    lib: "shamir",
    ok_split: false,
    ok_combine: false,
    ok_fail_k_minus_1: false,
    shares_count: 0,
    time_ms: 0
};

try {
    // A lib pede Uint8Array. Buffer herda de Uint8Array, então funciona.
    const secretBuffer = Buffer.from(secretHex, 'hex');

    const start = process.hrtime.bigint();

    // API: split(randomBytes, n, k, secret)
    const sharesObj = split(crypto.randomBytes, n, k, secretBuffer);
    
    // A lib retorna um objeto { "1": Uint8Array, "2": Uint8Array... }
    const shareKeys = Object.keys(sharesObj);
    
    result.shares_count = shareKeys.length;
    result.ok_split = (shareKeys.length === n);

    // 2. COMBINE (JOIN)
    // Precisamos passar um objeto com apenas K chaves
    const subsetK = {};
    shareKeys.slice(0, k).forEach(key => {
        subsetK[key] = sharesObj[key];
    });

    // API: join(parts)
    const recovered = join(subsetK);
    const recoveredBuffer = Buffer.from(recovered); // Garante que seja Buffer para comparação

    if (recoveredBuffer.equals(secretBuffer)) {
        result.ok_combine = true;
    }

    // 3. FAIL TEST (k-1)
    const subsetFail = {};
    shareKeys.slice(0, k - 1).forEach(key => {
        subsetFail[key] = sharesObj[key];
    });

    try {
        const recoveredFail = join(subsetFail);
        const recoveredFailBuffer = Buffer.from(recoveredFail);
        
        // Se retornar algo, tem que ser diferente
        if (!recoveredFailBuffer.equals(secretBuffer)) {
            result.ok_fail_k_minus_1 = true;
        } else {
            result.ok_fail_k_minus_1 = false; // Falha grave de segurança
        }
    } catch (e) {
        // Se lançar erro, é comportamento aceitável
        result.ok_fail_k_minus_1 = true;
    }

 
    const end = process.hrtime.bigint();
    const totalMs = Number(end - start) / 1e6;
    result.time_ms = parseFloat(totalMs.toFixed(3));

} catch (e) {
    result.error = e.message;
}

console.log(JSON.stringify(result));
