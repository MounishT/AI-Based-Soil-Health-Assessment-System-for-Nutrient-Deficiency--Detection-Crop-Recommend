import { useRef } from "react";
import { Camera, Upload } from "lucide-react";
import { useTranslation } from "react-i18next";

export default function ImageUploader({
  image,
  setImage,
  imagePreview,
  setImagePreview,
  inputMode,
  setInputMode,
}) {
  const { t } = useTranslation();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const startCamera = async () => {
    setInputMode("camera");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch {
      alert("Camera access denied or unavailable.");
    }
  };

  const captureImage = () => {
    const video = videoRef.current, canvas = canvasRef.current;
    if (video && canvas) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0);
      canvas.toBlob((blob) => {
        const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
        setImage(file);
        setImagePreview(URL.createObjectURL(file));
        video.srcObject?.getTracks().forEach((t) => t.stop());
        video.srcObject = null;
      }, "image/jpeg");
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      alert("Please select a valid image file.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      alert("File size exceeds 5MB limit.");
      return;
    }
    setImage(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const resetImage = () => {
    setImage(null);
    setImagePreview(null);
    setInputMode(null);
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-300 rounded-xl p-4 mb-4 text-center">
      {!image && !inputMode && (
        <div className="flex justify-center gap-3">
          <button type="button" onClick={startCamera} className="flex items-center gap-2 px-4 py-2 bg-white border rounded-lg hover:bg-gray-50 text-sm font-medium shadow-sm transition-all">
            <Camera size={16} /> {t("use_camera")}
          </button>
          <button type="button" onClick={() => setInputMode("upload")} className="flex items-center gap-2 px-4 py-2 bg-white border rounded-lg hover:bg-gray-50 text-sm font-medium shadow-sm transition-all">
            <Upload size={16} /> {t("upload_image")}
          </button>
        </div>
      )}
      {!image && inputMode === "camera" && (
        <div>
          <video ref={videoRef} autoPlay playsInline className="w-full max-w-md mx-auto rounded-lg mb-3" />
          <canvas ref={canvasRef} style={{ display: "none" }} />
          <div className="flex justify-center gap-3">
            <button type="button" onClick={captureImage} className="btn-green px-4 py-2 rounded-lg text-sm font-medium">
              {t("capture")}
            </button>
            <button type="button" onClick={resetImage} className="px-4 py-2 bg-gray-200 rounded-lg text-sm font-medium">
              {t("cancel")}
            </button>
          </div>
        </div>
      )}
      {!image && inputMode === "upload" && (
        <div>
          <label className="flex flex-col items-center gap-2 cursor-pointer">
            <Upload size={32} className="text-primary-500" />
            <span className="text-sm text-gray-500">Click to browse or drop an image</span>
            <input type="file" accept="image/*" onChange={handleFileUpload} hidden />
          </label>
          <button type="button" onClick={resetImage} className="mt-3 px-4 py-2 bg-gray-200 rounded-lg text-sm font-medium">
            {t("cancel")}
          </button>
        </div>
      )}
      {image && (
        <div className="flex flex-col items-center gap-2">
          <img src={imagePreview} alt="Preview" className="max-h-48 rounded-lg shadow" />
          <p className="text-sm text-green-600 font-semibold">✅ {t("image_ready")}: {image.name}</p>
          <button type="button" onClick={resetImage} className="text-sm text-primary-600 hover:underline">
            {t("change_image")}
          </button>
        </div>
      )}
    </div>
  );
}
