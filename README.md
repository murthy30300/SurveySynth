# 📊 SurveySynth – Serverless Survey Analyzer for Education

**By:** Vishnu Murthy | B.Tech Final Year | KL University  
**Deployed Frontend:** [SurveySynth UI (S3)](https://surveysynth-ui.s3.amazonaws.com/)

---

## 🧠 Problem Statement

In large universities like mine (KL University), thousands of Computer Science students share the same set of core courses. Each course is managed by a **course coordinator** who gathers post-course feedback to improve the syllabus and delivery for future batches.

However, manually analyzing CSV-based survey responses (often hundreds or thousands of entries) is inefficient and subjective. There’s no automated system to extract **pain points**, **sentiment**, or **actionable suggestions** from open-text feedback.

---

## 🚀 Solution: SurveySynth

SurveySynth is a **fully serverless feedback analyzer** designed to help course coordinators extract key insights from survey results. Students upload CSVs, and within minutes get:

- ✨ Summary & Sentiment Analysis  
- 🔍 Top Pain Points & Suggestions  
- 📈 Visual Charts  
- 🧾 (Optional) PDF Report

---

## 🧱 Architecture Overview

### ✅ Built 100% using Serverless Technologies on AWS

```plaintext
1. Register/Login → API Gateway → Lambda
2. Upload CSV → S3 → uploadSurveyHandler → DynamoDB
3. Triggers Glue ETL Job → Cleans & Writes Silver CSV
4. Lambda updateStatusPostGlue updates metadata
5. summarizeFeedbackHandler uses Bedrock for insights
6. Results saved to SurveyInsights table
7. Stream triggers triggerVisualizationJob → Glue → PNG charts
8. Frontend polls for results → renders summary + visuals
```
---
### 🔗 Endpoints & Lambda Flows
| Flow Step              | Trigger/Service   | Lambda Function                                                    | Purpose                              |
| ---------------------- | ----------------- | ------------------------------------------------------------------ | ------------------------------------ |
| 🔐 Register/Login      | API Gateway       | `UserApiHandler`                                                   | Auth (Mock, stores in DynamoDB)      |
| 📤 Upload Survey       | API Gateway       | `uploadSurveyHandler`                                              | Upload to `S3`, update `SurveyMeta`  |
| 🧼 Preprocess CSV      | S3 → Glue Trigger | `SurveyPreprocessJob`                                              | Clean CSV → `silver/` folder         |
| 📊 Update ETL Status   | EventBridge       | `updateStatusPostGlue`                                             | Set status = preprocessed            |
| 🧠 Generate AI Summary | Lambda Stream     | `summarizeFeedbackHandler`                                         | Bedrock → `SurveyInsights`           |
| 📈 Generate Charts     | DynamoDB Stream   | `triggerVisualizationJob`                                          | Triggers `Visual_job` Glue Job       |
| 🖼️ Final PNG Charts   | Glue Job          | `Visual_job`                                                       | Generate & upload Seaborn/Matplotlib |
| 📡 Fetch Data for UI   | API Gateway       | `SurveyMetaHandler`, `SurveyInsightHandler`, `getChartUrlsHandler` | Feed UI                              |
---
### 💡 Highlights
Language Support: Works with free-text fields in English

Scalability: Serverless — scales with number of students/surveys

AI Integration: Amazon Bedrock → Claude Model for summarization

Visualization: Seaborn-based PNG charts (instead of QuickSight)

Deployment: Fully deployed via AWS SAM and S3
---
### 🧰 AWS Services Used

| Service            | Usage                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Lambda**         | Business logic: 8+ functions (auth, upload, summarize, chart gen)  |
| **API Gateway**    | Login, Register, Upload, Insights APIs                             |
| **DynamoDB**       | `Users`, `SurveyMeta`, `SurveyInsights` metadata                   |
| **S3**             | Stores raw/silver CSVs, PNG charts, optional PDF                   |
| **AWS Glue**       | 2 jobs: `SurveyPreprocessJob` (cleaning) and `Visual_job` (charts) |
| **Amazon Bedrock** | Summarization and sentiment analysis using `Claude` model          |
| **EventBridge**    | Detect Glue job completion                                         |
| **CloudWatch**     | Logging, debugging during development                              |
| **CloudFormation** | Serverless Application model                                       |
---
### 🖼️ Frontend Flow (React + S3 Hosted)

1. Register/Login → Save session in localStorage
2. Upload CSV file (base64) → /upload endpoint
3. Polls /survey-meta and /insights APIs
4. Displays:
   - Summary
   - Actionable Suggestions
   - PNG Charts (fetched from S3)
5. Optional Download PDF (next)
Frontend is deployed at:
👉 https://surveysynth-ui.s3.amazonaws.com/
---
### Example Output (from 10 feedback rows)
```
{
  "summary": "Users found the interface intuitive but faced performance issues.",
  "pain_points": ["App crashes", "Slow load times", "Login bugs"],
  "positive_feedback": ["Great design", "Useful search function"],
  "actionable_suggestions": [
    "Fix login crashes",
    "Improve app speed",
    "Add dark mode"
  ]
}
```
---
### Local Setup (if required)
1) Setup S3
2) create Dynamodb table
3) npm install     # React frontend
4) npm run dev     # Runs at http://localhost:5173
5) sam build && sam deploy --guided  # Deploy backend
---
### Future Enhancements
1) Generate downloadable PDF Reports
2) Embed charts inside PDF
3) Add email notification on upload completion
4) Switch to Amazon Cognito for full auth
5) Multi-language summarization
---
### About the Developer
Vishnu Nukala 
University ID: 2200030300
Final-year B.Tech | KL University
Used SurveySynth to solve a real problem at scale — improving courses for thousands of students based on feedback that matters.
