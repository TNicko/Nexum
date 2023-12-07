pub use self::error::{Error, Result};
use crate::model::ModelController;
use axum::{
    routing::get,
    Router, 
};
use tokio::net::TcpListener;


mod error;
mod web;
mod model;

#[tokio::main]
async fn main() -> Result<()>{

    let mc = ModelController::new().await?;

    let app = Router::new()
        .route("/", get(|| async { "Hello world!" }))
        .nest("/api", web::routes_messages::routes(mc.clone()));

    // Run our app with hyper, listening globally on port 3000
    let listener = TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("->> LISTENING on {:?}\n", listener.local_addr());
    axum::serve(listener, app.into_make_service()).await.unwrap();

    Ok(())
}



