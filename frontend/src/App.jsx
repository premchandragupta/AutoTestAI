
import React, {useState} from 'react'
import axios from 'axios'
const BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
export default function App(){
  const [file,setFile]=useState(null)
  const [token,setToken]=useState(localStorage.getItem('token')||'')
  const [docId,setDocId]=useState('')
  const [status,setStatus]=useState('')

  async function loginWithApiKey(){
    const apiKey = prompt('Enter API key (demo-api-key-12345):')
    if(!apiKey) return
    try{
      const res = await axios.post(`${BACKEND}/api/auth/token`, null, { headers: {'x-api-key': apiKey} })
      setToken(res.data.access_token)
      localStorage.setItem('token', res.data.access_token)
      alert('Token saved')
    }catch(e){ alert('Auth failed') }
  }

  async function upload(e){
    e.preventDefault()
    if(!file) return alert('Choose .txt file')
    const form = new FormData(); form.append('file', file)
    setStatus('Uploading...')
    try{
      const res = await axios.post(`${BACKEND}/api/upload`, form, { headers: {'Authorization': 'Bearer '+token}, })
      setDocId(res.data.document_id); setStatus('Done: '+res.data.generated+' testcases')
    }catch(err){ console.error(err); setStatus('Upload failed') }
  }

  async function fetchTC(){ if(!docId) return alert('No doc id'); const res = await axios.get(`${BACKEND}/api/documents/${docId}/testcases`, { headers: {'Authorization':'Bearer '+token} }); alert(JSON.stringify(res.data,null,2)) }

  return (<div className="container"><h1>AutoTestAI</h1>
    <button onClick={loginWithApiKey}>Get JWT (using API key)</button>
    <form onSubmit={upload}><input type="file" accept=".txt" onChange={e=>setFile(e.target.files[0])} /><button>Upload</button></form>
    <p>Status: {status}</p>
    <input placeholder="Document ID" value={docId} onChange={e=>setDocId(e.target.value)} /> <button onClick={fetchTC}>Fetch Testcases</button>
  </div>)
}
