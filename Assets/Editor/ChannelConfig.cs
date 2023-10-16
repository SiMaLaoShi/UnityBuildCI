using System;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEditor;

[Serializable]
public class ChannelConfig
{
    [LabelText("App ID")] public string appId;
    [LabelText("App Name")] public string appName;
    [LabelText("P12 Password")] public string p12Pwd;
    [LabelText("Mac Password")] public string macPwd;

    [LabelText("Development Mobile Path")] public string devMobPath;

    [LabelText("Distribution Mobile Path")]
    public string disMobPath;

    [LabelText("Distribution P12 Path")] public string disP12Path;

    [LabelText("Development P12 Path")] public string devP12Path;

    [LabelText("Development Certificate")] public string devCer;

    [LabelText("Distribution Certificate")]
    public string disCer;

    [LabelText("Team ID")] public string teamId;

    [TabGroup("DevMobileProvisionData")] public MobileProvisionData DevMobileProvisionData = new MobileProvisionData();

    [TabGroup("DevMobileProvisionData")]
    [Button(ButtonSizes.Small)]
    private void ImportDev()
    {
        var filePath = EditorUtility.OpenFilePanel("Import dev.mobileprovision", "", "mobileprovision");
        DevMobileProvisionData = GetMobileProvisionData(filePath);
    }

    [TabGroup("DisMobileProvisionData")] public MobileProvisionData DisMobileProvisionData = new MobileProvisionData();

    [TabGroup("DisMobileProvisionData")]
    [Button(ButtonSizes.Small)]
    private void ImportDis()
    {
        var filePath = EditorUtility.OpenFilePanel("Import dis.mobileprovision", "", "mobileprovision");
        DisMobileProvisionData = GetMobileProvisionData(filePath);
        teamId = DisMobileProvisionData.TeamIdentifier;
    }

    [LabelText("Build Properties")] [DictionaryDrawerSettings()] [ShowInInspector]
    public Dictionary<string, string> BuildPropertys = new Dictionary<string, string>();

    [LabelText("Framework To Projects")] [DictionaryDrawerSettings()] [ShowInInspector]
    public Dictionary<string, bool> FrameworkToProjects = new Dictionary<string, bool>();

    [LabelText("Boolean Properties")] [DictionaryDrawerSettings()] [ShowInInspector]
    public Dictionary<string, bool> BooleanPropertys = new Dictionary<string, bool>();

    [LabelText("String Properties")] [DictionaryDrawerSettings()] [ShowInInspector]
    public Dictionary<string, string> StringPropertys = new Dictionary<string, string>();

    [LabelText("Integer Properties")] [DictionaryDrawerSettings()] [ShowInInspector]
    public Dictionary<string, int> IntegerPropertys = new Dictionary<string, int>();

    public MobileProvisionData GetMobileProvisionData(string path)
    {
        return MobileProvisionParser.ParseMobileProvision(path);
    }
}