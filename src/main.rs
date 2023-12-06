use axum::{
    body::Body,
    routing::{get, post},
    http::StatusCode,
    response::{IntoResponse, Response},
    Router, Json, extract::Query, 
};
use serde::{Serialize, Deserialize};

#[derive(Debug, Deserialize, Serialize)]
struct User {
    id: u64,
    name: String,
    email: String,
}

#[derive(Debug, Deserialize, Serialize)]
struct UserParams {
    username: Option<String>,
}

async fn create_user() -> impl IntoResponse {
    Response::builder()
        .status(StatusCode::CREATED)
        .body(Body::from("User created succesfully"))
        .unwrap()
}

async fn list_users() -> Json<Vec<User>> {
    let users = vec![
        User {
            id: 1,
            name: "Nicko".to_string(),
            email: "nicko@example.com".to_string(),
        },
        User {
            id: 2,
            name: "Arek".to_string(),
            email: "arek@example.com".to_string(),
        }, 
    ];
    Json(users)
}

async fn get_user(Query(params): Query<UserParams>) -> Json<User> {
    println!("->> {:<12} - get_user - {params:?}", "HANDLER");
    
    let username: &str = params.username.as_deref().unwrap_or("RandomUsername"); 
    let user: User = User {
        id: 1,
        name: username.to_string(),
        email: "{username}@email.com".to_string(),
    };
    Json(user)
}

#[tokio::main]
async fn main() {
    // Build app with single route
    let app = Router::new()
        .route("/", get(|| async { "Hello world!" }))
        .route("/create-user", post(create_user))
        .route("/users", get(list_users))
        .route("/user", get(get_user));

    println!("Running on http:://0.0.0.0:3000");

    // Run our app with hyper, listening globally on port 3000
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}



