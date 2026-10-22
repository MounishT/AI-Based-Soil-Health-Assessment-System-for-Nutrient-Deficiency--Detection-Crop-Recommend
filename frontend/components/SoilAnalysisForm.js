import { Activity, TestTube2, Droplets, Leaf } from "lucide-react";
import { useTranslation } from "react-i18next";
import InputField from "./InputField";
import Loader from "./Loader";
import ImageUploader from "./ImageUploader";

export default function SoilAnalysisForm({
  formData,
  setFormData,
  image,
  setImage,
  imagePreview,
  setImagePreview,
  inputMode,
  setInputMode,
  loading,
  onSubmit,
}) {
  const { t } = useTranslation();

  return (
    <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-lg p-6 mb-6 animate-[fadeIn_0.3s_ease]">
      <h2 className="text-lg font-semibold text-gray-700 mb-4">{t("subtitle")}</h2>
      <form onSubmit={onSubmit}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <InputField
            label={t("n_label")}
            icon={<Leaf size={14} />}
            value={formData.nitrogen}
            onChange={(e) => setFormData({ ...formData, nitrogen: e.target.value })}
          />
          <InputField
            label={t("p_label")}
            icon={<Activity size={14} />}
            value={formData.phosphorus}
            onChange={(e) => setFormData({ ...formData, phosphorus: e.target.value })}
          />
          <InputField
            label={t("k_label")}
            icon={<Droplets size={14} />}
            value={formData.potassium}
            onChange={(e) => setFormData({ ...formData, potassium: e.target.value })}
          />
          <InputField
            label={t("ph_label")}
            icon={<TestTube2 size={14} />}
            step="0.1"
            value={formData.ph}
            onChange={(e) => setFormData({ ...formData, ph: e.target.value })}
          />
        </div>

        <ImageUploader 
          image={image}
          setImage={setImage}
          imagePreview={imagePreview}
          setImagePreview={setImagePreview}
          inputMode={inputMode}
          setInputMode={setInputMode}
        />

        <button type="submit" disabled={loading} className="btn-green w-full py-4 font-bold rounded-xl text-lg transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl relative z-10 mt-2">
          {loading ? <Loader text={t("loading")} /> : t("analyze_btn")}
        </button>
      </form>
    </div>
  );
}

