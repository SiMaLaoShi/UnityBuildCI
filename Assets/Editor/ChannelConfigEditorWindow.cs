using System;
using System.IO;
using System.Text.RegularExpressions;
using LitJson;
using UnityEditor;
using UnityEngine;
using Sirenix.OdinInspector.Editor;

public class ChannelConfigWindow : OdinEditorWindow

{
    [SerializeField]
    private ChannelConfig config;

    [MenuItem("Window/Channel Config")]
    public static void OpenWindow()
    {
        // 创建并显示窗口
        ChannelConfigWindow window = GetWindow<ChannelConfigWindow>();
        window.titleContent = new GUIContent("Channel Config");
        window.Show();
    }

    // 在窗口中绘制 GUI
    private void OnGUI()
    {
        base.OnGUI();

        // 在这里绘制你的配置字段
        if (GUILayout.Button("Import Config"))
        {
            ImportConfig();
        }

        // 添加导出按钮
        if (GUILayout.Button("Export Config as JSON"))
        {
            ExportConfigAsJson();
        }
    }
    public void ImportConfig()
    {
        string filePath = EditorUtility.OpenFilePanel("Import Config as JSON", "", "json");
        if (File.Exists(filePath))
        {
            string json = File.ReadAllText(filePath);
            config = JsonMapper.ToObject<ChannelConfig>(json);
            Debug.Log("Config imported.");
        }
        else
        {
            Debug.LogError("Config file not found.");
        }
    }
    
    // 导出配置为 JSON 的方法
    private void ExportConfigAsJson()
    {
        // 将配置对象转换为 JSON 字符串
        JsonWriter jw = new JsonWriter();
        jw.PrettyPrint = true;
        JsonMapper.ToJson(config, jw);
        var json = Regex.Unescape(jw.TextWriter.ToString());
        Debug.Log(json);
        // 选择导出路径
        string exportPath = EditorUtility.SaveFilePanel("Export Config as JSON", "", "config.json", "json");
        // 如果选择了有效的导出路径
        if (!string.IsNullOrEmpty(exportPath))
        {
            // 将 JSON 字符串写入文件
            File.WriteAllText(exportPath, json);
            Debug.Log("Config exported as JSON: " + exportPath);
        }
    }
}