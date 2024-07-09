using System.Collections;
using System.Collections.Generic;
using SimpleFileBrowser;
using System.IO;
using UnityEngine;
using Dummiesman;

public class FileUploading : MonoBehaviour {
    GameObject loadedObject;
    string error = string.Empty;
    GameObject loadingObject;
    public Transform loadingPosition;


    public void OpenFileBrowser() {
        FileBrowser.ShowLoadDialog(OnFileSelected, null, FileBrowser.PickMode.Files, false, null, "Select OBJ File", "Select");
    }

    // Works only with .obj
    void OnFileSelected(string[] paths) {
        if (paths.Length > 0) {
            string path = paths[0];
            print(path);
            if (Path.GetExtension(path).ToLower() == ".obj") {
                LoadObjModel(path);
            } else {
                PopUp.Instance.ShowPopUpWindow("Selected file is not an OBJ model.");
            }
        }
    }

    void LoadObjModel(string path) {
        if (loadingObject != null)
            Destroy(loadingObject);
        loadingObject = new OBJLoader().Load(path);
        loadingObject.transform.position = loadingPosition.position;
    }
}
