using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ArrowHandle : MonoBehaviour {
    public enum Axis { X, Y, Z }
    public Axis axis;
    private Vector3 initialPosition;
    private Vector3 initialMousePosition;
    private bool dragging = false;

    void OnMouseDown() {
        dragging = true;
        initialPosition = transform.parent.position;
        initialMousePosition = GetMouseWorldPos();
    }

    void OnMouseUp() {
        dragging = false;
    }

    void Update() {
        if (dragging) {
            Vector3 currentMousePosition = GetMouseWorldPos();
            Vector3 delta = currentMousePosition - initialMousePosition;

            switch (axis) {
                case Axis.X:
                    transform.root.position = initialPosition + new Vector3(delta.x, 0, 0);
                    break;
                case Axis.Y:
                    transform.root.position = initialPosition + new Vector3(0, delta.y, 0);
                    break;
                case Axis.Z:
                    transform.root.position = initialPosition + new Vector3(0, 0, delta.z);
                    break;
            }
        }
    }

    Vector3 GetMouseWorldPos() {
        Vector3 mousePoint = Input.mousePosition;
        mousePoint.z = Camera.main.WorldToScreenPoint(transform.position).z;
        return Camera.main.ScreenToWorldPoint(mousePoint);
    }
}
