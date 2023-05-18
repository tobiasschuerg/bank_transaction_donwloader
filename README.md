# Bank Transaction Downloader

The Bank Transaction Downloader is a Python-based utility that fetches bank account transactions and stores them in a
local MySQL database. It also comes with a simple web UI for transaction management and a CSV export functionality.

## Overview

The Bank Transaction Downloader project consists of three main components:

- `main.py`: Handles the downloading of transactions.
- `app.py`: A Flask application for viewing and managing transactions via a web interface.
- `export.py`: Provides the functionality to export transactions as CSV files.

## Getting Started

Follow the steps below to quickly get the system up and running:

1. Sign up for a free API key from [Nordigen](https://nordigen.com).
2. Run the command `python main.py` and follow the prompts on the console.
3. Follow the console prompts
4. Run `python app.py` to start the web application for viewing and managing transactions.

## Features

The Bank Transaction Downloader offers the following capabilities:

- Download transactions using the bank's API endpoint.
- Save transactions in a local MySQL database.
- Categorize transactions for easy tracking and management.
- Train a local classifier to suggest transaction categories.
- Export transactions as a CSV file for data analysis and backup.
- Manage multiple bank accounts simultaneously.
- Customize settings and configurations via yaml files.

## Notice
The Bank Transaction Downloader is a tool for personal use and is provided as-is 
without any warranties or guarantees of any kind. The user is solely responsible for the data they access 
and how they use it. 
Please also remember to be careful with your personal data. 
Keep your Nordigen API key confidential, and do not share it with others.
