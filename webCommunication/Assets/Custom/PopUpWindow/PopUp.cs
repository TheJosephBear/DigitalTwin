using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PopUp : MonoBehaviour {

    public static PopUp Instance;
    public GameObject PopUpPrefab;

    void Awake() {
        if (Instance == null) {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        } else {
            Destroy(gameObject);
        }
    }

    public void ShowPopUpWindow(string text) {
        PopUpWindow pw = Instantiate(PopUpPrefab).GetComponent<PopUpWindow>();
        pw.SetText(text);
    }
    
}
