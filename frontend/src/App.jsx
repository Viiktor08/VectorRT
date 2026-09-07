import { useEffect, useRef, useState } from 'react'
import TargetSelector from './components/TargetSelector'
import AttackButtons from './components/AttackButtons'
import ResultsPanel from './components/ResultsPanel'

export default function App() {
  const [targets, setTargets] = useState([])
  const [targetIp, setTargetIp] = useState('')
  const [status, setStatus] = useState('idle') // idle | running | done | error
  const [lines, setLines] = useState([])
  const [errorMessage, setErrorMessage] = useState('')
  const wsRef = useRef(null)

  useEffect(() => {
    fetch('/api/targets')
      .then((res) => res.json())
      .then(setTargets)
      .catch(() => setTargets([]))
  }, [])

  useEffect(() => () => wsRef.current?.close(), [])

  function runAttack(attackType) {
    if (!targetIp || status === 'running') return

    setStatus('running')
    setLines([])
    setErrorMessage('')

    const jobId = crypto.randomUUID()
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${protocol}://${window.location.host}/ws/attacks/${jobId}?attack_type=${attackType}&target_ip=${targetIp}`
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.type === 'line') {
        setLines((prev) => [...prev, msg.data])
      } else if (msg.type === 'done') {
        setStatus('done')
      } else if (msg.type === 'error') {
        setStatus('error')
        setErrorMessage(msg.message)
      }
    }

    ws.onerror = () => {
      setStatus('error')
      setErrorMessage('Error de conexión con el backend')
    }
  }

  return (
    <div className="min-h-screen max-w-3xl mx-auto px-6 py-10 flex flex-col gap-6">
      <header>
        <h1 className="text-2xl font-semibold text-white">VectorRT</h1>
        <p className="text-sm text-gray-400">
          Laboratorio de red team contra infraestructura propia y aislada.
        </p>
      </header>

      <TargetSelector targets={targets} value={targetIp} onChange={setTargetIp} />

      <AttackButtons disabled={!targetIp} running={status === 'running'} onRun={runAttack} />

      <ResultsPanel status={status} lines={lines} errorMessage={errorMessage} />
    </div>
  )
}
