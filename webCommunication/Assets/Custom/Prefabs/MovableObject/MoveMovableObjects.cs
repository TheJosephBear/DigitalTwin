using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MoveMovableObjects : MonoBehaviour {

    public GameObject pivotArrows;
    GameObject selectedObject;
    GameObject selectedObjectArrows;


    void Update() {
        if (Input.GetMouseButtonDown(0)) {
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            RaycastHit hit;
            if (selectedObject == null) {
                // Vybrat
                if (Physics.Raycast(ray, out hit) && hit.collider.gameObject.layer == LayerMask.NameToLayer("Movable")) {
                    SelectObject(hit.collider.gameObject);
                }
            } else{
                //Zrušit výbìr
                if (Physics.Raycast(ray, out hit) && hit.collider.gameObject.transform.root.gameObject.name != selectedObject.name) {
                    DeselectObject();
                }
            }
        }
    }

    void SelectObject(GameObject obj) {
        selectedObject = obj;
        StartMovingObject();
    }

    void DeselectObject() {
        selectedObject = null;
        Destroy(selectedObjectArrows);
        selectedObjectArrows = null;
    }

    public void StartMovingObject() {
        selectedObjectArrows = Instantiate(pivotArrows, selectedObject.transform);
    }
}
