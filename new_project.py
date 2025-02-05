'''This project is designed to automate and simplify online research
by integrating real-time news retrieval and AI-powered summarization. 
It allows users to quickly gather, summarize, and store relevant 
information on any topic'''

import os
import asyncio
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# API Keys (Replace these with your actual keys)
NEWSDATA_API_KEY = "p808"
GEMINI_API_KEY = "A"


# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)


# Initialize Flask app
app = Flask(__name__)
CORS(app)




# Base Agent Class
class Agent:
    def __init__(self, name):
        self.name = name

    def perceive(self, input_data):
        raise NotImplementedError("Perceive method must be implemented.")

    def act(self):
        raise NotImplementedError("Act method must be implemented.")




# Input Agent
class InputAgent(Agent):
    def perceive(self, input_data):
        self.topic = input_data

    def act(self):
        return self.topic



# Retrieval Agent (Uses NewsData.io API)
class RetrievalAgent(Agent):
    def perceive(self, topic):
        self.topic = topic

    async def fetch_news(self):
        """Fetch relevant articles from NewsData.io API."""
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q={self.topic}&language=en"

        try:
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                news_data = response.json()
                articles = news_data.get("results", [])

                if not articles:
                    return "No relevant news articles found."

                # Extract top 3 articles
                news_summaries = []
                for article in articles[:5]:  # Limit to 3 articles
                    title = article.get("title", "No title available")
                    source = article.get("source_id", "Unknown source")
                    link = article.get("link", "#")
                    news_summaries.append(f"- {title} (Source: {source}) [Read more]({link})")

                return "\n".join(news_summaries)

            return "Error retrieving news articles."
        
        except Exception as e:
            print(f"Error fetching data from NewsData.io: {e}")
            return "Error retrieving news information."

    async def act(self):
        return await self.fetch_news()




# Summarization Agent (Uses Gemini AI)
class SummarizationAgent(Agent):
    def perceive(self, content):
        self.content = content

    async def summarize_content(self):
        """Summarize content using Gemini AI."""
        if not self.content or self.content == "No relevant news articles found.":
            return "No relevant information available for summarization."

        prompt = f"Summarize the following information and for each article give me details summary of each article in good fromat following the name of article. the format should be 1.Article Name and source, summary:\n\n{self.content}"
        model = genai.GenerativeModel("gemini-pro")

        try:
            response = model.generate_content(prompt)
            return response.text if response.text else "No summary available."
        except Exception as e:
            print(f"Error summarizing content: {e}")
            return "Error in summarization."

    async def act(self):
        return await self.summarize_content()



# File Storage Agent

class FileStorageAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.is_saved = False  # Flag to check if the file is already saved

    def perceive(self, summary):
        self.summary = summary

    def act(self):
        """Store summary in a local file at a specific path."""
        if self.is_saved:  # Check if the file is already saved
            return ""

        try:
            # Define the absolute path to save the summary file
            folder_path = r"D:\project\Project_2\research-bot\summary"
            
            # Check if the folder exists, create it if it doesn't
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            # Define the full path to save the summary
            file_path = os.path.join(folder_path, 'research_summary.txt')
            
            # Save the summary to the specified file path
            with open(file_path, 'w') as file:
                file.write(self.summary + "\n\n")
            
            # Mark the file as saved
            self.is_saved = True
            
            print(f"File saved at {file_path}")  # Debugging: Print the path where the file is saved
            return "Summary saved successfully."
        except Exception as e:
            print(f"Error saving summary: {e}")
            return "Error saving summary."


# Workflow Management
class Workflow:
    def __init__(self, agents):
        self.agents = agents

    async def run(self, input_data):
        current_data = input_data
        for agent in self.agents:
            agent.perceive(current_data)
            if isinstance(agent, (RetrievalAgent, SummarizationAgent)):
                current_data = await agent.act()
            else:
                current_data = agent.act()
        return current_data  # Returning final processed data (summary)




# Flask Route
@app.route('/run_workflow', methods=['POST'])
def run_workflow():
    data = request.json
    topic = data.get("topic")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    # Define agents
    input_agent = InputAgent("InputAgent")
    retrieval_agent = RetrievalAgent("RetrievalAgent")
    summarization_agent = SummarizationAgent("SummarizationAgent")
    file_storage_agent = FileStorageAgent("FileStorageAgent")

    agents = [input_agent, retrieval_agent, summarization_agent, file_storage_agent]
    research_workflow = Workflow(agents)

    # Run asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Get the final summary message
    final_summary = loop.run_until_complete(research_workflow.run(topic))

    # Display all messages in the response
    return jsonify({
        "message": "Workflow completed.",
        "summary": final_summary,
        "file_status": file_storage_agent.act()  # This will give the status of file saving
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
