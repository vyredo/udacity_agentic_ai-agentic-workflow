# AI-Powered Agentic Workflow for Project Management

**Author**: Vidy Alfredo
**Course**: Udacity Agentic AI Nanodegree

An intelligent email routing system built with Python, featuring AI agents that automatically process and route emails based on content analysis. This project demonstrates workflow automation, type-safe Python development, and practical agentic AI implementation.

## Project Overview

This repository contains two main components:

- **Phase 1**: Basic routing agent implementation
- **Phase 2**: Advanced agentic workflow with multi-step execution

The system uses AI agents to intelligently process emails, analyze content, and route messages to appropriate handlers based on predefined workflows and product specifications.

## Prerequisites

- Python 3.8 or higher
- OpenAI API access

## Getting Started

### 1. Environment Setup

Create a `.env` file in the project root directory with your OpenAI API key:

```bash
# Create .env file
touch .env
```

Add the following content to your `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

⚠️ **Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key. Never commit your `.env` file to version control.

### 2. Install Dependencies

If working locally, install the required dependencies:

```bash
pip install -r requirements.txt
```

**Note**: If you're using the Udacity classroom workspace, all required libraries are pre-configured.

### 3. Run the Project

Execute the following commands to run different phases of the project:

#### Phase 1 - Basic Routing Agent

```bash
python starter/phase_1/routing_agent.py
```

#### Phase 2 - Advanced Agentic Workflow

```bash
python starter/phase_2/agentic_workflow.py
```

## Project Structure

```
├── starter/
│   ├── phase_1/
│   │   └── routing_agent.py          # Basic email routing implementation
│   ├── phase_2/
│   │   ├── agentic_workflow.py       # Advanced workflow execution
│   │   └── Product-Spec-Email-Router.txt  # Product specifications
├── requirements.txt                   # Python dependencies
├── .env                              # Environment variables (create this)
└── README.md                         # This file
```

## Features

- **Intelligent Email Processing**: AI-powered content analysis and routing
- **Multi-step Workflows**: Automated execution with error handling
- **Type Safety**: Comprehensive Python type annotations
- **Robust Error Handling**: Graceful failure management
- **Cross-platform Compatibility**: Uses `pathlib` for reliable file operations

## Dependencies

A `requirements.txt` file has been provided in this repo if you want to work on the project locally. Otherwise, the workspace provided in the Udacity classroom has been configured with all the required libraries.

## Troubleshooting

- **File not found errors**: Ensure you're running commands from the project root directory
- **API errors**: Verify your OpenAI API key is correctly set in the `.env` file
- **Import errors**: Make sure all dependencies are installed via `pip install -r requirements.txt`
