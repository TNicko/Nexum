use crate::model::{ModelController, Message, MessageForCreate};
use axum::extract::{State, Path};
use axum::routing::{post, delete};
use axum::{body, Json, Router};
use serde_json::json;
use serde_json::Value;
use crate::error::Result as customResult;
use llm_chain::chains::map_reduce::Chain;
use llm_chain::step::Step;
use llm_chain::{executor, parameters, prompt, Parameters};


pub fn routes(mc: ModelController) -> Router {
    Router::new()
        .route("/doGreeting", post(present_greeting))
        .with_state(mc)
}

async fn present_greeting(
    State(mc): State<ModelController>,
    Json(message_fc): Json<MessageForCreate>,
) -> customResult<Json<Value>> {
    println!("->> {:<12} - query", "HANDLER");
    println!("{}", message_fc.message);
    let generated_greeting = greet_generate(message_fc.message);
    let body = Json(json!({
        "id" : 133,
        //"messagep1" : generated_greeting,

    }));
    Ok(body)
}

async fn greet_generate(
    name : String
) -> Result<String, Box<dyn std::error::Error>> {
    // Create a new ChatGPT executor
    let exec = executor!()?;
    // Create our step containing our prompt template
    let step = Step::for_prompt_template(prompt!(
        "You are a bot for making personalized greetings",
        "Make a personalized greeting tweet for {{text}}" // Text is the default parameter name, but you can use whatever you want
    ));

    // A greeting for emil!
    let res = step.run(&parameters!(name), &exec).await?;
    println!("{}", res);

    println!("{}", res.to_immediate().await?.as_content());

    let my_result = String::from("I like dogs");

    Ok(my_result)
}
