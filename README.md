# Peer Chat Application

The Peer Chat Application is a simple command-line chat application that enables users to communicate through one-to-one chats and chat rooms. The application comprises a server component (`server.py`) and a client component (`peer.py`). Additionally, there's a stress testing script (`stress_testing.py`) for assessing the application's performance under load.

## Table of Contents
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)

## Features

- User authentication (Login and Create Account)
- One-to-one chat functionality
- Chat room creation, listing, and joining
- Handling Hello messages for user liveness
- Multi-threaded server to handle multiple client connections
- Stress testing script to assess application performance

## Getting Started

### Prerequisites

Before you begin, ensure you have the following prerequisites:

- Python 3.x installed.
- MongoDB installed.
- Required dependencies installed:

  ```
  pip install netifaces psutil pyargon2 pymongo pytest tabulate

### Installation
 first clone the code:
 
 ```
  git clone https://github.com/your-username/your-repo.git
  cd your-repo
```

Start the server:

 ```
  python server/server.py
```

Start the peer:

```
  python client/peer.py
```


 

