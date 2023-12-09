pub use self::error::{Error, Result};
use crate::model::ModelController;
use axum::{
    routing::get,
    Router, 
};
use tokio::net::TcpListener;
use axum::http::{
    header::{ACCEPT, AUTHORIZATION, CONTENT_TYPE},
    HeaderValue, Method,
};
use tower_http::cors::CorsLayer;


mod error;
mod web;
mod model;

#[tokio::main]
async fn main() -> Result<()>{

    let mc = ModelController::new().await?;
    

    // TODO:
    // - allow methods
    // - allow credentials
    // - allow headers
    let cors = CorsLayer::new()
        .allow_origin("http://localhost:3000".parse::<HeaderValue>().unwrap());

    let app = Router::new()
        .route("/", get(|| async { "Hello world!" }))
        .nest("/api", web::routes_messages::routes(mc.clone()))
        .layer(cors);

    // Run our app with hyper, listening globally on port 3000
    let listener = TcpListener::bind("0.0.0.0:8000").await.unwrap();
    println!("->> LISTENING on {:?}\n", listener.local_addr());
    axum::serve(listener, app.into_make_service()).await.unwrap();

    Ok(())
}



