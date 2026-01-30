// Creates application user (separate from the root user)
db.createUser({
  user: "appuser",
  pwd: "apppassword",
  roles: [
    { role: "readWrite", db: "VRTherapy" }
  ]
});

print("Application user created");