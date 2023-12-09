#![allow(unused)]

use anyhow::Result;
use serde_json::json;

#[tokio::test]
async fn quick_dev() -> Result<()> {
    let hc = httpc_test::new_client("http://localhost:8000")?;
    hc.do_get("/user/nicko").await?.print().await?;

    let req_create_msg = hc.do_post(
        "/api/messages",
        json!({
            "message": "This is a dummy message"
        }),
    );
    req_create_msg.await?.print().await?;
    
    hc.do_get("/api/messages").await?.print().await?;

    Ok(())
}
