import { useState } from 'react'

const MAX_LOAD_DURATION_SECONDS = 30
const MAX_LOAD_CONCURRENCY = 50

export default function AttackButtons({ disabled, running, onRun }) {
  const [durationSeconds, setDurationSeconds] = useState(5)
  const [concurrency, setConcurrency] = useState(10)

  const buttonClass =
    'px-4 py-2 rounded-md bg-purple-600 text-white font-medium ' +
    'hover:bg-purple-500 transition-colors ' +
    'disabled:bg-gray-800 disabled:text-gray-500 disabled:cursor-not-allowed'

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          disabled={disabled || running}
          onClick={() => onRun('port-scan')}
          className={buttonClass}
        >
          Escaneo de puertos
        </button>

        <button
          type="button"
          disabled={disabled || running}
          onClick={() => onRun('ssh-bruteforce')}
          className={buttonClass}
        >
          Fuerza bruta SSH
        </button>
      </div>

      <div className="flex flex-wrap items-end gap-3 border-t border-gray-800 pt-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="duration" className="text-xs text-gray-400">
            Duración (s, máx. {MAX_LOAD_DURATION_SECONDS})
          </label>
          <input
            id="duration"
            type="number"
            min={1}
            max={MAX_LOAD_DURATION_SECONDS}
            value={durationSeconds}
            onChange={(event) =>
              setDurationSeconds(
                Math.min(MAX_LOAD_DURATION_SECONDS, Math.max(1, Number(event.target.value) || 1)),
              )
            }
            className="w-24 bg-gray-900 border border-gray-700 rounded-md px-2 py-1 text-white"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="concurrency" className="text-xs text-gray-400">
            Concurrencia (máx. {MAX_LOAD_CONCURRENCY})
          </label>
          <input
            id="concurrency"
            type="number"
            min={1}
            max={MAX_LOAD_CONCURRENCY}
            value={concurrency}
            onChange={(event) =>
              setConcurrency(
                Math.min(MAX_LOAD_CONCURRENCY, Math.max(1, Number(event.target.value) || 1)),
              )
            }
            className="w-24 bg-gray-900 border border-gray-700 rounded-md px-2 py-1 text-white"
          />
        </div>

        <button
          type="button"
          disabled={disabled || running}
          onClick={() => onRun('load-test', { duration_seconds: durationSeconds, concurrency })}
          className={buttonClass}
        >
          Carga / DDoS pequeño
        </button>
      </div>
    </div>
  )
}
