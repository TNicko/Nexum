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

use dotenv::dotenv;
use std::env;


#[tokio::main]
async fn main() -> Result<()>{
    dotenv().ok();

    let mc = ModelController::new().await?;
    
    let cors = CorsLayer::new()
        .allow_origin("http://localhost:5173".parse::<HeaderValue>().unwrap())
        .allow_methods([Method::GET, Method::POST])
        .allow_headers([CONTENT_TYPE]);

    let app = Router::new()
        .route("/", get(|| async { "Hello world!" }))
        .nest("/api", web::routes_messages::routes(mc.clone()))
        .layer(cors);

    // Run our app with hyper, listening globally on port 8000
    let listener = TcpListener::bind("0.0.0.0:8000").await.unwrap();
    println!("->> LISTENING on {:?}\n", listener.local_addr());
    axum::serve(listener, app.into_make_service()).await.unwrap();

    Ok(())
}



