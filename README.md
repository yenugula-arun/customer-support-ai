# Intelligent Customer Support Ticket Triage & Resolution Assistant

An AI-powered serverless customer support system built on AWS that automatically classifies support tickets, retrieves knowledge base responses, invokes backend tools using Amazon Bedrock Agents, and supports human approval workflows for sensitive operations.

---

## Project Overview

This project solves the problem of manually handling customer support tickets by automating the complete ticket lifecycle.

The system:

- Accepts customer support tickets through a REST API
- Uploads ticket attachments to Amazon S3
- Stores tickets in DynamoDB
- Automatically classifies tickets using Amazon Bedrock
- Retrieves grounded responses from a Bedrock Knowledge Base (RAG)
- Invokes backend tools through Amazon Bedrock Agents
- Sends approval requests for sensitive operations
- Allows approval through both Email and Frontend
- Displays the complete workflow in a React dashboard

---

# Architecture

```
                                                ┌──────────────────────────────┐
                                                │       React Frontend         │
                                                │ (Customer / Admin Dashboard) │
                                                └──────────────┬───────────────┘
                                                               │
                                                               ▼
                                                  Amazon Cognito User Pool
                                                    Authentication & Roles
                                                               │
                                                               ▼
                                                      Amazon API Gateway
                                                               │
              ┌───────────────────────────────┬────────────────┼──────────────────┬────────────────────┐
              │                               │                │                  │                    │
              ▼                               ▼                ▼                  ▼                    ▼
  TicketIngestionFunction        TicketRetrievalFunction  TicketUpdateFunction  TicketDeleteFunction  TicketUploadFunction
(Create Ticket API)               (View Tickets API)       (Admin Update)        (Delete Ticket)      (Upload Attachment)
              │                               │                │                  │                    │
              ▼                               ▼                ▼                  ▼                    ▼
         Amazon SQS                    Amazon DynamoDB    Amazon DynamoDB   Amazon DynamoDB         Amazon S3
              │
              ▼
  TicketProcessorFunction
(Store Ticket in DynamoDB)
              │
              ▼
       Amazon DynamoDB
              │
      DynamoDB Streams
              │
              ▼
      AIEnrichmentFunction
              │
      ┌───────┼──────────────────────────────┐
      │       │                              │
      ▼       ▼                              ▼
 Amazon Bedrock             Bedrock Knowledge Base        Bedrock Agent
(Classification)               (RAG Search)             (Action Groups)
      │                               │                       │
      └───────────────┬───────────────┘                       │
                      ▼                                       ▼
             AI Classification                  SupportToolsFunction
       - Category                               │
       - Priority                               │
       - Sentiment                              │
       - Language                               │
                                                 ├──────────────► getOrderStatus
                                                 │                    │
                                                 │                    ▼
                                                 │          Final Response Generated
                                                 │                    │
                                                 │                    ▼
                                                 │             Update DynamoDB
                                                 │
                                                 ├──────────────► issueRefund
                                                 │                    │
                                                 │                    ▼
                                                 │              Amazon SNS Email
                                                 │
                                                 └──────────────► resetPassword
                                                                      │
                                                                      ▼
                                                                Amazon SNS Email

                                         ┌────────────────────────────┴────────────────────────────┐
                                         │                                                         │
                                         ▼                                                         ▼
                          Email Approve / Reject                                   Frontend Approve / Reject
                                         │                                                         │
                                         └───────────────────────┬─────────────────────────────────┘
                                                                 ▼
                                                        ApprovalFunction
                                                                 │
                                                                 ▼
                                                        Amazon DynamoDB
                                                                 │
                                                                 ▼
                                                Final Response / Ticket Updated
```

---

# AWS Services Used

| Service | Purpose |
|----------|---------|
| API Gateway | REST APIs |
| Lambda | Serverless backend |
| SQS | Ticket queue |
| DynamoDB | Ticket storage |
| DynamoDB Streams | Trigger AI processing |
| Amazon S3 | Attachment storage |
| Amazon Bedrock | Ticket classification |
| Bedrock Knowledge Base | RAG responses |
| Bedrock Agent | Tool invocation |
| Amazon SNS | Approval emails |
| Amazon Cognito | Authentication |
| CloudWatch | Monitoring & Logs |
| AWS SAM | Infrastructure as Code |

---

# Features

## Customer Features

- User Signup/Login using Cognito
- Create Support Tickets
- Upload Attachments
- View Ticket Status
- View AI Generated Resolution
- Download Attachments

---

## AI Features

Automatic:

- Category Classification
- Priority Detection
- Sentiment Analysis
- Language Detection
- Suggested Resolution Generation

Powered by Amazon Bedrock.

---

## RAG (Knowledge Base)

The application searches a Knowledge Base before generating responses.

Example categories:

- Refund Policy
- Password Reset
- Order Delivery
- Account Support

Grounded responses reduce hallucinations.

---

## Agentic AI

Amazon Bedrock Agents invoke backend tools automatically.

Implemented tools:

### getOrderStatus

Returns current order status.

Example:

```
Order ORD-12345 status: Shipped
```

---

### issueRefund

Requires human approval.

Workflow:

Customer Request

↓

SNS Email

↓

Approve / Reject

↓

Final Response

---

### resetPassword

Requires human approval.

Workflow:

Customer Request

↓

SNS Email

↓

Approve / Reject

↓

Final Response

---

# Human-in-the-loop Approval

Sensitive actions require manual approval.

Approval methods:

- Email
- Frontend Dashboard

Implemented protections:

- Prevent duplicate approvals
- Prevent duplicate rejections
- Disable approval after completion
- Hide frontend approval buttons after processing

---

# Ticket Workflow

```
Customer
      │
      ▼
Create Ticket
      │
      ▼
API Gateway
      │
      ▼
SQS Queue
      │
      ▼
Processor Lambda
      │
      ▼
DynamoDB
      │
      ▼
AI Enrichment
      │
      ▼
Classification
      │
      ▼
Knowledge Base
      │
      ▼
Bedrock Agent
      │
      ▼
Support Tool
      │
      ▼
Approval (if required)
      │
      ▼
Final Response
```

---

# Project Structure

```
customer-support-ai

backend/
│
├── ingestion/
├── processor/
├── retrieval/
├── update/
├── delete/
├── upload/
├── ai-enrichment/
├── approval/
├── tools/
│     └── support-tools/
└── post-confirmation/

frontend/

knowledge-base/

template.yaml
README.md
```

---

# Frontend

Built using:

- React
- Vite
- Tailwind CSS
- Axios
- React Router
- Recharts

Includes:

- Dashboard
- Ticket List
- Ticket Details
- Analytics Dashboard
- Pending Approvals
- Profile Page

---

# Analytics Dashboard

Displays:

- Total Tickets
- Open Tickets
- Pending Approvals
- Resolved Tickets
- Ticket Category Distribution
- Priority Distribution
- Ticket Status
- Sentiment Analysis
- AI Tool Usage

---

# Monitoring

CloudWatch Dashboard includes:

- Lambda Invocations
- Errors
- Duration
- API Gateway Metrics
- DynamoDB Metrics
- SNS Metrics

CloudWatch Alarm configured for Lambda Errors.

---

# Security

- Amazon Cognito Authentication
- IAM Least Privilege Policies
- Serverless Architecture
- Approval workflow for destructive actions

---

# Deployment

## Build

```bash
sam build
```

## Deploy

```bash
sam deploy --guided
```

---

# Run Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Future Enhancements

- Amazon SES Email Ticket Ingestion
- Slack Approval Integration
- Bedrock Guardrails
- Secrets Manager Integration
- Multi-language Support
- Amazon Connect Voice Integration
- Cost Dashboard
- Evaluation Dataset
- Tool Call Analytics
- Admin Audit Logs

---

# Author

**Arun Yenugula**

B.Tech – Artificial Intelligence & Machine Learning

AWS | Generative AI | Serverless | React | Python

---

# License

This project is intended for educational and portfolio purposes.