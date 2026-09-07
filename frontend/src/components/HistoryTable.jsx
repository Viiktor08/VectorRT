import { Fragment, useEffect, useState } from 'react'
import { AuthExpiredError, authFetch } from '../auth'

const STATUS_COLORS = {
  success: 'text-green-400',
  error: 'text-red-400',
  running: 'text-yellow-400',
}

function formatDate(iso) {
  return new Date(iso).toLocaleString()
}

export default function HistoryTable({ token, refreshKey, onAuthExpired }) {
  const [jobs, setJobs] = useState([])
  const [expandedId, setExpandedId] = useState(null)
  const [detail, setDetail] = useState(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

  useEffect(() => {
    authFetch(token, '/api/attacks/history')
      .then((res) => res.json())
      .then(setJobs)
      .catch((err) => {
        if (err instanceof AuthExpiredError) onAuthExpired()
        else setJobs([])
      })
  }, [refreshKey, token, onAuthExpired])

  async function toggleDetail(jobId) {
    if (expandedId === jobId) {
      setExpandedId(null)
      setDetail(null)
      return
    }
    setExpandedId(jobId)
    setDetail(null)
    setLoadingDetail(true)
    try {
      const res = await authFetch(token, `/api/attacks/history/${jobId}`)
      setDetail(await res.json())
    } catch (err) {
      if (err instanceof AuthExpiredError) onAuthExpired()
    } finally {
      setLoadingDetail(false)
    }
  }

  if (jobs.length === 0) {
    return <p className="text-sm text-gray-500">Todavía no hay ataques registrados.</p>
  }

  return (
    <div className="flex flex-col gap-2">
      <h2 className="text-sm font-medium text-gray-300">Histórico</h2>
      <div className="overflow-x-auto border border-gray-800 rounded-md">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-900 text-gray-400">
            <tr>
              <th className="px-3 py-2">Fecha</th>
              <th className="px-3 py-2">Tipo</th>
              <th className="px-3 py-2">Target</th>
              <th className="px-3 py-2">Estado</th>
              <th className="px-3 py-2">Duración</th>
              <th className="px-3 py-2" />
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <Fragment key={job.id}>
                <tr className="border-t border-gray-800">
                  <td className="px-3 py-2 text-gray-400">{formatDate(job.started_at)}</td>
                  <td className="px-3 py-2">{job.attack_type}</td>
                  <td className="px-3 py-2">{job.target_ip}</td>
                  <td className={`px-3 py-2 ${STATUS_COLORS[job.status] ?? 'text-gray-400'}`}>
                    {job.status}
                  </td>
                  <td className="px-3 py-2 text-gray-400">
                    {job.duration_seconds ? `${job.duration_seconds.toFixed(2)}s` : '—'}
                  </td>
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      onClick={() => toggleDetail(job.id)}
                      className="text-purple-400 hover:text-purple-300 text-xs underline"
                    >
                      {expandedId === job.id ? 'ocultar' : 'ver detalle'}
                    </button>
                  </td>
                </tr>
                {expandedId === job.id && (
                  <tr className="border-t border-gray-800 bg-black">
                    <td colSpan={6} className="px-3 py-2">
                      {loadingDetail ? (
                        <span className="text-xs text-gray-500">Cargando…</span>
                      ) : (
                        <pre className="max-h-64 overflow-y-auto whitespace-pre-wrap text-xs text-green-400">
                          {detail?.raw_output || '(sin output)'}
                        </pre>
                      )}
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
