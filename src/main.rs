use axum::{
    routing::get,
    Router,
};

#[tokio::main]
async fn main() {

    // Build app with single route
    let app = Router::new().route("/", get(|| async {"Hello, world!"}));

    // Run our app with hyper, listening globally on port 3000
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
