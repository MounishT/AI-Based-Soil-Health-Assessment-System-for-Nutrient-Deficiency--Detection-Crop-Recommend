export default function InputField({ label, icon, type = "number", value, onChange, required = true, step = "any", placeholder = "" }) {
  return (
    <div>
      <label className="flex items-center gap-1 text-sm font-medium text-gray-500 mb-1">
        {icon} {label}
      </label>
      <input
        type={type}
        step={step}
        required={required}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full border-2 border-transparent rounded-lg px-3 py-2 bg-gray-50 focus:border-primary-500 focus:bg-white outline-none transition-all text-sm"
      />
    </div>
  );
}
