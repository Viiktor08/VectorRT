export default function TargetSelector({ targets, value, onChange }) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor="target" className="text-sm text-gray-400">
        Target
      </label>
      <select
        id="target"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="bg-gray-900 border border-gray-700 rounded-md px-3 py-2 text-white"
      >
        <option value="">Selecciona un target del laboratorio…</option>
        {targets.map((target) => (
          <option key={target.ip} value={target.ip}>
            {target.label} ({target.ip})
          </option>
        ))}
      </select>
    </div>
  )
}
