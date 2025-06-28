
# ✅ SurveySynth – Full Checklist & Execution Plan (with Glue Integration)

This document outlines everything you need to do to complete your project in structured phases, including raw survey ingestion, AWS Glue preprocessing, insights via Bedrock, and visualizations.

---

## 🧩 Phase 1: User Upload + Metadata

### 🎯 Objective:
Let a logged-in user upload a survey file → save it to S3 → store metadata in DynamoDB → trigger Glue job

### 📝 Checklist:

- [ ] ✅ Create Users table in DynamoDB
  - Fields: email, created_at, password, upload_count, user_id
- [ ] ✅ Create SurveyMeta table in DynamoDB
  - Fields: user_id, upload_id, s3_path_raw, status, timestamp
- [ ] ✅ Create S3 bucket surveysynth-uploads
  - Folders: raw_data_csv/, silver/, refined_data/, reports/
- [ ] ✅ Implement uploadSurveyHandler Lambda
  - Accepts file upload (base64), user email
  - Saves to raw_data_csv/{user_id}_c{upload_count}.csv
  - Updates upload_count in Users table
  - Stores metadata in SurveyMeta table (status = raw)
- [ ] ✅ Add IAM permissions to Lambda to invoke Glue
- [ ] ✅ Trigger a named Glue job (e.g. SurveyPreprocessJob) after upload
  - Pass arguments: user_id, upload_id, s3_input_path, s3_output_path

---

## 🧩 Phase 2: Preprocessing in AWS Glue

### 🎯 Objective:
Clean & normalize uploaded CSV → extract structured data → write to S3 silver layer

### 📝 Checklist:

- [ ] ✅ Create Glue Job in Glue Studio (name: SurveyPreprocessJob)
- [ ] ✅ Set job type: Python Shell or Spark (depending on data size)
- [ ] ✅ Add script to:
  - Read from raw_data_csv/
  - Clean missing rows/columns
  - Normalize column names (strip spaces, lower case)
  - Identify MCQ, rating, and free-text fields
  - Generate summary-level structured file
- [ ] ✅ Output to silver/{user_id}/{upload_id}.csv in S3
- [ ] ✅ Register output location in Glue Data Catalog (optional, for QuickSight)
- [ ] ✅ Add IAM role with Glue + S3 access
- [ ] ✅ (Optional) Add job bookmark to avoid reprocessing same files

---

## 🧩 Phase 3: Update Metadata Post-Glue

### 🎯 Objective:
Track ETL status and results

### 📝 Checklist:

- [ ] ✅ Add trigger or polling Lambda (updateStatusPostGlue)
  - Monitor Glue job completion (e.g., via EventBridge or Step Function)
- [ ] ✅ When job is done, update SurveyMeta:
  - status = preprocessed
  - Add s3_path_silver

---

## 🧩 Phase 4: AI Analysis via Bedrock

### 🎯 Objective:
Analyze open-text fields and generate actionable insights

### 📝 Checklist:

- [ ] ✅ Create Lambda summarizeFeedbackHandler
  - Triggered after Glue status is preprocessed
  - Read from silver/{user_id}/{upload_id}.csv
  - Extract feedback columns (liked_most, improvement_suggestions, etc.)
  - Chunk 10–20 responses
  - Send prompt to Amazon Bedrock (Claude or Titan)
- [ ] ✅ Receive summary:
  - Overall sentiment
  - Pain points
  - Top 3 actionable insights
- [ ] ✅ Store results back in SurveyMeta or new table SurveyInsights

---

## 🧩 Phase 5: Visualization in AWS QuickSight

### 🎯 Objective:
Generate pictorial insights from structured survey data

### 📝 Checklist:

- [ ] ✅ Register silver/ data in AWS Glue Data Catalog
- [ ] ✅ Connect QuickSight to catalog via Athena
- [ ] ✅ Create visualizations:
  - Bar chart: average module ratings
  - Pie chart: job readiness distribution
  - Line chart: future comparison across batches
  - Word cloud (optional): common suggestions
- [ ] ✅ Build dashboard per user_id or upload_id
- [ ] ✅ (Optional) Embed in frontend using QuickSight embedding or iframe

---

## 🧩 Phase 6: Report Generation (PDF)

### 🎯 Objective:
Generate and store downloadable PDF report per course upload

### 📝 Checklist:

- [ ] ✅ Create generatePdfHandler Lambda
  - Pull data from SurveyMeta and SurveyInsights
  - Use HTML template or markdown renderer
  - Render into PDF using pdfkit or xhtml2pdf
- [ ] ✅ Store final PDF in S3:
  - reports/{user_id}_{upload_id}.pdf
- [ ] ✅ Add download link to frontend dashboard

---

## 🧩 Phase 7: Frontend Integration

### 🎯 Objective:
Enable users to upload surveys, track status, and view insights

### 📝 Checklist:

- [ ] ✅ Login page (mocked or Cognito-based)
- [ ] ✅ Upload page (call API Gateway → upload Lambda)
- [ ] ✅ Status page
  - Show uploads from SurveyMeta
  - Show status updates (raw → processing → done)
- [ ] ✅ Insights viewer
  - Render summary + top suggestions
- [ ] ✅ PDF download button
- [ ] ✅ (Optional) QuickSight dashboard embed

---

## 🧠 Notes

- Use environment variables for all table/bucket names in Lambda
- Use Step Functions if you want to manage Glue → Bedrock → PDF flow together
- Use upload_id and user_id as traceable identifiers across all services

---

## ✅ Final Output Checklist

| Feature | Complete? |
|---------|-----------|
| User Upload + S3 + DynamoDB | ☐ |
| Glue Preprocessing → Silver Layer | ☐ |
| Metadata Updates | ☐ |
| Bedrock Summary | ☐ |
| QuickSight Dashboard | ☐ |
| PDF Report | ☐ |
| Frontend Integration | ☐ |