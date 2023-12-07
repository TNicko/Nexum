pub use self::error::{Error, Result};
use crate::model::ModelController;
use axum::{
    body::Body,
    routing::{get, post},
    http::StatusCode,
    response::{IntoResponse, Response},
    Router, Json, extract::{Query, Path}, 
};
use tokio::net::TcpListener;
use serde::{Serialize, Deserialize};

mod error;
mod web;
mod model;

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

// e.g. `/user?username=TNicko`
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

// e.g. `/user/nicko`
async fn get_user2(Path(name): Path<String>) -> Json<User> {
    println!("->> {:<12} - get_user2 - {name:?}", "HANDLER");
    
    let user: User = User {
        id: 2,
        name,
        email: "{username}@email.com".to_string(),
    };
    Json(user)

}

fn routes_users() -> Router {
    Router::new()
        .route("/create-user", post(create_user))
        .route("/users", get(list_users))
        .route("/user", get(get_user))
        .route("/user/:name", get(get_user2))
}

#[tokio::main]
async fn main() -> Result<()>{

    let mc = ModelController::new().await?;

    let app = Router::new()
        .route("/", get(|| async { "Hello world!" }))
        .nest("/api", web::routes_messages::routes(mc.clone()))
        .merge(routes_users());

    // Run our app with hyper, listening globally on port 3000
    let listener = TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("->> LISTENING on {:?}\n", listener.local_addr());
    axum::serve(listener, app.into_make_service()).await.unwrap();

    Ok(())
}



