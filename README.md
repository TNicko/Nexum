# Nexum - Loughborough Knowledge Base AI Chat Assistant

Nexum is an AI-powered chat assistant designed to facilitate access to 
Loughborough's extensive knowledge base setup on Supabase. Leveraging 
advanced natural language processing technologies, Nexum provides immediate, 
accurate answers to inquiries related to Loughborough's academic resources, 
campus life, and more, enhancing the student and staff experience.

## Local Setup

### Prerequisites
- Docker and Docker Compose
- A `.env` file with necessary secrets for the server component

### Setting up environment
1. **Clone the repository**:
	```bash
   git clone https://github.com/TNicko/Nexum.git
   cd nexum 
   ```

3. **Environment configuration**
Nexum requires certain environment variables for its server component:
	- `SUPABASE_URL`: The project's Supabase project URL.
	- `SUPABASE_KEY`: The project's Supabase service role key.
	- `OPENAI_API_KEY`: Your OpenAI API key.

	Create a `.env` file in the `server` directory and fill in your credentials:
	```
	SUPABASE_URL=<supabase_url>
	OPENAI_API_KEY=<your_openai_api_key>
	SUPABASE_KEY=<supabase_key>
	```

3. **Build and Run with Docker Compose**:
	```bash
	docker-compose up --build
	```
	This builds the Docker images and starts the containers. The `--build` flag
	ensures Docker rebuilds the images if there are any changes.

4. **Stopping the Application**
To stop Nexum and remove the containers, if running in the foreground, 
press `Ctrl+C` in terminal. Alternatively, run the following command in 
within the project directory:
	```bash
	docker-compose down
	```
