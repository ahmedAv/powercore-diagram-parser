
# Python Project



## 🛠 Requirements
Make sure you have the following installed:
- Python 3.11 (recommended)
- pip (Python package manager)
- Virtual environment
- Docker & Docker Compose (for containerized deployment)
- OpenAI API Key

---

## 📦 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/ahmedAv/powercore-diagram-parser.git
cd your-project
```

###  2️⃣ Create and activate virtual environment
```bash
python -m venv venv
# On Linux/macOS
source venv/bin/activate
# On Windows
venv\Scripts\activate
```

###  3️⃣ Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

###  34️⃣ Setup environment variables
Create a `.env` file in the project root and add your OpenAI API key (and other required environment variables).  

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1
```

###  ▶️ Running the project
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Run with Docker Compose
```bash
docker-compose up
```

➡️ Open Swagger UI: http://localhost:8000/docs