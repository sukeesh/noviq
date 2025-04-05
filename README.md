# Noviq - Free Deep Research on Local

## Overview

Noviq is a local research assistant that helps you conduct deep research on any topic. It uses local LLMs through Ollama to process your queries, ask clarifying questions, and generate comprehensive research reports based on web searches.

## Features

- User-friendly interface similar to Grok/ChatGPT
- Uses local LLMs through Ollama for privacy and control
- Asks clarifying questions to better understand your research needs
- Creates a detailed research plan
- Searches the web for relevant information
- Scrapes and processes webpage content
- Generates comprehensive HTML research reports with citations

## Installation

### Prerequisites

- Python 3.11+
- Node.js and npm
- [Ollama](https://ollama.ai/) installed and running with at least one model

### Setup

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```
3. Install Python dependencies:
   ```
   pip install -e .
   ```
4. Install UI dependencies:
   ```
   cd ui
   npm install
   cd ..
   ```

## Usage

1. Make sure Ollama is running: `ollama serve`
2. Start the Noviq application:
   ```
   python run_noviq.py
   ```
3. The application will open in your browser at http://localhost:3000

## How it Works

1. **Research Intent**: Enter your research topic or question
2. **Clarifying Questions**: The system asks questions to better understand your needs
3. **Research Plan**: Based on your answers, a research plan is generated
4. **Web Search**: The system searches the web for relevant information
5. **Content Analysis**: Webpage content is scraped and processed
6. **Report Generation**: A comprehensive research report is created with citations
7. **Review**: You can view the report in your browser

## UI Components

The UI is built with React and resembles modern AI chat interfaces:

- **Top Header**: Shows navigation and app info
- **Chat Interface**: Main interaction area for questions and answers
- **Research Progress**: Shows the research plan and progress
- **Search Results**: Displays search results as they're processed
- **Input Area**: Enter your research queries

## Architecture

Noviq consists of three main components:

1. **Backend**: FastAPI server that handles the research process
2. **UI**: React frontend that provides the user interface
3. **Main Library**: Core research functionality using DSPy and Ollama

## High level implementation steps

1. User gives intent of the deep research.
2. Hit LLM and generate few questions to clarify more.
    a. Use this https://arxiv.org/pdf/2406.12639
    b. Refer this: https://github.com/magicgh/Ask-before-Plan
3. User answers the clarifying questions.
4. Plan the steps to do deep research.
    a. What to search on the internet? Keywords to search.
    b. How to classify something as useful content?
5. Use Google / Free web search / Serper / Yahoo / Duck Duck Go for web search.
6. Collect all the information (Links to be researched)
7. Research individual links, gather all the relevant information from the link, summarize and store it SOMEWHERE(Graph DB, Vector DB?)
8. Provide and detailed final response gathering all the information so far.
    a. How to collate everything nicely (Big problem alone to be solved)

## Performance Considerations

Minimum specifications required for better performance. Optimize and slow down if the laptop doesn't support. Adjust research according to the laptop - local specifications.

1. Macbook Silicon - Speed, Memory, CPU.

## Future scope: Online scaling

1. Put all of these in Kubernetes cluster.
2. Run all of these as parallel jobs to scrape and extract content from the Internet.
