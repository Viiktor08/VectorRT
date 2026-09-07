import { useEffect, useRef } from 'react'

const STATUS_LABELS = {
  idle: 'En espera',
  running: 'Ejecutando…',
  done: 'Finalizado',
  error: 'Error',
}

const STATUS_COLORS = {
  idle: 'text-gray-400',
  running: 'text-yellow-400',
  done: 'text-green-400',
  error: 'text-red-400',
}

export default function ResultsPanel({ status, lines, errorMessage }) {
  const containerRef = useRef(null)

  useEffect(() => {
    containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight })
  }, [lines])

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2 text-sm">
        <span className="text-gray-400">Estado:</span>
        <span className={STATUS_COLORS[status]}>{STATUS_LABELS[status]}</span>
      </div>

      <pre
        ref={containerRef}
        className="bg-black border border-gray-800 rounded-md p-4 h-80 overflow-y-auto
                   text-sm text-green-400 whitespace-pre-wrap"
      >
        {lines.length === 0
          ? '// El resultado del ataque aparecerá aquí'
          : lines.join('\n')}
      </pre>

      {status === 'error' && errorMessage && (
        <p className="text-sm text-red-400">{errorMessage}</p>
      )}
    </div>
  )
}
