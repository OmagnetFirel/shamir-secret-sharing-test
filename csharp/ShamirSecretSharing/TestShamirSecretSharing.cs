using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using ShamirSecretSharing; 

class TestShamirSecretSharing
{
    static void Main(string[] args)
    {
        var pargs = ParseArgs(args);
        string secretHex = pargs["secret"].ToLower();
        int n = int.Parse(pargs["n"]);
        int k = int.Parse(pargs["k"]);

        byte[] secretBytes = HexToBytes(secretHex);
        string secretString = Encoding.UTF8.GetString(secretBytes);

        var result = new Dictionary<string, object>
        {
            ["lang"] = "csharp",
            ["lib"] = "ShamirSecretSharing"
        };

        var sw = Stopwatch.StartNew();

        var sss = new ShamirSecretSharingService(); 
        Share[] shares = Array.Empty<Share>();

        // 1) split
        try
        {
            shares = sss.SplitSecret(secretString, n, k); // Share[] [attached_file:1]
            result["ok_split"] = shares != null && shares.Length == n;
            result["shares_count"] = shares != null ? shares.Length : 0;
        }
        catch (Exception e)
        {
            result["ok_split"] = false;
            result["shares_count"] = 0;
            result["error_split"] = e.ToString();
            shares = Array.Empty<Share>();
        }

        // 2) combine com k shares
        try
        {
            if (shares != null && shares.Length >= k)
            {
                Share[] subset = shares.Take(k).ToArray();
                string rec = sss.ReconstructSecretString(subset, k); // [attached_file:1]
                bool okCombine = (rec == secretString);
                result["ok_combine"] = okCombine;
            }
            else
            {
                result["ok_combine"] = false;
            }
        }
        catch (Exception e)
        {
            result["ok_combine"] = false;
            result["error_combine"] = e.ToString();
        }

        // 3) falha com k-1 shares
        try
        {
            if (shares != null && shares.Length >= k)
            {
                bool okFail;
                try
                {
                    Share[] subset = shares.Take(k - 1).ToArray();
                    string rec2 = sss.ReconstructSecretString(subset, k);
                    okFail = (rec2 != secretString);
                }
                catch (Exception)
                {
                    okFail = true;
                }
                result["ok_fail_k_minus_1"] = okFail;
            }
            else
            {
                result["ok_fail_k_minus_1"] = false;
            }
        }
        catch (Exception e)
        {
            result["ok_fail_k_minus_1"] = false;
            result["error_fail_k_minus_1"] = e.ToString();
        }

        sw.Stop();
        result["time_ms"] = Math.Round(sw.Elapsed.TotalMilliseconds, 3);

        Console.WriteLine(ToJson(result));
    }

    static Dictionary<string, string> ParseArgs(string[] args)
    {
        var dict = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        for (int i = 0; i < args.Length; i += 2)
        {
            string key = args[i].TrimStart('-');
            dict[key] = args[i + 1];
        }
        return dict;
    }

    static byte[] HexToBytes(string hex)
    {
        hex = hex.Replace("0x", "").ToLower();
        int len = hex.Length;
        var bytes = new byte[len / 2];
        for (int i = 0; i < len; i += 2)
            bytes[i / 2] = Convert.ToByte(hex.Substring(i, 2), 16);
        return bytes;
    }

    static string ToJson(Dictionary<string, object> map)
    {
        var sb = new StringBuilder();
        sb.Append("{");
        bool first = true;
        foreach (var kv in map)
        {
            if (!first) sb.Append(",");
            first = false;
            sb.Append("\"").Append(kv.Key).Append("\":");
            if (kv.Value is string s)
                sb.Append("\"").Append(s.Replace("\"", "\\\"")).Append("\"");
            else if (kv.Value is bool b)
                sb.Append(b ? "true" : "false");
            else
                sb.Append(kv.Value.ToString());
        }
        sb.Append("}");
        return sb.ToString();
    }
}
