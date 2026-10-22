import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import { translations } from "./lib/translations";

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: translations.en },
      hi: { translation: translations.hi },
      kn: { translation: translations.kn },
      te: { translation: translations.te },
    },
    lng: "en",
    fallbackLng: "en",
    interpolation: { escapeValue: false },
  });

export default i18n;
