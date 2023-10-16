using System;
using System.Collections.Generic;
using System.Reflection;

public class CommandLineOptions
{
    public string Version { get; set; } = "1.0.0";
    public string Channel { get; set; } = "default";
    public string ExportMethod { get; set; } = "default";

    public static CommandLineOptions Parse(string[] args)
    {
        CommandLineOptions options = new CommandLineOptions();

        Dictionary<string, string> parsedArgs = new Dictionary<string, string>();

        for (int i = 0; i < args.Length; i++)
        {
            string arg = args[i].Trim();

            if (arg.StartsWith("-"))
            {
                string key = arg.Substring(1);
                string value = i + 1 < args.Length ? args[i + 1].Trim() : null;

                parsedArgs[key] = value;
            }
        }

        Type optionsType = typeof(CommandLineOptions);
        PropertyInfo[] properties = optionsType.GetProperties();

        foreach (PropertyInfo property in properties)
        {
            if (parsedArgs.TryGetValue(property.Name.ToLower(), out string argValue))
            {
                property.SetValue(options, argValue);
            }
        }

        return options;
    }
}