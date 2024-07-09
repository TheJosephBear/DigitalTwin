using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FreeCam : MonoBehaviour {

    public GameObject vCam;
    public float movementSpeed = 10f;
    public float mouseSensitivity = 2f;
    public float slowdownSpeed = 5f;

    float yaw = 0f;
    float pitch = 0f;
    Vector3 currentVelocity;

    bool canMove = false;


    void Update() {
        if (canMove) {
            MouseLook();
            Movement();
        }
    }

    public void ToggleFreeCam(bool enable) {
        //vCam.SetActive(enable);
        canMove = enable;
        if(enable) {
            // hide cursor
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        } else {
            // show cursor
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }
    }

    void MouseLook() {
        yaw += Input.GetAxis("Mouse X") * mouseSensitivity;
        pitch -= Input.GetAxis("Mouse Y") * mouseSensitivity;
        pitch = Mathf.Clamp(pitch, -90f, 90f);
        // Apply
        vCam.transform.eulerAngles = new Vector3(pitch, yaw, 0f);
    }

    void Movement() {
        float horizontalInput = Input.GetAxis("Horizontal");
        float verticalInput = Input.GetAxis("Vertical");
        Vector3 forwardMovement = vCam.transform.forward * verticalInput;
        Vector3 rightMovement = vCam.transform.right * horizontalInput;
        Vector3 movement = (forwardMovement + rightMovement).normalized * movementSpeed * Time.deltaTime;
        if (Input.GetKey(KeyCode.E)) {
            movement.y += movementSpeed * Time.deltaTime;
        }
        if (Input.GetKey(KeyCode.Q)) {
            movement.y -= movementSpeed * Time.deltaTime;
        }
        // Slow down smoothly if not moving forward
        if (verticalInput == 0) {
            movement = Vector3.SmoothDamp(movement, Vector3.zero, ref currentVelocity, 1f / slowdownSpeed);
        }
        // Apply
        vCam.transform.position += movement;
    }
}
