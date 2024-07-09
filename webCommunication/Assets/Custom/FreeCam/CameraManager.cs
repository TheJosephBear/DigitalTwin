using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraManager : MonoBehaviour {
    
    FreeCam freeCam;


    void Start() {
        freeCam = GetComponent<FreeCam>();
    }

    void Update() {
        // on RightClick move
        if (Input.GetMouseButtonDown(1)) {
            freeCam.ToggleFreeCam(true);
        } else if (Input.GetMouseButtonUp(1)) {
            freeCam.ToggleFreeCam(false);
        }

        // on Shift move
        /*
        if (Input.GetKeyDown(KeyCode.LeftShift)) {
            freeCam.ToggleFreeCam(true);
        } else if (Input.GetKeyUp(KeyCode.LeftShift)) {
            freeCam.ToggleFreeCam(false);
        }
        */
    }
}
