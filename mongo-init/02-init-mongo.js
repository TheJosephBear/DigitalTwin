// This script runs automatically in the context of MONGO_INITDB_DATABASE
// No need to specify the database if working with the default one
// We're already in the database specified by MONGO_INITDB_DATABASE
// db = db.getSiblingDB('flaskapp'); // This line is not needed

// Create collections
db.createCollection('users');
db.createCollection('projects');

// Insert initial data if needed
db.users.insertMany([
  {
    username: "admin",
    email: "admin@example.com",
    role: "admin",
    created_at: new Date()
  },
  {
    username: "user",
    email: "user@example.com",
    role: "user",
    created_at: new Date()
  }
]);

db.projects.insertOne({
  name: "Sample Item",
  save_data: {data: "This is a sample project data."},
  updated_at: new Date()
});

// Create indexes
db.users.createIndex({ "username": 1 }, { unique: true });
db.projects.createIndex({ "name": 1 }, { unique: true });

print("========================================");
print("MongoDB initialization script executed at " + new Date());
print("Collections created: users, projects");
print("Users created: " + db.users.countDocuments() + ", Projects created: " + db.projects.countDocuments());
print("Initial data inserted successfully");
print("========================================");