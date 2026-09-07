const ATTACKS = [
  { type: 'port-scan', label: 'Escaneo de puertos', available: true },
  { type: 'ssh-bruteforce', label: 'Fuerza bruta SSH', available: false },
  { type: 'load-test', label: 'Carga / DDoS pequeño', available: false },
]

export default function AttackButtons({ disabled, running, onRun }) {
  return (
    <div className="flex flex-wrap gap-3">
      {ATTACKS.map((attack) => (
        <button
          key={attack.type}
          type="button"
          disabled={disabled || running || !attack.available}
          onClick={() => onRun(attack.type)}
          title={attack.available ? undefined : 'Disponible en Fase 3'}
          className="px-4 py-2 rounded-md bg-purple-600 text-white font-medium
                     hover:bg-purple-500 transition-colors
                     disabled:bg-gray-800 disabled:text-gray-500 disabled:cursor-not-allowed"
        >
          {attack.label}
        </button>
      ))}
    </div>
  )
}
