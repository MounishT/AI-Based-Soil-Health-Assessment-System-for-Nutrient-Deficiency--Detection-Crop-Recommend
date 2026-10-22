"use client";

import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { Clock, Loader2, FileText, ChevronRight } from "lucide-react";
import ReportModal from "./ReportModal";

export default function HistoryList({ refreshTrigger }) {
  const [history, setHistory] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, [refreshTrigger]);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch("/api/v1/history?limit=10");
      setHistory(data);
    } catch (err) {
      setError(err.message || "Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Unknown Date";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-GB", { day: '2-digit', month: 'short', year: 'numeric' });
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "bg-green-100 text-green-800";
    if (score >= 60) return "bg-blue-100 text-blue-800";
    if (score >= 40) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  return (
    <div className="bg-white/80 backdrop-blur-lg p-4 md:p-6 rounded-2xl shadow-md flex flex-col h-full">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <Clock className="text-primary-500" size={20} />
        Previous Analyses
      </h2>

      {loading ? (
        <div className="flex-1 space-y-3" data-testid="skeleton-loader">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse flex items-center gap-3 p-3 border rounded-xl">
              <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/3"></div>
              </div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="text-sm text-red-500 p-3 bg-red-50 rounded-lg">
          {error}
          <button onClick={fetchHistory} className="ml-2 underline text-red-700">Retry</button>
        </div>
      ) : history.items.length === 0 ? (
        <div className="text-center py-8 text-gray-500 flex flex-col items-center">
          <FileText size={32} className="mb-2 text-gray-300" />
          <p className="text-sm">No analysis history yet.</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto pr-1 space-y-3">
          {history.items.map(report => (
            <div 
              key={report.id} 
              onClick={() => setSelectedReport(report)}
              className="flex items-center gap-3 p-3 border rounded-xl hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <div className="w-12 h-12 flex-shrink-0 bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center border border-gray-200">
                {report.image_path ? (
                   <img src={`http://localhost:8000/${report.image_path}`} alt="Soil" className="w-full h-full object-cover" />
                ) : (
                   <SproutIconFallback />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-start mb-1">
                  <p className="text-sm font-medium text-gray-800 truncate">
                    {formatDate(report.created_at)}
                  </p>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${getScoreColor(report.score)}`}>
                    {report.score ? Math.round(report.score) : "--"}
                  </span>
                </div>
                <p className="text-xs text-gray-500 truncate">
                  Status: {report.health_status || "Unknown"}
                </p>
              </div>
              <ChevronRight size={16} className="text-gray-400" />
            </div>
          ))}
        </div>
      )}

      {selectedReport && (
        <ReportModal report={selectedReport} onClose={() => setSelectedReport(null)} />
      )}
    </div>
  );
}

function SproutIconFallback() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400">
      <path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>
    </svg>
  );
}
