# User Login

This diagram shows the authentication flow when a user logs in with their username and password. The system validates credentials, verifies the password hash, and generates a JWT access token upon successful authentication.

```puml
@startuml sequence_diagram_login
title User Login - Sequence Diagram

actor User
participant "AuthREST" as REST
participant "AuthService" as SVC
database "SQL Database" as DB


User -> REST: POST /api/auth/login\n{ username, password }

== Validate Payload ==
REST -> REST: Validate request payload

== Authenticate User ==
REST -> SVC: authenticate_user(username, password)

== User Lookup ==
SVC -> DB: SELECT id, username, email, password_hash, created_at\nFROM users\nWHERE username = :username
DB --> SVC: user record or None

alt user not found
  SVC --> REST: None
  REST --> User: 401 Unauthorized\n{ message: "Invalid username or password" }
else user found
  == Password Verification ==
  SVC -> SVC: check_password_hash(\n  user.password_hash,\n  password)
  
  alt password valid
    SVC --> REST: User object
    
    == Generate Token ==
    REST -> SVC: create_token(user.id)
    SVC --> REST: access_token
    REST --> User: 200 OK\n{ access_token }
  else password invalid
    SVC --> REST: None
    REST --> User: 401 Unauthorized\n{ message: "Invalid username or password" }
  end
end

@enduml
```
