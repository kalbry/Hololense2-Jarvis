// BackendConnection.cs
//
// Phase 3 skeleton from docs/BUILD_PLAN.md.
//
// Requires the NativeWebSocket package (or equivalent WebSocket client):
// https://github.com/endel/NativeWebSocket
// Install via Unity Package Manager -> Add package from git URL.
//
// Attach this to a single GameObject in your scene (e.g. "BackendConnection").
// Set backendHost / backendPort in the Inspector to your backend PC's LAN IP
// and the port from backend/config/config.yaml (default 8765).

using System;
using System.Text;
using UnityEngine;
using NativeWebSocket;

[Serializable]
public class PromptMessage
{
    public string type = "prompt";
    public string text;
}

[Serializable]
public class ResponseMessage
{
    public string type;
    public string text;
}

public class BackendConnection : MonoBehaviour
{
    [Header("Backend connection")]
    [Tooltip("LAN IP address of the backend PC running relay/server.py")]
    public string backendHost = "192.168.1.100";

    [Tooltip("Must match server.port in backend/config/config.yaml")]
    public int backendPort = 8765;

    [Header("Events")]
    public Action<string> OnResponseReceived;
    public Action OnConnected;
    public Action OnDisconnected;

    private WebSocket websocket;

    async void Start()
    {
        string url = $"ws://{backendHost}:{backendPort}";
        websocket = new WebSocket(url);

        websocket.OnOpen += () =>
        {
            Debug.Log("[BackendConnection] Connected to " + url);
            OnConnected?.Invoke();
        };

        websocket.OnError += (e) =>
        {
            Debug.LogError("[BackendConnection] Error: " + e);
        };

        websocket.OnClose += (e) =>
        {
            Debug.Log("[BackendConnection] Closed: " + e);
            OnDisconnected?.Invoke();
        };

        websocket.OnMessage += (bytes) =>
        {
            string json = Encoding.UTF8.GetString(bytes);
            var response = JsonUtility.FromJson<ResponseMessage>(json);
            if (response != null && response.type == "response")
            {
                Debug.Log("[BackendConnection] Response: " + response.text);
                OnResponseReceived?.Invoke(response.text);
            }
        };

        await websocket.Connect();
    }

    public void SendPrompt(string text)
    {
        if (websocket == null || websocket.State != WebSocketState.Open)
        {
            Debug.LogWarning("[BackendConnection] Not connected — cannot send prompt.");
            return;
        }

        var message = new PromptMessage { text = text };
        string json = JsonUtility.ToJson(message);
        websocket.SendText(json);
    }

    void Update()
    {
#if !UNITY_WEBGL || UNITY_EDITOR
        websocket?.DispatchMessageQueue();
#endif
    }

    private async void OnApplicationQuit()
    {
        if (websocket != null)
        {
            await websocket.Close();
        }
    }
}
