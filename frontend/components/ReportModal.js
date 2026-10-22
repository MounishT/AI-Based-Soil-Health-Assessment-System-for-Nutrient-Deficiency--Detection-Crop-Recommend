"use client";

import { X, Calendar, Droplet, FlaskConical } from "lucide-react";

export default function ReportModal({ report, onClose }) {
  if (!report) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white w-full max-w-lg rounded-2xl shadow-xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Calendar size={18} className="text-primary-500" />
            Report: {new Date(report.created_at).toLocaleDateString()}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-6">
          
          <div className="flex gap-4 items-center">
            {report.image_path && (
              <img 
                src={`http://localhost:8000/${report.image_path}`} 
                alt="Soil Sample" 
                className="w-24 h-24 object-cover rounded-xl border"
              />
            )}
            <div>
              <p className="text-sm text-gray-500 uppercase tracking-wider">Health Score</p>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold text-gray-800">
                  {report.score ? Math.round(report.score) : "N/A"}
                </span>
                <span className="text-sm font-medium text-gray-500">/ 100</span>
              </div>
              <p className="text-sm mt-1 font-medium text-primary-700">Status: {report.health_status}</p>
            </div>
          </div>

          <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100">
            <h3 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <FlaskConical size={16} /> Nutrients & Soil Properties
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500">Nitrogen (N)</p>
                <p className="font-medium text-gray-800">{report.nitrogen || "--"} mg/kg</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Phosphorus (P)</p>
                <p className="font-medium text-gray-800">{report.phosphorus || "--"} mg/kg</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Potassium (K)</p>
                <p className="font-medium text-gray-800">{report.potassium || "--"} mg/kg</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">pH Level</p>
                <p className="font-medium text-gray-800">{report.ph || "--"}</p>
              </div>
            </div>
          </div>

          {report.recommendations && report.recommendations.crop_recommendation && (
            <div className="bg-green-50/50 p-4 rounded-xl border border-green-100">
              <h3 className="text-sm font-semibold text-green-900 mb-2 flex items-center gap-2">
                <Droplet size={16} /> Recommendations
              </h3>
              <p className="text-sm text-gray-700">
                {report.recommendations.crop_recommendation}
              </p>
            </div>
          )}

        </div>
        
        {/* Footer */}
        <div className="p-4 border-t bg-gray-50 text-right">
          <button 
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 text-sm font-medium rounded-lg hover:bg-gray-300 transition"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
