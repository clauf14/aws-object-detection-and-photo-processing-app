# 📸 Image Analysis App with AWS Services

This application features a **React frontend** that interacts with a powerful backend pipeline built entirely with AWS services. Using Python in the Lambda function, the image is processed using Pillow library. A rectangle is drawn around detected objects based on bounding box coordinates, and the object’s name is overlaid on the image. If an object is detected but lacks bounding box data, it will not be drawn on the 
image, though it will still be included in the metadata. Works for multiple objects too!

## Demo
![Demo GIF](https://github.com/clauf14/aws-object-detection-and-photo-processing-app/raw/main/2025-05-1610-54-32-ezgif.com-video-to-gif-converter.gif)

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
