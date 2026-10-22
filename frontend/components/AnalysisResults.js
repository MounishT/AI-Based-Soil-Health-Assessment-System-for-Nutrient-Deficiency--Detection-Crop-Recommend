import { useState } from "react";
import { Volume2, FileText, Share2, Phone, Loader2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Line } from "react-chartjs-2";
import { apiFetch, API_URL } from "../lib/api";
import ResultCard from "./ResultCard";

export default function AnalysisResults({ results, setResults, formData }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language || "en";

  const [shareUrl, setShareUrl] = useState("");
  const [smsPhone, setSmsPhone] = useState("");
  const [smsStatus, setSmsStatus] = useState("");

  const speakResults = async () => {
    if (!results) return;
    const { soil_health_score, health_band, fertilizer_recommendation } = results;
    const band = t(health_band) || health_band.toUpperCase();
    let text = lang === "hi" ? `आपका मृदा स्वास्थ्य स्कोर ${soil_health_score} है। स्थिति ${band} है।` :
      lang === "kn" ? `ನಿಮ್ಮ ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಸ್ಕೋರ್ ${soil_health_score} ಆಗಿದೆ. ಸ್ಥಿತಿ ${band} ಆಗಿದೆ.` :
      lang === "te" ? `మీ మట్టి ఆరోగ్య స్కోర్ ${soil_health_score}. స్థితి ${band}.` :
      `Your soil health score is ${soil_health_score}. The condition is ${band}. Recommendation: ${fertilizer_recommendation[0]?.fertilizer_type || "None"} at ${fertilizer_recommendation[0]?.dosage_kg_per_acre || "0"} kg per acre.`;
    
    try {
      const res = await fetch(`${API_URL}/tts/generate`, { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify({ text, language: lang }) 
      });
      if (!res.ok) throw new Error("TTS failed");
      const audio = new Audio(URL.createObjectURL(await res.blob())); 
      audio.play();
    } catch {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = lang === "hi" ? "hi-IN" : lang === "kn" ? "kn-IN" : lang === "te" ? "te-IN" : "en-US";
      window.speechSynthesis.speak(u);
    }
  };

  const downloadPdf = async () => {
    if (!results) return;
    try {
      const res = await fetch(`${API_URL}/api/v1/report/generate`, { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify({ 
          soil_health_score: results.soil_health_score, 
          health_band: results.health_band, 
          diagnosis: results.diagnosis, 
          crop_ranking: results.crop_ranking || [], 
          fertilizer_recommendation: results.fertilizer_recommendation || [], 
          input_values: { ...formData } 
        }) 
      });
      const a = document.createElement("a"); 
      a.href = URL.createObjectURL(await res.blob()); 
      a.download = "Soil_Health_Report.pdf"; 
      a.click();
    } catch (e) { 
      console.error(e); 
    }
  };

  const sendSmsAlert = async () => {
    if (!smsPhone) return;
    setSmsStatus("sending");
    try {
      const data = await apiFetch("/sms/send", { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify({ 
          phone: smsPhone, 
          message: `Soil Alert: Health Score ${results?.soil_health_score || "N/A"}. ${results?.health_band || ""}`, 
          alert_type: "soil_alert" 
        }) 
      });
      setSmsStatus(data.success ? "sent" : "failed");
    } catch { 
      setSmsStatus("failed"); 
    }
    setTimeout(() => setSmsStatus(""), 3000);
  };

  const shareReport = async () => {
    if (!results) return;
    try {
      const data = await apiFetch("/share/create", { 
        method: "POST", 
        headers: { "Content-Type": "application/json" }, 
        body: JSON.stringify({ 
          soil_health_score: results.soil_health_score, 
          health_band: results.health_band, 
          diagnosis: results.diagnosis, 
          fertilizer_recommendation: results.fertilizer_recommendation || [], 
          crop_ranking: results.crop_ranking || [], 
          input_values: { ...formData } 
        }) 
      });
      const url = `${window.location.origin}${data.share_url}`;
      setShareUrl(url);
      navigator.clipboard?.writeText(url);
    } catch { 
      console.error("Share failed"); 
    }
  };

  return (
    <div className="space-y-6 pb-6 animate-[fadeIn_0.4s_ease]">
      <div className="flex flex-wrap justify-between items-center bg-white/80 backdrop-blur-lg rounded-2xl p-4 shadow-md">
        <h2 className="text-xl font-bold text-gray-800">{t("results_title")}</h2>
        <div className="flex flex-wrap gap-2 mt-2 md:mt-0">
          <button onClick={speakResults} className="flex items-center gap-1.5 px-3 py-2 bg-white border rounded-lg text-sm font-medium hover:bg-gray-50 shadow-sm">
            <Volume2 size={14} /> {t("listen")}
          </button>
          <button onClick={downloadPdf} className="flex items-center gap-1.5 px-3 py-2 bg-white border rounded-lg text-sm font-medium hover:bg-gray-50 shadow-sm">
            <FileText size={14} /> {t("download_pdf")}
          </button>
          <button onClick={shareReport} className="flex items-center gap-1.5 px-3 py-2 bg-white border rounded-lg text-sm font-medium hover:bg-gray-50 shadow-sm">
            <Share2 size={14} /> {t("share")}
          </button>
          <button onClick={() => { setResults(null); setShareUrl(""); }} className="flex items-center gap-1.5 px-3 py-2 bg-gray-100 rounded-lg text-sm font-medium hover:bg-gray-200">
            {t("reset")}
          </button>
        </div>
      </div>

      {shareUrl && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-3 text-sm text-green-700 flex items-center gap-2">
          🔗 Share link copied to clipboard: <a href={shareUrl} className="underline font-medium">{shareUrl}</a>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ResultCard className="flex flex-col items-center">
          <h3 className="font-semibold text-gray-600 mb-2">{t("health_score")}</h3>
          <div className={`w-28 h-28 rounded-full flex items-center justify-center text-3xl font-bold text-white shadow-lg ${
            results.health_band === "excellent" || results.health_band === "good" ? "score-good" :
            results.health_band === "moderate" ? "score-moderate" : "score-poor"
          }`}>
            {Math.round(results.soil_health_score)}
          </div>
          <p className="mt-2 font-semibold text-gray-500">{t(results.health_band) || results.health_band?.toUpperCase()}</p>
        </ResultCard>

        <ResultCard title={t("diagnosis")}>
          <div className="space-y-2">
            {Object.entries(results.diagnosis || {}).map(([key, val]) => (
              <div key={key} className={`flex justify-between items-center p-2 rounded-lg text-sm ${val === "low" ? "bg-red-50 border-l-4 border-red-400" : "bg-green-50 border-l-4 border-green-400"}`}>
                <span className="font-semibold uppercase">{key}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${val === "low" ? "bg-red-100 text-red-700" : val === "high" ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"}`}>
                  {t(val) || val.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </ResultCard>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ResultCard title={t("fert_rec")}>
          {results.fertilizer_recommendation?.length > 0 ? results.fertilizer_recommendation.map((f, i) => (
            <div key={i} className="bg-white p-3 rounded-lg mb-2 border-l-4 border-primary-400">
              <div className="font-semibold text-sm">{f.nutrient}: {f.fertilizer_type} ({f.dosage_kg_per_acre} kg/acre)</div>
              <p className="text-xs text-gray-500 mt-1">{f.schedule}</p>
            </div>
          )) : <p className="text-sm text-gray-500">None needed.</p>}
        </ResultCard>

        <ResultCard title={t("crop_rec")}>
          <ol className="space-y-2">
            {results.crop_ranking?.slice(0, 3).map((crop, i) => (
              <li key={i} className="flex items-center gap-3 p-2 bg-white rounded-lg">
                <span className={`w-7 h-7 flex items-center justify-center rounded-full text-white text-xs font-bold ${i === 0 ? "bg-yellow-500" : i === 1 ? "bg-gray-400" : "bg-amber-600"}`}>{i + 1}</span>
                <div>
                  <span className="font-semibold text-sm">{crop.crop}</span>
                  <span className="text-xs text-gray-500 ml-2">Score: {crop.suitability_score}</span>
                </div>
              </li>
            ))}
          </ol>
        </ResultCard>
      </div>

      {results.trend_prediction && (
        <ResultCard title={t("trend")}>
          <p className="text-sm text-gray-500 mb-3">{results.trend_prediction.summary}</p>
          <div className="h-64">
            <Line data={results.trend_prediction.chart_data} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </ResultCard>
      )}

      <ResultCard title={t("sms_alerts")} icon={<Phone size={16} />}>
        <p className="text-xs text-gray-500 mb-3">Get SMS alerts when soil conditions are critical.</p>
        <div className="flex gap-2">
          <input 
            type="tel" 
            placeholder={t("phone_number")} 
            value={smsPhone} 
            onChange={(e) => setSmsPhone(e.target.value)}
            className="flex-1 border rounded-lg px-3 py-2 text-sm outline-none focus:border-primary-500" 
          />
          <button 
            onClick={sendSmsAlert} 
            disabled={!smsPhone || smsStatus === "sending"}
            className="btn-green px-4 py-2 rounded-lg text-sm font-medium disabled:bg-gray-400 flex items-center gap-1"
          >
            {smsStatus === "sending" ? <Loader2 size={14} className="animate-spin" /> : smsStatus === "sent" ? "✓ Sent" : t("send_alert")}
          </button>
        </div>
      </ResultCard>
    </div>
  );
}
