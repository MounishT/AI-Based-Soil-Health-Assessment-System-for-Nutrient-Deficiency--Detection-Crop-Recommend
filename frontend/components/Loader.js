import { Loader2 } from "lucide-react";

export default function Loader({ size = 16, text, className = "" }) {
  return (
    <div className={`flex items-center justify-center gap-2 text-gray-500 ${className}`}>
      <Loader2 size={size} className="animate-spin" />
      {text && <span className="text-sm font-medium">{text}</span>}
    </div>
  );
}
