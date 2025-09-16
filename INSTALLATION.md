# INSTALLATION GUIDE for Project - C.A.R.E.
This guide explains how to set up and run **Project-CARE** on your local machine using Docker containers for the FHIR database and servers built with Python and Node.js.

  ---  
## ✅ Prerequisites
Before proceeding, make sure you have the following installed on your system:  
### 1. **Docker**  Docker is required to run the HAPI FHIR server container.  
- **Install on Ubuntu/Debian:**    
```bash    
sudo apt update    
sudo apt install -y docker.io    
sudo systemctl start docker    
sudo systemctl enable docker   `

docker --version
```

### 2. **Python (>=3.8 recommended)**

Python is required to run the backend server.
```bash
sudo apt update
sudo apt install -y python3 python3-pip
python3 --version
pip3 --version
```

### 3\. **Node.js (>=16 recommended)**

Node.js is required to run the frontend/server in the care-secure-app directory.
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
\. "$HOME/.nvm/nvm.sh"
nvm install 22

*   curl -fsSL https://deb.nodesource.com/setup\_16.x | sudo -E bash -sudo apt updatesudo apt install -y nodejs
    
*   node --versionnpm --version
```

### 4\. **Git (optional, if cloning the repository)**

```bash
*   sudo apt updatesudo apt install -y git
```

📦 Setup Instructions
---------------------

### Step 1 – Clone the Repository (if not already done)

```bash
git clone https://github.com/snbhowmik/Project-CARE.git
```

### Step 2 – Run HAPI FHIR Server using Docker

We used se the official hapiproject/hapi:latest Docker image to run the FHIR server.
```bash
docker pull hapiproject/hapi:latest  
docker run -d --name hapi-fhir -p 8080:8080 hapiproject/hapi:latest   `
```
*   The FHIR server will now be accessible at:http://localhost:8080
```bash
docker ps
    
docker logs hapi-fhir
```
CTRL+C to stop the logs

### Step 3 – Install Python Dependencies

Navigate to the project’s root directory and install required Python packages.
```bash
cd /path/to/project-care  
pip3 install -r requirements.txt   `
```
> Make sure you are using python3 and pip3 depending on your system’s configuration.

### Step 4 – Run the Python Server

Start the Python backend server:
```bash
python3 app.py   `
```
> The server will run in the terminal and connect to the FHIR server at http://localhost:8080.

### Step 5 – Install Node.js Dependencies

Navigate to the care-secure-app directory and install dependencies.
```bash
cd care-secure-app  
npm install   `
```
### Step 6 – Run the Node.js Server

Start the Node.js application:
```bash
npm run dev
```
> The frontend will now be available at http://localhost:5173 