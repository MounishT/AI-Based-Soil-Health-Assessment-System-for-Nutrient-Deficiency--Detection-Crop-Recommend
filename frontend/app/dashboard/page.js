"use client";

import { useState } from "react";
import {
  Globe, Cloud, TrendingUp, Bug, Calculator, X, AlertTriangle,
  Sprout, CloudRain, IndianRupee, LogOut
} from "lucide-react";
import "../../i18n";
import { useTranslation } from "react-i18next";
import ChatWidget from "../../components/ChatWidget";
import SoilAnalysisForm from "../../components/SoilAnalysisForm";
import AnalysisResults from "../../components/AnalysisResults";
import ResultCard from "../../components/ResultCard";
import Loader from "../../components/Loader";
import ProtectedRoute from "../../components/ProtectedRoute";
import HistoryList from "../../components/HistoryList";
import { apiFetch } from "../../lib/api";
import { useAuth } from "../../lib/auth-context";
import { useRouter } from "next/navigation";

import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

function DashboardContent() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language || "en";
  const { user, logout } = useAuth();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState("analysis");

  // Form State
  const [formData, setFormData] = useState({ nitrogen: "", phosphorus: "", potassium: "", ph: "" });
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [inputMode, setInputMode] = useState(null);
  const [historyRefresh, setHistoryRefresh] = useState(0);

  // Analysis State
  const [analysis, setAnalysis] = useState({ loading: false, error: null, results: null });

  // Weather State
  const [weather, setWeather] = useState({ loading: false, error: null, data: null });

  // Prices State
  const [prices, setPrices] = useState({ loading: false, error: null, data: [] });

  // Pest State
  const [pest, setPest] = useState({ loading: false, error: null, result: null });

  // Profit State
  const [profit, setProfit] = useState({ loading: false, error: null, result: null });
  const [profitForm, setProfitForm] = useState({ farm_size_acres: "", crop_type: "Rice" });

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setAnalysis({ ...analysis, loading: true, error: null });
    try {
      let image_id = null;
      if (image) {
        const fd = new FormData();
        fd.append("file", image);
        const imgRes = await apiFetch("/api/v1/images", { method: "POST", body: fd });
        image_id = imgRes.id;
      }

      const resData = await apiFetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          field_id: 1,
          nitrogen: +formData.nitrogen,
          phosphorus: +formData.phosphorus,
          potassium: +formData.potassium,
          ph: +formData.ph,
          image_id,
          fuse: true,
        }),
      });
      setAnalysis({ loading: false, error: null, results: resData });
      setHistoryRefresh(prev => prev + 1);
    } catch (err) {
      setAnalysis({ loading: false, error: err.message, results: null });
    }
  };

  const fetchWeather = async () => {
    setWeather({ ...weather, loading: true, error: null });
    try {
      const data = await apiFetch("/weather/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat: 28.6139, lon: 77.2090, fertilizer_recommended: !!analysis.results }),
      });
      setWeather({ loading: false, error: null, data });
    } catch (err) {
      setWeather({ loading: false, error: err.message, data: { alert: false, message: "Could not fetch weather data.", temp_c: 0, humidity: 0, description: "N/A", rain_expected: false } });
    }
  };

  const fetchPrices = async () => {
    setPrices({ ...prices, loading: true, error: null });
    try {
      const data = await apiFetch("/market/prices");
      setPrices({ loading: false, error: null, data: data.prices || [] });
    } catch (err) {
      setPrices({ loading: false, error: err.message, data: [] });
    }
  };

  const handlePestDiagnose = async (file) => {
    if (!file) return;
    setPest({ ...pest, loading: true, error: null, result: null });
    try {
      const fd = new FormData();
      fd.append("file", file);
      const data = await apiFetch("/pest/diagnose", { method: "POST", body: fd });
      setPest({ loading: false, error: null, result: data });
    } catch (err) {
      setPest({ loading: false, error: err.message, result: { disease: "Error", cause: "Could not diagnose", treatment: "Try again later", severity: "unknown", confidence: 0 } });
    }
  };

  const calculateProfit = async () => {
    if (!profitForm.farm_size_acres) return;
    setProfit({ ...profit, loading: true, error: null });
    try {
      const data = await apiFetch("/profit/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ farm_size_acres: +profitForm.farm_size_acres, crop_type: profitForm.crop_type }),
      });
      setProfit({ loading: false, error: null, result: data });
    } catch (err) {
      setProfit({ ...profit, loading: false, error: err.message });
    }
  };

  const tabs = [
    { id: "analysis", icon: <Sprout size={16} />, label: "Analysis" },
    { id: "weather", icon: <Cloud size={16} />, label: t("weather_alerts") },
    { id: "prices", icon: <IndianRupee size={16} />, label: t("market_prices") },
    { id: "pest", icon: <Bug size={16} />, label: t("scan_disease") },
    { id: "profit", icon: <Calculator size={16} />, label: t("profit_calculator") },
  ];

  return (
    <div className="min-h-screen pb-28">
      <div className="max-w-[1200px] mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Main Content Area */}
        <div className="lg:col-span-3 flex flex-col space-y-6">
          <header className="flex flex-wrap justify-between items-center bg-white/80 backdrop-blur-lg p-4 rounded-2xl shadow-md">
          <h1 className="text-xl md:text-2xl font-bold text-primary-800 flex items-center gap-2">
            <Sprout className="text-primary-500" /> {t("title")}
          </h1>
          <div className="flex items-center gap-3 mt-2 md:mt-0">
            {user && (
              <span className="text-sm text-gray-600 hidden md:inline">
                {user.full_name || user.email}
              </span>
            )}
            <Globe size={16} className="text-gray-500" />
            <select value={lang} onChange={(e) => i18n.changeLanguage(e.target.value)} className="text-sm border rounded-lg px-2 py-1 bg-white">
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="kn">ಕನ್ನಡ</option>
              <option value="te">తెలుగు</option>
            </select>
            <button onClick={handleLogout} className="flex items-center gap-1 text-sm text-red-600 hover:text-red-800 transition-colors" title="Logout">
              <LogOut size={16} />
            </button>
          </div>
          </header>

          <div className="flex gap-1 overflow-x-auto pb-2 bg-white/60 backdrop-blur rounded-xl p-1">
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${activeTab === tab.id ? "tab-active shadow-md" : "tab-inactive"}`}>
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {analysis.error && (
          <div className="error-toast mb-4 flex items-center gap-2">
            <AlertTriangle size={18} className="text-red-500 flex-shrink-0" />
            <span className="error-toast-msg">{analysis.error}</span>
            <button onClick={() => setAnalysis({ ...analysis, error: null })} className="error-toast-close ml-auto"><X size={16} /></button>
          </div>
        )}

        {activeTab === "analysis" && !analysis.results && (
          <SoilAnalysisForm
            formData={formData}
            setFormData={setFormData}
            image={image}
            setImage={setImage}
            imagePreview={imagePreview}
            setImagePreview={setImagePreview}
            inputMode={inputMode}
            setInputMode={setInputMode}
            loading={analysis.loading}
            onSubmit={handleAnalyze}
          />
        )}

        {activeTab === "analysis" && analysis.results && (
          <AnalysisResults results={analysis.results} setResults={(res) => setAnalysis({ ...analysis, results: res })} formData={formData} />
        )}

        {activeTab === "weather" && (
          <ResultCard title={t("weather_title")} icon={<Cloud size={20} />}>
            <button onClick={fetchWeather} disabled={weather.loading}
              className="btn-green px-4 py-2 rounded-lg font-medium disabled:bg-gray-400 flex items-center gap-2 mb-4">
              {weather.loading ? <Loader size={16} text="Checking..." /> : <><CloudRain size={16} /> Check Weather</>}
            </button>
            {weather.data && (
              <div className={`p-4 rounded-xl border-2 ${weather.data.alert ? "bg-orange-50 border-orange-300" : "bg-green-50 border-green-300"}`}>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">{weather.data.rain_expected ? "🌧️" : weather.data.temp_c > 35 ? "☀️" : "🌤️"}</span>
                  <div>
                    <p className="font-bold text-lg">{weather.data.temp_c}°C — {weather.data.description}</p>
                    <p className="text-sm text-gray-600">Humidity: {weather.data.humidity}%</p>
                  </div>
                </div>
                <p className={`font-semibold ${weather.data.alert ? "text-orange-700" : "text-green-700"}`}>{weather.data.message}</p>
              </div>
            )}
          </ResultCard>
        )}

        {activeTab === "prices" && (
          <ResultCard title={t("market_prices")} icon={<IndianRupee size={20} />}>
            <button onClick={fetchPrices} disabled={prices.loading}
              className="btn-green px-4 py-2 rounded-lg font-medium disabled:bg-gray-400 flex items-center gap-2 mb-4">
              {prices.loading ? <Loader size={16} text="Loading..." /> : <><TrendingUp size={16} /> Refresh Prices</>}
            </button>
            {prices.data.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                {prices.data.map((p) => (
                  <div key={p.crop} className="bg-white p-3 rounded-xl border text-center shadow-sm hover:shadow-md transition-shadow">
                    <p className="font-bold text-gray-800">{p.crop}</p>
                    <p className="text-primary-600 text-lg font-bold mt-1">₹{p.price}/{p.unit}</p>
                    <p className="text-xs text-gray-400">{t("market_mandi")}</p>
                  </div>
                ))}
              </div>
            )}
          </ResultCard>
        )}

        {activeTab === "pest" && (
          <ResultCard title={t("pest_title")} icon={<Bug size={20} />}>
            <label className="flex flex-col items-center gap-3 p-6 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-primary-400 transition-colors">
              <Bug size={40} className="text-primary-400" />
              <span className="text-sm text-gray-500">{t("upload_leaf")}</span>
              <input type="file" accept="image/*" onChange={(e) => handlePestDiagnose(e.target.files[0])} hidden />
            </label>
            {pest.loading && <div className="mt-4"><Loader text="Analyzing image..." /></div>}
            {pest.result && (
              <div className="mt-4 p-4 bg-white rounded-xl border shadow-sm">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl">{pest.result.severity === "high" ? "🔴" : pest.result.severity === "moderate" ? "🟡" : "🟢"}</span>
                  <div>
                    <p className="font-bold text-lg">{pest.result.disease}</p>
                    <p className="text-xs text-gray-500">Confidence: {(pest.result.confidence * 100).toFixed(0)}%</p>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <p><span className="font-semibold text-gray-600">{t("disease_name")}:</span> {pest.result.disease}</p>
                  <p><span className="font-semibold text-gray-600">Cause:</span> {pest.result.cause}</p>
                  <p><span className="font-semibold text-gray-600">{t("treatment")}:</span> {pest.result.treatment}</p>
                  <p><span className="font-semibold text-gray-600">{t("severity")}:</span> <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${pest.result.severity === "high" ? "bg-red-100 text-red-700" : pest.result.severity === "moderate" ? "bg-yellow-100 text-yellow-700" : "bg-green-100 text-green-700"}`}>{pest.result.severity.toUpperCase()}</span></p>
                </div>
              </div>
            )}
          </ResultCard>
        )}

        {activeTab === "profit" && (
          <ResultCard title={t("profit_calculator")} icon={<Calculator size={20} />}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="text-sm font-medium text-gray-500 mb-1 block">{t("farm_size")} *</label>
                <input type="number" step="0.5" value={profitForm.farm_size_acres} onChange={(e) => setProfitForm({ ...profitForm, farm_size_acres: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm outline-none focus:border-primary-500" placeholder="e.g. 5" />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500 mb-1 block">{t("crop_type")}</label>
                <select value={profitForm.crop_type} onChange={(e) => setProfitForm({ ...profitForm, crop_type: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm outline-none focus:border-primary-500">
                  {["Rice", "Wheat", "Maize", "Cotton", "Tomato", "Potato", "Soybean", "Groundnut", "Chilli", "Turmeric"].map((c) => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div className="flex items-end">
                <button onClick={calculateProfit} disabled={profit.loading} className="btn-green w-full py-2 rounded-lg font-medium flex items-center justify-center gap-2">
                  {profit.loading ? <Loader size={16} /> : <><Calculator size={16} /> {t("calculate")}</>}
                </button>
              </div>
            </div>

            {profit.result && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                  { label: t("estimated_cost"), value: `₹${profit.result.estimated_cost.toLocaleString()}`, color: "text-red-600" },
                  { label: t("expected_yield"), value: `${profit.result.expected_yield_kg.toLocaleString()} kg`, color: "text-blue-600" },
                  { label: t("expected_revenue"), value: `₹${profit.result.expected_revenue.toLocaleString()}`, color: "text-green-600" },
                  { label: t("estimated_profit"), value: `₹${profit.result.estimated_profit.toLocaleString()}`, color: profit.result.estimated_profit >= 0 ? "text-green-600" : "text-red-600" },
                ].map((item, i) => (
                  <div key={i} className="bg-white p-3 rounded-xl border text-center shadow-sm">
                    <p className="text-xs text-gray-500 mb-1">{item.label}</p>
                    <p className={`text-lg font-bold ${item.color}`}>{item.value}</p>
                  </div>
                ))}
                <div className="col-span-2 md:col-span-4 bg-primary-50 p-3 rounded-xl text-center">
                  <p className="text-sm text-gray-600">{t("roi")}</p>
                  <p className="text-2xl font-bold text-primary-700">{profit.result.roi_percent}%</p>
                </div>
              </div>
            )}
          </ResultCard>
        )}
        </div>

        {/* Sidebar for History */}
        <div className="lg:col-span-1 hidden lg:block h-[calc(100vh-80px)] sticky top-6">
          <HistoryList refreshTrigger={historyRefresh} />
        </div>
        
        {/* Mobile History (shows below main content) */}
        <div className="lg:hidden mt-6">
          <HistoryList refreshTrigger={historyRefresh} />
        </div>
        
      </div>

      <ChatWidget />
    </div>
  );
}
