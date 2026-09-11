import { useState } from "react"

function App() {
  const [resume, setResume] = useState(null)
  const [jobDesc, setJobDesc] = useState("")

  const handleAnalyze = async () => {

    const formData = new FormData()

    formData.append("resume", resume)
    formData.append("job_desc", jobDesc)

    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/parse-resume",
      {
        method: "POST",
        body: formData
      }
    )

    const data = await response.json()

    console.log(data)
    
  }

  return (
    <div>
      <h1>CVLint</h1>
      <p>AI-powered resume analysis</p>
      <div>
        <label>Upload Resume</label>
        <br /> 
        <input
          type='file'
          accept=".docx" 
          onChange={(event) => setResume(event.target.files[0])}
        />
      </div>
      <br /> 
      <div>
        <label>Job Description</label>
        <br />
        <textarea
          rows="10"
          cols="60"
          placeholder="Paste the job description"
          value={jobDesc}
          onChange={(event) => setJobDesc(event.target.value)}
        />
      </div>
      <br /> 
      <button onClick={handleAnalyze}>
        Analyze Resume
      </button>
    </div>
  )
}

export default App
