# 📊 SurveySynth – AI-Driven Course Feedback Analyzer

SurveySynth is a full-stack serverless application that lets course instructors upload student feedback surveys and receive **automated insights**, **actionable suggestions**, and **data visualizations**. It uses **React JS** on the frontend, with a backend built using **AWS Lambda**, **Amazon Bedrock**, **AWS Glue**, **DynamoDB**, and **S3**.

---

## 📐 Architecture Overview
```
Frontend (React)
    |
    v
API Gateway → Lambda: uploadSurveyHandler
    |
    v
S3 (raw_data_csv/) ← Glue Preprocessing Job
    |
    v
S3 (silver/) → Lambda: summarizeFeedbackHandler → Bedrock
    |
    v
DynamoDB: SurveyMeta & SurveyInsights
    |
    v
Glue: Visual job → PNG charts to S3 (visuals/)
    |
    v
Frontend (insight viewer + download PDF)
```

---

## ✅ Features Implemented

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | User Registration, Login, Survey Upload | ✅ Complete |
| **Phase 2** | Glue Preprocessing for CSVs | ✅ Complete |
| **Phase 3** | Status Update After Glue Job | ✅ Complete |
| **Phase 4** | Bedrock Analysis & Insight Generation | ✅ Complete |
| **Phase 5** | Charts via Glue (Matplotlib, Seaborn) | ✅ Complete |
| **Phase 6** | PDF Report Generation | ⬜ In Progress |
| **Phase 7** | React Dashboard (Login, Upload, Viewer) | ⬜ In Progress |

---

## 🧩 Phase-wise Breakdown

### Phase 1: Upload + Metadata

- Uploads CSV to S3 under `raw_data_csv/`
- Tracks upload in DynamoDB:
  - Table: `Users`, `SurveyMeta`
- Triggers AWS Glue ETL job

---

### Phase 2: Glue Preprocessing

- Glue Job: `SurveyPreprocessJob`
- Cleans raw CSV (drop empty rows, fix column names)
- Identifies feedback columns
- Outputs to: `silver/{user_id}/{upload_id}.csv`

---

### Phase 3: Glue Status Tracker

- Lambda: `updateStatusPostGlue`
- Trigger: EventBridge from Glue
- Updates:
  - `status = preprocessed`
  - `s3_path_silver`

---

### Phase 4: AI-Powered Insight Generation

- Lambda: `summarizeFeedbackHandler`
- Reads cleaned CSV from `silver/`
- Sends batch prompts to Amazon Bedrock (Claude)
- Generates:
  - Summary
  - Top pain points
  - Actionable suggestions
- Saves to DynamoDB: `SurveyInsights`

---

### Phase 5: Data Visualizations

- Glue Job: `SurveyVisualJob`
- Triggered by DynamoDB Stream on `SurveyInsights`
- Generates:
  - Bar chart: top actions
  - Word cloud: pain points
- Stores `.png` to: `visuals/{user_id}/{upload_id}/`

---

### Phase 6: PDF Report (WIP)

- Lambda will:
  - Pull summary & visual PNGs
  - Render into HTML → PDF
  - Store in: `reports/{user_id}_{upload_id}.pdf`

---

### Phase 7: Frontend (React JS)

- **Login/Register**
- **Upload CSV**
- **View Status**
- **View Summary + Charts**
- **Download PDF**

---

## 🧰 AWS Resources Used

| Service | Purpose |
|--------|---------|
| **S3** | Store raw, cleaned, and visual data |
| **DynamoDB** | Store user and survey metadata |
| **Lambda** | Handle uploads, analysis, glue triggers |
| **Glue** | ETL and visualization |
| **Bedrock** | Generate AI summaries |
| **EventBridge** | Detect job completions |
| **IAM** | Role-based access control |
| **React** | Frontend dashboard |

---

## 📂 Folder Structure

```
SurveySynth/
├── template.yml # SAM template
├── src/
│ └── lambdas/
│ ├── auth/ # register_user.py
│ ├── process_survey/ # uploadSurveyHandler
│ ├── summarize_feedback/ # summarizeFeedbackHandler
│ └── post_glue_update/ # updateStatusPostGlue
│ └── Visualization/ # glue_script.py,trigger_glue.py
├── frontend/ # React app
└── prompts/
├── test_data
└── dependencies

```

---

## 🚀 Deployment Guide

1. **Install AWS SAM CLI**
2. Run:
   ```bash
   sam build
   sam deploy --guided
3. Setup your S3 bucket & DynamoDB manually or via the template
4. Upload glue_deps.zip to:
5. s3://surveysynth-uploads/source_packages/glue_deps.zip


## 🎯 QA & Observability
- **CloudWatch Logs** → Use for detailed execution logs from Lambda and Glue.
- **EventBridge** → Verify that triggers fire correctly whenever data is updated or jobs complete.
- **API Testing** → Tools like Postman can be used to test endpoints (/upload, /register, /login).
- **Frontend Testing** → Validate success and error states in the React UI’s upload and insights workflow.




## 📄 Future Enhancements

- ✅ **Add Bedrock Sentiment Score in SurveyMeta**  
  Leverage Amazon Bedrock to incorporate detailed sentiment scoring alongside each survey entry, enabling more nuanced analytics in `SurveyMeta`.

- ⬜ **PDF Export via pdfkit**  
  Provide one-click PDF generation of both textual insights and charts, simplifying content sharing for instructors and stakeholders.

- ⬜ **Upload Multiple Files (Batch Processing)**  
  Add support for multi-file uploads, so multiple surveys can be processed in a single step, streamlining large batch imports.

- ⬜ **AWS Cognito for Secure Auth**  
  Integrate Cognito user pools for sign-up, sign-in, and MFA. This will further secure the SurveySynth platform and simplify identity management.

---

## 🧠 Authors
Built with ❤️ using the AWS Serverless stack and Amazon Bedrock by **Vishnu Nukala**.  
Stay in touch: [linkedin.com/in/vishnu1702](https://linkedin.com/in/vishnu1702)
