import com.codahale.shamir.Scheme;
import java.security.SecureRandom;
import java.util.LinkedHashMap;
import java.util.Map;

public class TestCodahaleShamir {

    private static Map<String, String> parseArgs(String[] args) {
        Map<String, String> map = new LinkedHashMap<>();
        for (int i = 0; i < args.length; i += 2) {
            String key = args[i].replaceFirst("^--", "");
            map.put(key, args[i + 1]);
        }
        return map;
    }

    public static void main(String[] args) {
        Map<String, String> pargs = parseArgs(args);
        String secretHex = pargs.get("secret").toLowerCase();
        int n = Integer.parseInt(pargs.get("n"));
        int k = Integer.parseInt(pargs.get("k"));

        byte[] secret = hexToBytes(secretHex);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("lang", "java");
        result.put("lib", "com.codahale:shamir");

        long start = System.nanoTime();

        Scheme scheme = new Scheme(new SecureRandom(), n, k);

        Map<Integer, byte[]> parts = null;

        // 1) split
        try {
            parts = scheme.split(secret);                  // Map<Integer, byte[]>
            boolean okSplit = parts.size() == n;
            result.put("ok_split", okSplit);
            result.put("shares_count", parts.size());
        } catch (Exception e) {
            result.put("ok_split", false);
            result.put("shares_count", 0);
            result.put("error_split", e.toString());
        }

        // 2) combine com k shares
        try {
            if (parts != null && parts.size() >= k) {
                Map<Integer, byte[]> subset = new LinkedHashMap<>();
                int count = 0;
                for (Map.Entry<Integer, byte[]> e : parts.entrySet()) {
                    subset.put(e.getKey(), e.getValue());
                    count++;
                    if (count >= k) break;
                }
                byte[] rec = scheme.join(subset);         // join(Map<Integer, byte[]>)
                boolean okCombine = bytesEquals(rec, secret);
                result.put("ok_combine", okCombine);
            } else {
                result.put("ok_combine", false);
            }
        } catch (Exception e) {
            result.put("ok_combine", false);
            result.put("error_combine", e.toString());
        }

        // 3) falha com k-1 shares
        try {
            if (parts != null && parts.size() >= k) {
                Map<Integer, byte[]> subset = new LinkedHashMap<>();
                int count = 0;
                for (Map.Entry<Integer, byte[]> e : parts.entrySet()) {
                    subset.put(e.getKey(), e.getValue());
                    count++;
                    if (count >= k - 1) break;
                }
                boolean okFail;
                try {
                    byte[] rec2 = scheme.join(subset);
                    okFail = !bytesEquals(rec2, secret);
                } catch (Exception ex) {
                    okFail = true;
                }
                result.put("ok_fail_k_minus_1", okFail);
            } else {
                result.put("ok_fail_k_minus_1", false);
            }
        } catch (Exception e) {
            result.put("ok_fail_k_minus_1", false);
            result.put("error_fail_k_minus_1", e.toString());
        }

        long totalNs = System.nanoTime() - start;
        double ms = totalNs / 1_000_000.0;
        // Normalize to milliseconds with 3 decimal places
        result.put("time_ms", Math.round(ms * 1000.0) / 1000.0);
     
        System.out.println(toJson(result));
    }

    private static byte[] hexToBytes(String hex) {
        hex = hex.replaceAll("^0x", "").toLowerCase();
        int len = hex.length();
        byte[] out = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            out[i / 2] = (byte) Integer.parseInt(hex.substring(i, i + 2), 16);
        }
        return out;
    }

    private static boolean bytesEquals(byte[] a, byte[] b) {
        if (a == null || b == null || a.length != b.length) return false;
        boolean eq = true;
        for (int i = 0; i < a.length; i++) {
            eq &= (a[i] == b[i]);
        }
        return eq;
    }

    private static String toJson(Map<String, Object> map) {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        boolean first = true;
        for (Map.Entry<String, Object> e : map.entrySet()) {
            if (!first) sb.append(",");
            first = false;
            sb.append("\"").append(e.getKey()).append("\":");
            Object v = e.getValue();
            if (v instanceof String) {
                sb.append("\"").append(v.toString().replace("\"", "\\\"")).append("\"");
            } else if (v instanceof Boolean) {
                sb.append(((Boolean) v) ? "true" : "false");
            } else {
                sb.append(v.toString());
            }
        }
        sb.append("}");
        return sb.toString();
    }
}
