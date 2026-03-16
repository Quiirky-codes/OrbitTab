# OrbiTab

OrbiTab is an AI-powered Chrome extension that intelligently organizes large numbers of browser tabs. It automatically groups related tabs, generates summaries, and stores research sessions for later retrieval. The system runs entirely on the user's machine using a local language model, ensuring that browsing data remains private and never leaves the device.

OrbiTab is built as a full-stack local AI system combining a Chrome extension frontend, a Python-based native messaging backend, and a lightweight SQLite database for persistent session storage.

## Table of Contents

1. Overview
2. Key Features
3. Architecture
4. Technology Stack
5. System Design
6. Installation Guide
7. Running the Project
8. Project Structure
9. Database Schema
10. Native Messaging Integration
11. AI Processing Pipeline
12. Privacy and Security
13. Performance Considerations
14. Future Improvements

## Overview

Modern browsing sessions often involve dozens of open tabs during research, development, or interview preparation. Managing these tabs manually quickly becomes difficult.

OrbiTab addresses this problem by using a local AI model to:

  * Analyze open browser tabs
  * Group related tabs automatically
  * Generate summaries for each tab
  * Store organized browsing sessions
  * Enable search across previously visited tabs

All AI inference runs locally using Ollama, ensuring that no browsing data is transmitted to external services.

## Key Features

### Automatic Tab Organization

OrbiTab analyzes the titles and domains of open tabs and automatically groups related tabs into logical clusters.

Example:

  * Group: Amazon Interview Preparation

  * Amazon Leadership Principles

  * Behavioral Interview Questions

  * STAR Method Examples

### AI-Generated Summaries

Each tab is summarized using a local language model to help users quickly understand the content without revisiting every page.

### Session Storage

Organized tab groups are stored in a local SQLite database so that users can revisit past research sessions later.

### Search Across Past Tabs

Users can search for previously opened tabs by keyword, allowing them to quickly rediscover useful resources.

### Pinned Tabs

Users can mark tabs as important to prevent them from being reorganized or closed.

### Session Export

Sessions can be exported as:

  * Markdown

  * Plain text

This makes it easy to document research notes.

### Keyboard Shortcuts

A keyboard shortcut allows users to organize all open tabs instantly.

### Privacy-First Design

All processing happens locally:

  * No external APIs

  * No telemetry

  * No cloud storage

  * No browsing data leaves the machine

## Architecture

OrbiTab is composed of three main components.

#### Chrome Extension Frontend
Handles the user interface and tab interaction.

#### Python Native Host Backend
Processes AI tasks and manages persistent storage.

#### Local AI Model
Runs tab summarization and grouping locally through Ollama.

#### System flow:

##### Chrome Extension
→ Native Messaging
→ Python Backend
→ Local LLM (Ollama)
→ SQLite Database

## Technology Stack

### Frontend

  * React

  * Vite

  * Chrome Extension Manifest V3

  * Tailwind CSS

### Backend

  * Python 3

  * SQLite

  * Sentence Transformers

  * Ollama

### AI

  * Phi-3 or Gemma models via Ollama

  * Embedding models for semantic similarity

### Infrastructure

  * Chrome Native Messaging

  * Local SQLite database

  * Virtual environment (venv)

## System Design

The system is designed to keep all heavy processing outside the browser.

1. The Chrome extension collects metadata about open tabs.

2. Tab data is sent to the Python backend using native messaging.

3. The backend processes tab data using AI models.

4. Organized groups and summaries are returned to the extension.

5. Sessions are stored in SQLite for future retrieval.

This design keeps the extension lightweight while allowing powerful AI processing.

## Installation Guide

### 1. Clone the Repository

```

git clone https://github.com/Quiirky-codes/OrbitTab.git
cd orbitab

```

### 2. Install Python Dependencies

#### Create a virtual environment.

```

python3 -m venv venv
source venv/bin/activate

```

#### Install required packages.

```

pip install -r requirements.txt

```

### 3. Install Ollama

#### Download Ollama from:

[https://ollama.ai](https://ollama.ai)

#### Pull a model.

` ollama pull phi3 `

or

` ollama pull gemma:2b `

### 4. Build the Chrome Extension

#### Navigate to the extension directory.
```

cd chrome-extension
npm install
npm run build

```

### 5. Register Native Messaging Host

#### Create the native messaging manifest.

Location on macOS:

` ~/Library/Application Support/Google/Chrome/NativeMessagingHosts/ `

File:

` ai.tab.manager.json `

> Example:
```

{
  "name": "ai.tab.manager",
  "description": "OrbiTab Native Host",
  "path": "/FULL/PATH/native-host/host.py",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://EXTENSION_ID/"
  ]
}

```
### 6. Load Extension in Chrome

#### Open:

` chrome://extensions `

#### Enable Developer Mode.

**Click:**

  * **Load Unpacked**

Select:

` chrome-extension/dist `

## Running the Project

### Start Ollama

` ollama serve `

> Ensure Python virtual environment is active.

` source venv/bin/activate `

**Reload the extension in Chrome.**

Click the extension icon and select **"Organize Tabs"**.

## Project Structure
```

orbitab
│
├── chrome-extension
│   ├── src
│   ├── public
│   ├── manifest.json
│   └── vite.config.js
│
├── native-host
│   ├── host.py
│   ├── agent.py
│   ├── db.py
│   ├── migrations.py
│   ├── database.db
│   └── native_host.log
│
├── requirements.txt
└── README.md

```

## Database Schema

The SQLite database stores organized browsing sessions.

### Sessions Table

Stores each saved browsing session.

Fields:

  * id

  * created timestamp

  * session title

  * Groups Table

### Stores AI-generated tab groups.

Fields:

  * id

  * session_id

  * group name

  * group summary
  
  * Tabs Table

### Stores individual tabs.

Fields:

  * id
  * group_id
  * tab title
  * domain
  * summary
  * pinned flag

## Native Messaging Integration

Chrome extensions cannot run Python directly.
OrbiTab uses Chrome Native Messaging to connect the extension to a Python process.

Communication format:

Length-prefixed JSON messages over standard input and output.

> Example message:

```

{
  "action": "organize_tabs",
  "tabs": [...]
}

```

The Python host processes the request and returns structured tab groups.

## AI Processing Pipeline

#### The backend performs several steps.

  * Tab Metadata Extraction

#### Titles and domains are extracted from open tabs.

  * Semantic Embedding

#### Tab titles are converted into embeddings using a lightweight model.

  * Clustering

#### Tabs are grouped based on semantic similarity.

  * LLM Summarization

#### A local language model generates concise summaries.

  * Session Storage

Results are saved in SQLite for later retrieval.

## Privacy and Security

OrbiTab is designed to protect user data.

  * All AI processing runs locally
  
  * No browsing data is sent to external servers

  * SQLite database is stored locally
  
  * Native messaging restricts allowed extension origins

  * No telemetry or tracking

File permissions can be restricted using:

` chmod 600 database.db `

## Performance Considerations

Running local AI models can be resource-intensive.

To optimize performance:

  * Use lightweight models such as Phi-3 Mini or Gemma 2B

  * Limit summarization context length

  * Batch tab summarization requests

  * Avoid processing pinned tabs

These optimizations allow OrbiTab to run efficiently even on laptops with limited memory.

## Future Improvements

Planned improvements include:

  * Full-text search using SQLite FTS5

  * Semantic search using embeddings

  * Background tab analysis

  * Visual tab relationship graphs

  * Cross-device encrypted session sync

  * Productivity analytics dashboard

## License

MIT License

Copyright (c) 2026 Amith M Jain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
