# 📸 Image Analysis App with AWS Services

I’m excited to share the source code for a project that demonstrates a modern, serverless architecture using several AWS services. Below is an overview of the app and instructions on how to run it.

---

## 🔧 Project Overview

This application features a **React frontend** that interacts with a powerful backend pipeline built entirely with AWS services.

### 🧩 Architecture & Services Used

- **Frontend**:  
  Built with **React**, the UI allows users to upload images, which are then sent to the backend via a POST request.

- **API Gateway**:  
  Serves as the entry point to the backend, exposing an endpoint that triggers further processing.

- **AWS Lambda**:  
  The API Gateway invokes a Lambda function that orchestrates the entire workflow.

- **Amazon S3**:  
  Stores the uploaded images reliably and securely.

- **Amazon DynamoDB**:  
  Persists metadata related to each image for fast and scalable querying.

- **Amazon Rekognition**:  
  Analyzes the image to detect objects, scenes, and labels using machine learning.

- **Amazon SNS**:  
  Sends an email notification once the image analysis is complete, informing the user about the results.

---

## 🚀 How to Run the Project

### 1. Clone the Repository into a folder

```bash
git clone https://github.com/clauf14/aws-object-detection-and-photo-processing-app
```

### 2. Open the folder with VS Code
### 3. Type in terminal
```bash
npm start
```
