using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class PopUpWindow : MonoBehaviour {

    [SerializeField]
    TextMeshProUGUI text;

    public void Exit() {
        Destroy(this.gameObject);
    }

    public void SetText(string text) {
        this.text.text = text;
    }
}
