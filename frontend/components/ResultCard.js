export default function ResultCard({ title, icon, children, className = "" }) {
  return (
    <div className={`bg-white/80 backdrop-blur rounded-2xl p-6 shadow-md animate-[fadeIn_0.3s_ease] ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
          {icon}
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}
