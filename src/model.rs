use crate::{Error, Result};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};

#[derive(Clone, Debug, Serialize)]
pub struct Message {
    pub id: u64,
    pub message: String,
}

#[derive(Deserialize)]
pub struct MessageForCreate {
    pub message: String,
    //pub datetime: String,
}

#[derive(Clone)]
pub struct ModelController {
    messages_store: Arc<Mutex<Vec<Option<Message>>>>,
}

impl ModelController {
    pub async fn new() -> Result<Self> {
        Ok(Self {
            messages_store: Arc::default(),
        })
    }
}

// CRUD Implementation

impl ModelController {
    pub async fn create_message(&self, message_fc: MessageForCreate) -> Result<Message> {
        let mut store = self.messages_store.lock().unwrap();

        let id = store.len() as u64;
        let message = Message {
            id,
            message: message_fc.message,
        };
        store.push(Some(message.clone()));

        Ok(message)
    }

    pub async fn list_messages(&self) -> Result<Vec<Message>> {
        let store = self.messages_store.lock().unwrap();
        let messages = store.iter().filter_map(|m| m.clone()).collect();

        Ok(messages)
    }

    pub async fn delete_message(&self, id: u64) -> Result<Message> {
        let mut store = self.messages_store.lock().unwrap();
        let message = store.get_mut(id as usize).and_then(|m| m.take());

        message.ok_or(Error::MessageDeleteFailIdNotFound { id })
    }
}
