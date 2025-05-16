import React, { useState } from "react"
import axios from "axios"
import Loading from "./Loading"

const FileUpload = () => {
  const [file, setFile] = useState(null)
  const [newPhotoUrl, setNewPhotoUrl] = useState("")
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState("")
  const [labels, setLabels] = useState([])
  const [responseLoading, setResponseLoading] = useState(false)
  const [fileSelected, setFileSelected] = useState(false)

  const handleFileChange = (e) => {
    if (e.target.files.length === 0) {
      setFile(null)
      setFileSelected(false)
      return
    }

    const file = e.target.files[0]

    if (file.size > 500 * 1024) {
      // 500KB in bytes
      alert("File size must be less than 500KB.")
      setFile(null)
      setFileSelected(false)
      return
    }

    setFile(file)
    setFileSelected(true)
  }

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a file.")
      return
    }
    setUploading(true)
    setResponseLoading(true)
    setMessage("")

    try {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = async () => {
        const base64String = reader.result.split(",")[1]

        const response = await axios.post(
          "https://h2az91frc6.execute-api.us-east-1.amazonaws.com/dev/images",
          JSON.stringify({
            file: base64String,
            filename: file.name,
          }),
          {
            headers: {
              "Content-Type": "application/json",
            },
          }
        )

        setMessage("Upload successful!")
        setNewPhotoUrl(response.data.processed_image_url)
        setLabels(response.data.labels)
        setUploading(false)
        setResponseLoading(false)
      }
    } catch (error) {
      console.error("Upload failed:", error)
      setMessage("Upload failed.")
    }
  }

  const handleReset = () => {
    setFile(null)
    setNewPhotoUrl("")
    setUploading(false)
    setMessage("")
    setLabels([])
    setResponseLoading(false)
    setFileSelected(false)
  }

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white shadow-lg rounded-lg p-6 max-w-2xl mx-auto">
        <h2 className="text-center items-center text-xl font-bold mb-4">Upload an Image</h2>
        <input type="file" accept="image/png, image/jpeg" onChange={handleFileChange} className="block w-full mb-4 border p-2 rounded" />
        <button onClick={handleUpload} disabled={uploading || !fileSelected} className="w-full bg-blue-500 text-white py-2 rounded disabled:bg-gray-300">
          {uploading ? "Uploading..." : "Upload"}
        </button>
        <button onClick={handleReset} className="w-full bg-red-500 text-white py-2 rounded mt-2">
          Reset
        </button>
        <p className="text-center text-sm text-gray-600 mt-2">{message}</p>
        {uploading && <Loading />} {/* Show loading when uploading starts */}
        {!uploading && newPhotoUrl && !responseLoading && (
          <div className="mt-6 text-center">
            <img src={newPhotoUrl} alt="Processed" className="w-full max-h-90 object-cover mx-auto rounded-lg shadow-md" />
            <h3 className="text-lg font-semibold mt-4">Detected Objects or Materials:</h3>
            <div className="grid grid-cols-3 gap-4 mt-4">
              {labels.map((label, index) => (
                <div key={index} className="bg-gray-100 p-3 rounded-lg shadow">
                  <strong>{label.Name}</strong> ({label.Confidence.toFixed(2)}%)
                  {label.BoundingBox.Width && label.BoundingBox.Height && (
                    <div className="text-xs mt-2">
                      <strong>BoundingBox:</strong>
                      <ul className="list-none">
                        <li>Width: {label.BoundingBox.Width}</li>
                        <li>Height: {label.BoundingBox.Height}</li>
                        <li>Top: {label.BoundingBox.Top}</li>
                        <li>Left: {label.BoundingBox.Left}</li>
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default FileUpload
