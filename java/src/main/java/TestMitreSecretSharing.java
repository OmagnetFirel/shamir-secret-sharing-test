import org.mitre.secretsharing.Secrets;
import org.mitre.secretsharing.Part;
import com.google.gson.Gson;
import java.util.HashMap;
import java.util.Map;
import java.util.Arrays;
import java.security.SecureRandom;

public class TestMitreSecretSharing {
    public static void main(String[] args) {
        SecureRandom random = new SecureRandom();

        String secretHex = null;
        int n = 0;
        int k = 0;

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--secret") && i + 1 < args.length) {
                secretHex = args[i + 1];
            } else if (args[i].equals("--n") && i + 1 < args.length) {
                n = Integer.parseInt(args[i + 1]);
            } else if (args[i].equals("--k") && i + 1 < args.length) {
                k = Integer.parseInt(args[i + 1]);
            }
        }

        Map<String, Object> result = new HashMap<>();
        result.put("lang", "java");
        result.put("lib", "org.mitre.secretsharing");
        result.put("ok_split", false);
        result.put("ok_combine", false);
        result.put("ok_fail_k_minus_1", false);
        result.put("shares_count", n);
        result.put("time_ms", 0.0);

        try {
            byte[] secret = hexToBytes(secretHex);
            long startTime = System.nanoTime();

            // Split: Secrets.split(secret, n, k)
            Part[] parts = Secrets.split(secret, n, k, random );

            if (parts != null && parts.length == n) {
                result.put("ok_split", true);
            }

            // Combine with k shares
            Part[] subset = Arrays.copyOfRange(parts, 0, k);
            byte[] recoveredSecret = Secrets.join(subset);

            if (Arrays.equals(secret, recoveredSecret)) {
                result.put("ok_combine", true);
            }

            // Test with k-1 shares (should fail or produce different result)
            try {
                Part[] subsetFail = Arrays.copyOfRange(parts, 0, k - 1);
                byte[] recoveredFail = Secrets.join(subsetFail);
                
                if (!Arrays.equals(secret, recoveredFail)) {
                    result.put("ok_fail_k_minus_1", true);
                }
            } catch (Exception e) {
                // If it throws with k-1 shares, that's correct behavior
                result.put("ok_fail_k_minus_1", true);
            }

            long endTime = System.nanoTime();
            double elapsedMs = (endTime - startTime) / 1_000_000.0;
            // Normalize to milliseconds with 3 decimal places
            result.put("time_ms", Math.round(elapsedMs * 1000.0) / 1000.0);

        } catch (Exception e) {
            result.put("error", e.getMessage());
        }

        Gson gson = new Gson();
        System.out.println(gson.toJson(result));
    }

    private static byte[] hexToBytes(String hex) {
        int len = hex.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4)
                                 + Character.digit(hex.charAt(i+1), 16));
        }
        return data;
    }
}
