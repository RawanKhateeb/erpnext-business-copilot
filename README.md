# 🚀 ERPNext Business Copilot – Automation Project

An AI-powered backend system integrated with ERPNext, developed as a final project for the QA Automation course.

The system enables users to interact with ERP data using natural language, receive intelligent insights, and validate system quality using full automation pipelines.

---

## 📌 Project Overview

ERPNext Business Copilot is a smart analytics and automation platform that connects to ERPNext and provides:

- Natural language query processing
- AI-based intent detection
- Automatic ERP data retrieval
- Business insights and recommendations
- Automated API, integration, and UI testing
- Continuous Integration and Delivery (CI/CD)

The project focuses on quality assurance, automation best practices, and real system integration.
---

## 🎯 Project Goals

- Design a scalable FastAPI backend
- Integrate real ERPNext services
- Apply AI for business analysis
- Implement full automation testing
- Achieve high code coverage (90%+)
- Build a complete CI/CD pipeline
- Follow industry QA standards

---

## 🛠️ Technologies & Tools

- Python 3.11
- FastAPI
- ERPNext REST API
- OpenAI API
- Pytest / Unittest
- Playwright
- GitHub Actions
- Allure Reports
- Coverage.py

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

git clone <repository-url>  
cd erpnext-business-copilot  

### 2️⃣ Create Virtual Environment

python -m venv .venv  

Linux / Mac:  
source .venv/bin/activate  

Windows:  
.venv\Scripts\activate  

### 3️⃣ Install Dependencies

pip install -r requirements.txt  

---

## 🔐 Environment Configuration

Create `.env` file in project root:

ERP_URL=your_erpnext_url  
ERP_API_KEY=your_api_key  
OPENAI_API_KEY=your_openai_key  

---

## ▶️ Run Application

uvicorn app.main:app --reload  

Server URL:  
http://localhost:8000  


## 🧪 Testing Strategy

### Unit & API Tests

pytest backend/tests/api_mock  

### Integration Tests (Local Only)

pytest backend/tests/integration  

### UI Automation Tests

npx playwright test  

---

## 📊 Coverage Report

coverage run -m pytest  
coverage report  

Target Coverage: 90%+  

---

## 📈 Allure Reports

allure serve allure-results  

---

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for:

- Automated test execution
- Code quality validation
- Coverage monitoring
- Allure report publishing
- Build verification

The pipeline runs automatically on push and pull requests.

---

## 📚 Learning Outcomes

During this project, the following skills were developed:

- Backend architecture design
- Automation testing strategy
- API and UI test implementation
- CI/CD configuration
- AI service integration
- ERP system integration
- Quality metrics analysis



