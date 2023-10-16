using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml.Linq;
using Sirenix.OdinInspector;
using UnityEngine;

[Serializable]
public class MobileProvisionData
{
    [LabelText("UUID")] 
    public string UUID;
    [LabelText("Name")]
    public string Name;
    [LabelText("TeamIdentifier")]
    public string TeamIdentifier;
    [LabelText("TeamName")]
    public string TeamName;
}

public static class MobileProvisionParser
{
    private static string ios = "";
    public static MobileProvisionData ParseMobileProvision(string filePath)
    {
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException("Mobile provision file not found.", filePath);
        }
// 使用正则表达式提取 <plist> 标签中的内容
        string pattern = @"<plist[^>]*>(.*?)</plist>";
        var xml = "";
        Match match = Regex.Match(File.ReadAllText(filePath), pattern, RegexOptions.Singleline);
        if (match.Success)
        {
            xml = match.Groups[1].Value.Trim();
            Debug.Log(xml);
        }
        else
        {
            Debug.LogError("提取失败");
            return null;
        }
        try
        {
            XDocument doc = XDocument.Parse(xml);
            XElement dict = doc.Element("dict");

            if (dict != null)
            {
                MobileProvisionData provisionData = new MobileProvisionData();

                List<XElement> keys = dict.Elements("key").ToList();
                List<XElement> values = dict.Elements().Where(e => e.Name != "key").ToList();

                for (int i = 0; i < keys.Count; i++)
                {
                    XElement keyElement = keys[i];
                    string key = keyElement.Value;

                    XElement valueElement = values[i];

                    switch (key)
                    {
                        case "UUID":
                            provisionData.UUID = valueElement.Value;
                            break;
                        case "Name":
                            provisionData.Name = valueElement.Value;
                            break;
                        case "TeamIdentifier":
                            provisionData.TeamIdentifier = valueElement.Elements("string").FirstOrDefault()?.Value;
                            break;
                        case "TeamName":
                            provisionData.TeamName = valueElement.Value;
                            break;
                    }
                }

                return provisionData;
            }
        }
        catch (Exception ex)
        {
            throw new Exception("Failed to parse mobile provision file.", ex);
        }

        return null;
    }
}