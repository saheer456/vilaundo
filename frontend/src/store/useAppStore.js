import { create } from 'zustand';
import i18n from '../i18n/i18n';

export const useAppStore = create((set) => ({
  language: localStorage.getItem('language') || 'en',
  district: localStorage.getItem('district') || '',
  category: 'all',
  searchQuery: '',
  theme: localStorage.getItem('theme') || 'light',
  selectedCommodity: null,
  showSubmitModal: false,
  showAlertModal: false,

  setLanguage: (lang) => {
    localStorage.setItem('language', lang);
    i18n.changeLanguage(lang);
    set({ language: lang });
  },
  setDistrict: (dist) => {
    localStorage.setItem('district', dist);
    set({ district: dist });
  },
  setCategory: (cat) => set({ category: cat }),
  setSearchQuery: (q) => set({ searchQuery: q }),
  setTheme: (theme) => {
    localStorage.setItem('theme', theme);
    set({ theme });
  },
  setSelectedCommodity: (item) => set({ selectedCommodity: item }),
  setShowSubmitModal: (show) => set({ showSubmitModal: show }),
  setShowAlertModal: (show) => set({ showAlertModal: show })
}));
