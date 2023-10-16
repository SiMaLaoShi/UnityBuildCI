using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using LitJson;
using UnityEditor;
using UnityEditor.Callbacks;
using UnityEditor.iOS.Xcode;
using Debug = UnityEngine.Debug;
using Debugger = UnityEngine.Debug;

public class BuildPip : Editor
{
    private static ChannelConfig channelConfig = new ChannelConfig();
    private static string CHANNEL_ROOT = Path.Combine(System.Environment.CurrentDirectory, "Channel");
    private const string CONFIG_NAME = "config.json";
    private static string CHANNEL_Path = "";
    
    [MenuItem("Tools/BuildIpa")]
    public static void BuildIpa()
    {
        //todo 实现渠道加载
        CHANNEL_Path = Path.Combine(CHANNEL_ROOT, "001");
        var p = Path.Combine(CHANNEL_Path, CONFIG_NAME);
        var jsonStr = File.ReadAllText(p);
        channelConfig = JsonMapper.ToObject<ChannelConfig>(jsonStr);
        if (null == channelConfig)
        {
            Debug.Log("渠道配置错误");
            return;
        }

        PlayerSettings.applicationIdentifier = channelConfig.appId;
        PlayerSettings.productName = channelConfig.appName;
        
        Debug.Log(jsonStr);
        string outputPath = "Builds/xcode";
        BuildPipeline.BuildPlayer(new[] {"Assets/Scenes/SampleScene.unity"}, outputPath, BuildTarget.iOS, BuildOptions.None);
        var userPodFile = true;
        if (userPodFile)
            usepodinstall(outputPath);
        xcodebuild_archive(outputPath, false, true);
        generate_export_options_plist(outputPath, exportMethod_development, channelConfig.teamId, channelConfig.appId, channelConfig.DevMobileProvisionData.Name);
        xcodebuild_export(outputPath, true, channelConfig.teamId, exportMethod_development);
        
        generate_export_options_plist(outputPath, exportMethod_appstore, channelConfig.teamId, channelConfig.appId,
            channelConfig.DisMobileProvisionData.Name);
        xcodebuild_export(outputPath, true, channelConfig.teamId, exportMethod_appstore);
    }

    static void ImportP12()
    {
        Debugger.Log("执行 ImportP12");
        var shSb = new StringBuilder();
        shSb.AppendLine("#!/bin/sh");
        //默认钥匙串
        shSb.AppendLine("security default-keychain -s ~/Library/Keychains/login.keychain");
        //解锁指定的钥匙串
        shSb.AppendLine($"security unlock-keychain -p {channelConfig.p12Pwd}");
        //导入开发证书
        shSb.AppendLine($"security import {channelConfig.devP12Path} -k ~/Library/Keychains/login.keychain -P {channelConfig.p12Pwd}");
        shSb.AppendLine($"security import {channelConfig.devCer} -k ~/Library/Keychains/login.keychain -P {channelConfig.p12Pwd}");
        //导入发布证书
        shSb.AppendLine($"security import {channelConfig.disP12Path} -k ~/Library/Keychains/login.keychain -P {channelConfig.p12Pwd}");
        shSb.AppendLine($"security import {channelConfig.disCer} -k ~/Library/Keychains/login.keychain -P {channelConfig.p12Pwd}");
        //导入开发描述文件
        shSb.AppendLine($"cp {channelConfig.devMobPath} ~/Library/MobileDevice/Provisioning\\ Profiles/{channelConfig.DevMobileProvisionData.UUID}.mobileprovision");
        //导入发布描述文件
        shSb.AppendLine($"cp {channelConfig.disMobPath} ~/Library/MobileDevice/Provisioning\\ Profiles/{channelConfig.DevMobileProvisionData.UUID}.mobileprovision");
        //修改访问权限
        shSb.AppendLine(
            $"security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k {channelConfig.macPwd} login.keychain");
        int exitCode;
        var path = Path.Combine(System.Environment.CurrentDirectory, "importP12.sh");
        File.WriteAllText(path, shSb.ToString());
        Debugger.Log(shSb.ToString());
        var bash = "/bin/sh";
        if (!ExecuteCmd(bash, path, out exitCode))
            Debugger.LogError("P12导入失败 : " + exitCode);
        else
            Debugger.Log("P12导入成功 : " + exitCode);
    }

    private static Dictionary<string, string> DebugSignInfo = new Dictionary<string, string>()
    {
        {"CODE_SIGN_IDENTITY", ""},
        {"PROVISIONING_PROFILE", ""},
        {"PROVISIONING_PROFILE_SPECIFIER", ""},
        {"DEVELOPMENT_TEAM", ""}
    };

    private static Dictionary<string, string> ReleaseSignInfo = new Dictionary<string, string>()
    {
        {"CODE_SIGN_IDENTITY", ""},
        {"PROVISIONING_PROFILE", ""},
        {"PROVISIONING_PROFILE_SPECIFIER", ""},
        {"DEVELOPMENT_TEAM", ""}
    };

    private static void AddSign(PBXProject project)
    {
        SetSignInfo(DebugSignInfo, channelConfig.DevMobileProvisionData);
        SetSignInfo(ReleaseSignInfo, channelConfig.DisMobileProvisionData);
        string targetGuid = project.GetUnityMainTargetGuid();
        foreach (string configName in project.BuildConfigNames())
        {
            string configGuid = project.BuildConfigByName(targetGuid, configName);
            if (configName.Contains("Release"))
            {
                foreach (KeyValuePair<string, string> pair in ReleaseSignInfo)
                {
                    project.SetBuildPropertyForConfig(configGuid, pair.Key, pair.Value);
                    project.SetBuildPropertyForConfig(configGuid, "CODE_SIGN_IDENTITY[sdk=iphoneos*]",
                        "iPhone Distribution");
                }
            }
            else
            {
                foreach (KeyValuePair<string, string> pair in DebugSignInfo)
                {
                    project.SetBuildPropertyForConfig(configGuid, pair.Key, pair.Value);
                    project.SetBuildPropertyForConfig(configGuid, "CODE_SIGN_IDENTITY[sdk=iphoneos*]",
                        "iPhone Developer");
                }
            }
        }
    }

    private static void SetSignInfo(Dictionary<string, string> signInfo, MobileProvisionData mobileProvisionData)
    {
        signInfo["CODE_SIGN_IDENTITY"] = mobileProvisionData.TeamName;
        signInfo["PROVISIONING_PROFILE"] = mobileProvisionData.UUID;
        signInfo["PROVISIONING_PROFILE_SPECIFIER"] = mobileProvisionData.Name;
        signInfo["DEVELOPMENT_TEAM"] = mobileProvisionData.TeamIdentifier;
    }

    // ios版本xcode工程维护代码  
    [PostProcessBuild(999)]
    static void OnPostprocessBuild(BuildTarget buildTarget, string path)
    {
        if (buildTarget != BuildTarget.iOS)
        {
            return;
        }
        Debug.Log("OnPostprocessBuild");
        ImportP12();

        string projPath = PBXProject.GetPBXProjectPath(path);
        PBXProject proj = new PBXProject();
        proj.ReadFromString(File.ReadAllText(projPath));

        // 获取当前项目名字
#if UNITY_2019_3_OR_NEWER
        string target = proj.GetUnityMainTargetGuid();
#else
        string target = proj.TargetGuidByName(PBXProject.GetUnityTargetName());
#endif


        // 修改plist  方法
        string plistPath = path + "/Info.plist";
        PlistDocument plist = new PlistDocument();
        plist.ReadFromString(File.ReadAllText(plistPath));
        PlistElementDict rootDict = plist.root;

        DoBaseXCodeSetting(proj, target, rootDict);
        // 获取当前项目名字
#if UNITY_2019_3_OR_NEWER
        string targetGuid = proj.GetUnityFrameworkTargetGuid();
        proj.SetBuildProperty(targetGuid, "ENABLE_BITCODE", "NO");
        foreach (var kv in channelConfig.BuildPropertys)
        {
            proj.SetBuildProperty(targetGuid, kv.Key, kv.Value);
        }
#else
#endif
        
        AddSign(proj);


        //remove exist on suspend if it exists!
        string existsOnSuspendKey = "UIApplicationExitsOnSuspend";
        if (rootDict.values.ContainsKey(existsOnSuspendKey))
        {
            rootDict.values.Remove(existsOnSuspendKey);
        }

        // 保存plist  
        plist.WriteToFile(plistPath);

        // 保存pbx
        File.WriteAllText(projPath, proj.WriteToString());
    }

    static void DoBaseXCodeSetting(PBXProject proj, string target, PlistElementDict rootDict)
    {
        // Do37XCodeSetting(proj, target, rootDict);

        // 对所有的编译配置设置选项  
        proj.SetBuildProperty(target, "ENABLE_BITCODE", "NO");

        // 设置 Code Signing Style 为 Manual
        proj.SetBuildProperty(target, "CODE_SIGN_STYLE", "Manual");
        // 添加依赖库  方法
        
        proj.SetBuildProperty(target, "LD_RUNPATH_SEARCH_PATHS", "$(inherited) @executable_path/Frameworks");

        foreach (var kv in channelConfig.BuildPropertys)
        {
            proj.SetBuildProperty(target, kv.Key, kv.Value);
        }

        // unity3d
        proj.AddFrameworkToProject(target, "UnityFramework.framework", true);


        foreach (var kv in channelConfig.FrameworkToProjects)
        {
            proj.AddFrameworkToProject(target, kv.Key, kv.Value);
        }
        // 修改 PList

        // IOS新版SDK必须的权限

        foreach (var kv in channelConfig.StringPropertys)
        {
            rootDict.SetString(kv.Key, kv.Value);
        }
        
        foreach (var kv in channelConfig.BooleanPropertys)
        {
            rootDict.SetBoolean(kv.Key, kv.Value);
        }

        foreach (var kv in channelConfig.IntegerPropertys)
        {
            rootDict.SetInteger(kv.Key, kv.Value);
        }
        
        rootDict["UIRequiredDeviceCapabilities"].AsArray().values.Clear();
        
    }

    public static bool ExecuteCmd(string filename, string arguments, out int exitCode, string workdir = null,
        DataReceivedEventHandler recv = null)
    {
        exitCode = 0;
        UnityEngine.Debug.Log("ExecuteCmd( " + filename + " , " + arguments + " )");

        try
        {
            Process proc = new Process();
            proc.StartInfo.FileName = filename;
            proc.StartInfo.Arguments = arguments;
            if (string.IsNullOrEmpty(workdir))
                workdir = System.Environment.CurrentDirectory;
            UnityEngine.Debug.Log("Walk Directory:" + workdir);
            proc.StartInfo.WorkingDirectory = workdir;
            proc.StartInfo.UseShellExecute = false;
            proc.StartInfo.StandardOutputEncoding = System.Text.Encoding.UTF8;
            proc.StartInfo.RedirectStandardOutput = true;
            proc.StartInfo.CreateNoWindow = true;
            proc.StartInfo.StandardErrorEncoding = System.Text.Encoding.UTF8;
            proc.StartInfo.RedirectStandardError = true;
            proc.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
            if (null == recv)
                proc.OutputDataReceived += new DataReceivedEventHandler((sender, arg) =>
                {
                    UnityEngine.Debug.Log(arg.Data);
                });
            else
                proc.OutputDataReceived += recv;
            proc.ErrorDataReceived +=
                new DataReceivedEventHandler((sender, arg) => { UnityEngine.Debug.Log(arg.Data); });
            proc.Start();
            proc.BeginErrorReadLine();
            proc.BeginOutputReadLine();

            proc.WaitForExit();

            exitCode = proc.ExitCode;

            if (exitCode != 0)
                UnityEngine.Debug.LogError("Execute Command: " + filename + " " + arguments + " Exit Code=" + exitCode);

            return exitCode == 0;
        }
        catch (System.Exception ex)
        {
            UnityEngine.Debug.LogException(ex);
        }

        return false;
    }

    #region xcode相关操作

    public const string xcodebuild = "xcodebuild";
    public const string UnityProjectFileName = "Unity-iPhone.xcodeproj";
    public const string UnityProjectxcworkspace = "Unity-iPhone.xcworkspace";
    public const string ArchiveFileName = "SGAME.xcarchive";
    public const string ExportOptionsPListFileName = "ExportOptions.plist";
    public const string exportMethod_appstore = "app-store";
    public const string exportMethod_development = "development";
    public const string ExportFolder_appstore = "IPA_OUTPUT_APPSTORE";
    public const string ExportFolder = "IPA_OUTPUT";

    public static string GetBuildType(bool debug)
    {
        return debug ? "Debug" : "Release";
    }

    public static int xcodebuild_archive(string projectFolder, bool debug, bool autoSign, bool userPodFile = true)
    {
        //xcodebuild archive -project ./sgame_xcode/Unity-iPhone.xcodeproj -scheme Unity-iPhone -archivePath ./sgame.xcarchive
        StringBuilder args = new StringBuilder();
        args.Append(" build archive");
        if (autoSign)
        {
            args.Append(" -allowProvisioningUpdates");
        }
        
        Debugger.Log("usepodfile=" + userPodFile.ToString());
        //使用cocapods 方式命令操作的对象不一致
        if (userPodFile)
        {
            args.Append(" -workspace ").Append(Path.Combine(projectFolder, UnityProjectxcworkspace));
        }
        else
        {
            args.Append(" -project ").Append(Path.Combine(projectFolder, UnityProjectFileName));
        }

        args.Append(" -scheme Unity-iPhone");
        args.Append(" -archivePath ").Append(Path.Combine(projectFolder, ArchiveFileName));
        args.Append(" -configuration ").Append(GetBuildType(debug));
        if (!autoSign)
        {
            args.Append(" -UseModernBuildSystem=NO"); // xcode10
        }

        args.Append(" -destination 'generic/platform=iOS'");

        Debugger.Log(xcodebuild + " " + args.ToString());

        int exitCode;
        if (!ExecuteCmd(xcodebuild, args.ToString(), out exitCode))
            Debugger.Log("xcodebuild archive return : " + exitCode);

        return exitCode;
    }
    
    public static bool usepodinstall(string packFullPath)
    {
        Debugger.Log("pod install ...");
        string src = Path.Combine(CHANNEL_Path, "Podfile");
        string dst = Path.Combine(packFullPath, "Podfile");

        Debugger.Log("usepodinstall src: " + src + ",dst: " + dst);

        if (!File.Exists(src))
        {
            Debugger.Log("Channel Podfile Not Found");
            return false;
        }
        File.Copy(src, dst,true);
            
        int exitCode;
        if (!ExecuteCmd("ls", "", out exitCode, packFullPath))
        {
            Debugger.LogError("Execute ls failed.exit code = " + exitCode);
            return false;
        }
        if (!ExecuteCmd("pod", "install", out exitCode, packFullPath))
        {
            Debugger.LogError("Execute pod install failed, exit code = " + exitCode);
            return false;
        }
        if (!ExecuteCmd("chmod", "-R 777 Pods", out exitCode, packFullPath))
        {
            Debugger.Log("chmod pods failed, exit code = " + exitCode);
            return false;
        }
            
        if (!ExecuteCmd("pod", "install", out exitCode, packFullPath))
        {
            Debugger.Log("pod pods install, exit code = " + exitCode);
            return false;
        }

        return true;
    }

    public static void generate_export_options_plist(string projectFolder, string method, string teamID, string appId,
        string profileID)
    {
        //method: Describes how Xcode should export the archive. Available options: app-store, package, ad-hoc, enterprise, development, developer-id, and mac-application. The list of options varies based on the type of archive. Defaults to development.
        string filepath = Path.Combine(projectFolder, ExportOptionsPListFileName);
        StringBuilder res = new StringBuilder();
        res.AppendLine("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        res.AppendLine(
            "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">");
        res.AppendLine("<plist version=\"1.0\">");
        res.AppendLine("<dict>");
        if (method != exportMethod_appstore)
        {
            res.AppendLine("    <key>compileBitcode</key>");
            res.AppendLine("    <false/>");
        }

        res.AppendLine("    <key>destination</key>");
        res.AppendLine("    <string>export</string>");
        res.AppendLine("    <key>method</key>");
        res.AppendLine("    <string>" + method + "</string>");

        res.AppendLine("    <key>provisioningProfiles</key>");
        res.AppendLine("    <dict>");
        {
            res.AppendLine("        <key>" + appId + "</key>");
            res.AppendLine("        <string>" + profileID + "</string>");
        }
        res.AppendLine("    </dict>");

        if (method == exportMethod_development)
        {
            res.AppendLine("    <key>signingCertificate</key>");
            res.AppendLine("    <string>iPhone Developer</string>");
        }
        else
        {
            res.AppendLine("    <key>signingCertificate</key>");
            res.AppendLine("    <string>iPhone Distribution</string>");
        }

        res.AppendLine("    <key>signingStyle</key>");
        res.AppendLine("    <string>manual</string>");

        res.AppendLine("    <key>stripSwiftSymbols</key>");
        res.AppendLine("    <true/>");
        res.AppendLine("    <key>teamID</key>");
        res.AppendLine("    <string>" + teamID + "</string>");

        if (method == exportMethod_appstore)
        {
            res.AppendLine("    <key>uploadSymbols</key>");
            res.AppendLine("    <true/>");
        }
        else
        {
            res.AppendLine("    <key>thinning</key>");
            res.AppendLine("    <string>&lt;none&gt;</string>");
        }

        res.AppendLine("</dict>");
        res.AppendLine("</plist>");
        res.AppendLine();

        File.WriteAllText(filepath, res.ToString());
    }

    public static int xcodebuild_export(string projectFolder, bool debug, string teamID, string exportMethod)
    {
        //xcodebuild -exportArchive -archivePath ./sgame.xcarchive -exportPath ./sgame_dev_ipa -exportOptionsPlist ./sgame_xcode/ExportOptions.plist -allowProvisioningUpdates -configuration Debug
        StringBuilder args = new StringBuilder();
        args.Append("-exportArchive");
        args.Append(" -allowProvisioningUpdates");
        args.Append(" -archivePath ").Append(Path.Combine(projectFolder, ArchiveFileName));
        if (exportMethod == exportMethod_appstore)
        {
            args.Append(" -exportPath ").Append(Path.Combine(projectFolder, ExportFolder_appstore));
        }
        else
        {
            args.Append(" -exportPath ").Append(Path.Combine(projectFolder, ExportFolder));
        }

        args.Append(" -exportOptionsPlist ").Append(Path.Combine(projectFolder, ExportOptionsPListFileName));
        args.Append(" -configuration ").Append(GetBuildType(debug));

        Debugger.Log(xcodebuild + " " + args.ToString());

        int exitCode;
        if (!ExecuteCmd(xcodebuild, args.ToString(), out exitCode))
            Debugger.Log("xcodebuild export return : " + exitCode);
        return exitCode;
    }

    #endregion
}