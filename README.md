ADK Multi-Agent Blogger

A multi-agent blog generation system built with Google Agent Development Kit (ADK). The application uses specialized agents to plan, write, and validate technical blog posts through a coordinated workflow.

Features

Multi-agent architecture with Google ADK

Automatic blog outline generation

Technical blog writing in Markdown

Outline and article validation

Automatic retries using LoopAgent


Install dependencies:

pip install -r requirements.txt

Environment Variables

Create a .env file:

MODEL="gemini-flash-lite-latest"
GOOGLE_API_KEY=YOUR_API_KEY

Running the Project

Start the ADK application:

adk web

Then interact with the Blogger agent by providing a blog topic.
