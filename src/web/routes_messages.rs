use crate::{web, Error, Result};
use axum::routing::post;
use axum::{Json, Router};
use serde::Deserialize;
use serde_json::{json, Value};


#[derive(Debug, Deserialize)]
struct Message {
    message: String,
    datetime: String,
}

pub fn routes() -> Router {
    Router::new().route("/api/message", post(api_message))
}

async fn api_message() {}
