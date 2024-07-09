using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

public class webComm : MonoBehaviour {

    public string serverUrl = "http://127.0.0.1:5000/upload";
    public string dataToSend = "Pepa je bùh!";

    private void Start() {
        StartUpload();
    }

    public void StartUpload() {
        StartCoroutine(UploadDataCoroutine());
    }

    IEnumerator UploadDataCoroutine() {
        // Create form data
        WWWForm form = new WWWForm();
        form.AddField("myData", dataToSend);

        // Send request
        UnityWebRequest www = UnityWebRequest.Post(serverUrl, form);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success) {
            Debug.LogError("Error uploading data: " + www.error);
        } else {
            Debug.Log("Data uploaded successfully!");
            Debug.Log("Server response: " + www.downloadHandler.text);
        }
    }
}
