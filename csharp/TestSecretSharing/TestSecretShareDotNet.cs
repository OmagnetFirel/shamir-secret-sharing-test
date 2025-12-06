using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Text.Json;
using SecretSharingDotNet.Cryptography;
using SecretSharingDotNet.Cryptography.ShamirsSecretSharing;
using SecretSharingDotNet.Math;

namespace SecretSharingDotNetTest
{
    class Program
    {
        static void Main(string[] args)
        {
            string secretHex = null;
            int n = 0;
            int k = 0;

            for (int i = 0; i < args.Length; i++)
            {
                if (args[i] == "--secret" && i + 1 < args.Length)
                    secretHex = args[i + 1];
                else if (args[i] == "--n" && i + 1 < args.Length)
                    n = int.Parse(args[i + 1]);
                else if (args[i] == "--k" && i + 1 < args.Length)
                    k = int.Parse(args[i + 1]);
            }

            var result = new Dictionary<string, object>
            {
                ["lang"] = "csharp",
                ["lib"] = "SecretSharingDotNet",
                ["ok_split"] = false,
                ["ok_combine"] = false,
                ["ok_fail_k_minus_1"] = false,
                ["shares_count"] = n,
                ["time_ms"] = 0.0
            };

            try
            {
                byte[] secret = HexToBytes(secretHex);
                var sw = Stopwatch.StartNew();

                // Create splitter instance
                var splitter = new SecretSplitter<BigInteger>();
                
                // Split: MakeShares(k, n, bytes)
                var shares = splitter.MakeShares(k, n, secret);
                
                if (shares.Count() == n)
                {
                    result["ok_split"] = true;
                }

                // Create reconstructor instance
                var gcd = new ExtendedEuclideanAlgorithm<BigInteger>();
                var combiner = new SecretReconstructor<BigInteger>(gcd);

                // Combine with k shares
                var subset = shares.Take(k).ToArray();
                var recoveredSecret = combiner.Reconstruction(subset).ToByteArray();

                if (recoveredSecret.SequenceEqual(secret))
                {
                    result["ok_combine"] = true;
                }

                // Test with k-1 shares (should fail or produce different result)
                try
                {
                    var subsetFail = shares.Take(k - 1).ToArray();
                    var recoveredFail = combiner.Reconstruction(subsetFail).ToByteArray();
                    
                    if (!recoveredFail.SequenceEqual(secret))
                    {
                        result["ok_fail_k_minus_1"] = true;
                    }
                }
                catch
                {
                    result["ok_fail_k_minus_1"] = true;
                }

                sw.Stop();
                result["time_ms"] = sw.Elapsed.TotalMilliseconds;
            }
            catch (Exception ex)
            {
                result["error"] = ex.Message;
            }

            Console.WriteLine(JsonSerializer.Serialize(result));
        }

        static byte[] HexToBytes(string hex)
        {
            int numberChars = hex.Length;
            byte[] bytes = new byte[numberChars / 2];
            for (int i = 0; i < numberChars; i += 2)
                bytes[i / 2] = Convert.ToByte(hex.Substring(i, 2), 16);
            return bytes;
        }
    }
}
