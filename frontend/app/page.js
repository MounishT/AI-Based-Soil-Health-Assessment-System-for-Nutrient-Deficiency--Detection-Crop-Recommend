"use client";

import Link from "next/link";
import { Sprout, TrendingUp, Bug, CloudSun, IndianRupee, ShieldCheck, ArrowRight } from "lucide-react";
import { useAuth } from "../lib/auth-context";

export default function LandingPage() {
  const { user, loading } = useAuth();

  const features = [
    {
      icon: <Sprout className="w-8 h-8 text-green-600" />,
      title: "Soil Nutrient Analysis",
      description: "Get precise insights into Nitrogen, Phosphorus, Potassium, and pH levels using advanced ML models."
    },
    {
      icon: <TrendingUp className="w-8 h-8 text-blue-600" />,
      title: "Crop Recommendation",
      description: "Discover the best crops suited for your specific soil conditions to maximize yield."
    },
    {
      icon: <Bug className="w-8 h-8 text-red-500" />,
      title: "Plant Disease Scanning",
      description: "Upload a picture of a diseased leaf and our AI will instantly diagnose it and suggest treatments."
    },
    {
      icon: <IndianRupee className="w-8 h-8 text-yellow-600" />,
      title: "Market Prices & Profit",
      description: "Stay updated with live Mandi prices and calculate your estimated farming ROI."
    },
    {
      icon: <CloudSun className="w-8 h-8 text-orange-500" />,
      title: "Weather Alerts",
      description: "Receive timely weather forecasts to plan your irrigation and fertilizer applications."
    },
    {
      icon: <ShieldCheck className="w-8 h-8 text-teal-600" />,
      title: "Soil Health History",
      description: "Keep track of all your past soil reports and monitor your farm's health trends over time."
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 md:px-12 py-4 bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="bg-green-600 p-2 rounded-xl">
            <Sprout className="text-white w-6 h-6" />
          </div>
          <span className="font-bold text-xl text-gray-800 tracking-tight">Soil Health AI</span>
        </div>
        <div>
          {!loading && user ? (
            <Link href="/dashboard" className="px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-full shadow-md hover:shadow-lg transition-all duration-300">
              Go to Dashboard
            </Link>
          ) : (
            <Link href="/login" className="px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-full shadow-md hover:shadow-lg transition-all duration-300">
              Sign In
            </Link>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-32 flex flex-col items-center text-center px-4"
        style={{ background: "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)" }}>
        
        {/* Background Decorative Elements */}
        <div className="absolute top-10 left-10 w-64 h-64 bg-green-300/30 rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 right-10 w-80 h-80 bg-blue-300/20 rounded-full blur-3xl"></div>

        <div className="z-10 max-w-4xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 text-green-700 font-medium text-sm mb-4 border border-green-200">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-600"></span>
            </span>
            AI-Powered Agriculture
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold text-gray-900 tracking-tight leading-tight">
            Smart Farming Starts with <br className="hidden md:block"/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-teal-500">
              Healthy Soil
            </span>
          </h1>
          <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Empower your farming decisions with machine learning. Get precise nutrient analysis, crop recommendations, disease diagnosis, and live market insights—all in one place.
          </p>
          <div className="pt-6 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href={user ? "/dashboard" : "/login"} 
              className="px-8 py-4 bg-gray-900 hover:bg-black text-white rounded-full font-bold text-lg shadow-xl hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 flex items-center gap-2 w-full sm:w-auto justify-center">
              Get Started Now <ArrowRight className="w-5 h-5" />
            </Link>
            <a href="#features" 
              className="px-8 py-4 bg-white hover:bg-gray-50 text-gray-800 rounded-full font-bold text-lg shadow-sm border border-gray-200 transition-all duration-300 w-full sm:w-auto text-center">
              Explore Features
            </a>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 md:px-12 bg-white relative z-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Everything You Need to Succeed</h2>
            <p className="text-gray-500 max-w-2xl mx-auto">Our platform combines cutting-edge AI models with agricultural science to provide actionable insights for your farm.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feat, idx) => (
              <div key={idx} className="p-8 rounded-3xl bg-gray-50 border border-gray-100 hover:border-green-200 hover:shadow-xl hover:bg-white transition-all duration-300 group">
                <div className="w-16 h-16 rounded-2xl bg-white shadow-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 border border-gray-100">
                  {feat.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-3">{feat.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feat.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="py-20 px-6 bg-gray-900 text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <h2 className="text-3xl md:text-4xl font-bold text-white">Ready to boost your crop yield?</h2>
          <p className="text-gray-400">Join thousands of farmers making data-driven decisions today.</p>
          <div className="pt-4">
            <Link href={user ? "/dashboard" : "/login"} 
              className="inline-block px-8 py-4 bg-green-500 hover:bg-green-400 text-gray-900 rounded-full font-bold text-lg shadow-lg hover:shadow-green-500/30 transition-all duration-300">
              Access the Dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-950 py-8 text-center text-gray-500 text-sm">
        <p>&copy; {new Date().getFullYear()} Soil Health AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
