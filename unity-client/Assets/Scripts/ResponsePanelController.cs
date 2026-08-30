// ResponsePanelController.cs
//
// Phase 3 skeleton from docs/BUILD_PLAN.md.
//
// Wire this up to the MRTK floating panel's TextMeshPro component.
// Subscribe to BackendConnection.OnResponseReceived to display incoming
// LLM responses as they arrive.

using TMPro;
using UnityEngine;

public class ResponsePanelController : MonoBehaviour
{
    [Tooltip("TextMeshPro component on the MRTK panel that displays responses")]
    public TextMeshPro responseText;

    [Tooltip("Reference to the BackendConnection in the scene")]
    public BackendConnection backendConnection;

    void Start()
    {
        if (backendConnection != null)
        {
            backendConnection.OnResponseReceived += DisplayResponse;
        }

        if (responseText != null)
        {
            responseText.text = "Ready.";
        }
    }

    public void DisplayResponse(string text)
    {
        if (responseText != null)
        {
            responseText.text = text;
        }
    }

    // Wire this to an MRTK PressableButton's OnClick event for the
    // Phase 3 manual test flow (before voice input is added in Phase 4).
    public void SendTestPrompt()
    {
        if (responseText != null)
        {
            responseText.text = "Thinking...";
        }
        backendConnection?.SendPrompt("Say hello and confirm you're connected.");
    }

    void OnDestroy()
    {
        if (backendConnection != null)
        {
            backendConnection.OnResponseReceived -= DisplayResponse;
        }
    }
}
