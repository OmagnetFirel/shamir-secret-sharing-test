using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Text.Json;
using mtanksl.ShamirSecretSharing;

namespace MtankslShamirTest
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
                ["lib"] = "mtanksl.ShamirSecretSharing",
                ["ok_split"] = false,
                ["ok_combine"] = false,
                ["ok_fail_k_minus_1"] = false,
                ["shares_count"] = n,
                ["time_ms"] = 0.0
            };

            try
            {
                byte[] secretBytes = HexToBytes(secretHex);
                
                // Converter bytes para base64 string (mtanksl trabalha com strings)
                string secret = Convert.ToBase64String(secretBytes);
                
                var sw = Stopwatch.StartNew();

                using (var sss = new ShamirSecretSharing())
                {
                    // Split: usa string
                    var shares = sss.Split(k, n, secret);

                    if (shares != null && shares.Length == n)
                    {
                        result["ok_split"] = true;
                    }

                    // Combine: usa k shares
                    var subset = shares.Take(k).ToArray();
                    string recoveredSecret = sss.Join(subset);

                    // Converter de volta para bytes
                    byte[] recoveredBytes = Convert.FromBase64String(recoveredSecret);

                    if (recoveredBytes.SequenceEqual(secretBytes))
                    {
                        result["ok_combine"] = true;
                    }

                    // Test com k-1 shares (deve falhar)
                    try
                    {
                        var subsetFail = shares.Take(k - 1).ToArray();
                        string recoveredFail = sss.Join(subsetFail);
                        byte[] recoveredFailBytes = Convert.FromBase64String(recoveredFail);
                        
                        if (!recoveredFailBytes.SequenceEqual(secretBytes))
                        {
                            result["ok_fail_k_minus_1"] = true;
                        }
                    }
                    catch
                    {
                        result["ok_fail_k_minus_1"] = true;
                    }
                }

                sw.Stop();
                result["time_ms"] = Math.Round(sw.Elapsed.TotalMilliseconds, 3);
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
