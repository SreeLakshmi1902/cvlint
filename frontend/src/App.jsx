import { useState } from "react"

function App() {
  const [resume, setResume] = useState(null)
  const [jobDesc, setJobDesc] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleAnalyze = async () => {

    if (!resume) {
      setError("Please upload a resume")
      return 
    }
    if (!jobDesc.trim()) {
      setError("Please enter a job description")
      return
    }
    setLoading(true)
    setError("")

    try {
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

      if (!response.ok) {
        throw new Error("Failed to analyze resume")
      }

      const data = await response.json()
      setResult(data)

    } catch (error) {
      console.error(error)
      setError("Something went wrong while analyzing the resume")
    } finally {
      setLoading(false)      
    }
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
      <button onClick={handleAnalyze} disabled={loading}>
        { loading ? "Analyzing..." : "Analyze Resume"}
      </button>
      {error && <p>{error}</p>}
      {result && (
        <div>
          <h2>Analysis Results</h2>
          <p>Score: {result.score}%</p>
          <p>
            Overall Match: {result.llm_critique.overall_match}
          </p>
          <p>
            {result.llm_critique.summary}
          </p>
          <h3>Strengths</h3>
          {result.llm_critique.strengths.map((strength, index) => (
            <div key={index}>
              <h4>{strength.title}</h4>
              <p>{strength.explantion}</p>
              <p>Evidence: {strength.evidence}</p>
            </div>
          ))}

          <h3>Missing skills</h3>
          {result.llm_critique.missing_skills.map((item, index) => (
            <div key={index}>
              <h4>{item.skill}</h4>
              <p>{item.why_it_matters}</p>
            </div>
          ))}

          <h3>ATS Issues</h3>
          {result.llm_critique.ats_issues.map((issue, index) => (
            <div key={index}>
              <h4>{issue.issue}</h4>
              <p>Impact: {issue.impact}</p>
              <p>How to fix: {issue.fix}</p>
            </div>
          ))}

          <h3>Recommendations</h3>
          {result.llm_critique.recommendations.map((item, index) => (
            <div key={index}>
              <h4>{item.priority}. {item.recommendation}</h4>
              <p>Why: {item.why}</p>
              <p>How to improve: {item.how_to_improve}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App