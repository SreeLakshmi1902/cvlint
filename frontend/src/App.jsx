import { useState } from "react"
import "./App.css"

const STATUS_LABELS = {
  matched: "Matched",
  missing: "Missing",
  needs_review: "Needs review",
}

function CritiquePoints({ items, evidenceById }) {
  if (items.length === 0) return <p><em>None identified.</em></p>
  return items.map((item, index) => (
    <div key={index} className="critique-point">
      <p>{item.point}</p>
      {item.evidence_ids.map((id, idIndex) => {
        const bullet = evidenceById[id]
        return (
          <div key={`${id}-${idIndex}`} className="evidence">
            <p>
              <strong className="evidence-id">[{id}]</strong>{" "}
              {bullet
                ? bullet.text
                : <em className="unverified">Not among the bullets shown to the model</em>}
            </p>
          </div>
        )
      })}
    </div>
  ))
}

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
    setResult(null)

    try {
      const formData = new FormData()

      formData.append("resume", resume)
      formData.append("job_desc", jobDesc)

      const response = await fetch(
        "http://localhost:8000/api/v1/parse-resume",
        {
          method: "POST",
          body: formData
        }
      )

      if (!response.ok) {
        const body = await response.json().catch(() => null)
        throw new Error(body?.detail || "Failed to analyze resume")
      }

      const data = await response.json()
      setResult(data)

    } catch (error) {
      console.error(error)
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }
  const evidenceById = result
    ? Object.fromEntries(result.evidence.map((item) => [item.id, item]))
    : {}

  return (
    <div>
      <h1>CVLint</h1>
      <p>AI-powered resume analysis</p>
      <div>
        <label>Upload Resume</label>
        <br />
        <input
          type='file'
          accept=".docx, .pdf"
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
        {loading ? "Analyzing..." : "Analyze Resume"}
      </button>
      {error && <p>{error}</p>}
      {result && (
        <div className="results">
          <br/>
          <h2>Analysis Results</h2>
          <br/>
          <p><strong>Technical coverage:</strong> {result.score ?? "N/A"}{result.score !== null && "%"}</p>
          <p>
            <strong>Overall Match:</strong> {result.llm_critique.overall_match}
          </p>
          <p>
            {result.llm_critique.summary}
          </p>
          <h3>Job requirements</h3>
          <table className="requirements">
            <thead>
              <tr>
                <th>Requirement</th>
                <th>Importance</th>
                <th>Status</th>
                <th>From the job description</th>
              </tr>
            </thead>
            <tbody>
              {result.requirements.map((req, index) => (
                <tr key={index}>
                  <td>
                    {req.name}
                    {req.alternatives.length > 0 && ` (or ${req.alternatives.join(", ")})`}
                  </td>
                  <td>{req.importance === "must_have" ? "Must have" : "Nice to have"}</td>
                  <td>
                    <span className={`status status-${req.status}`}>{STATUS_LABELS[req.status]}</span>
                    {req.matched_as && req.matched_as !== req.name && ` (via ${req.matched_as})`}
                  </td>
                  <td>
                    "{req.source_quote}"
                    {!req.quote_verified && <em className="unverified"> Not found in the job description</em>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <h3>Strengths</h3>
          <CritiquePoints items={result.llm_critique.strengths} evidenceById={evidenceById} />

          <h3>Weak areas</h3>
          <CritiquePoints items={result.llm_critique.weak_areas} evidenceById={evidenceById} />

          <h3>Recommendations</h3>
          {result.llm_critique.recommendations.map((item, index) => (
            <div key={index} className="critique-point">
              <h4>{item.priority}. {item.action}</h4>
              <p><strong>Why:</strong> {item.why}</p>
            </div>
          ))}
          
          <h3>Resume evidence used</h3>
          <p><strong>The critique was based on these resume bullets, chosen by hybrid search as the most relevant to the job.</strong></p>
          <br/>
          {result.evidence.map((item) => (
            <div key={item.id} className="evidence">
              <p>
                <strong className="evidence-id">[{item.id}]</strong> {item.context && <em>{item.context}</em>}
              </p>
              <p>{item.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App