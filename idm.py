import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
import struct
import importlib.util
import winreg
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import subprocess
import threading
import time
import os
import stat
import datetime
import json
import shutil
import uuid
from pathlib import Path
from urllib import request, error
from enum import Enum, auto
from dataclasses import dataclass, field
from ctypes import windll, byref, sizeof, c_int 
import webbrowser
from tkinter import font

# --- Import for HTTP requests with Cloudflare bypass ---
try:
    import cloudscraper
except ImportError:
    cloudscraper = None
else:
    # استيراد استثناءات محددة من requests التي تستخدمها cloudscraper
    try:
        from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
    except ImportError:
        # في حال لم تكن requests مثبتة بشكل مباشر، سنعتمد على Exception العام
        RequestException = HTTPError = ConnectionError = Timeout = Exception

# --- Import for Image Processing ---
try:
    from PIL import Image, ImageTk, ImageOps
except ImportError:
    PillowAvailable = False
else:
    PillowAvailable = True
import sys # Ensure sys is imported

# --- Import for Desktop Notifications ---
try:
    from win10toast_persist import ToastNotifier
except ImportError:
    ToastNotifier = None # Handle gracefully if not installed

# --- Import for System Tray Icon ---
try:
    import pystray
except ImportError:
    pystray = None

try:
    from tkinterdnd2 import DND_TEXT, TkinterDnD, TkinterDnDWrapper
except ImportError:
    TkinterDnD = None # Handle gracefully


try:
    from ttkthemes import ThemedTk
except ImportError:
    ThemedTk = tk.Tk # Fallback to standard Tk if ttkthemes is not installed


# قفل لتحديث المتغيرات المشتركة بأمان من خيوط متعددة
overall_progress_lock = threading.Lock()

class SplashScreen(tk.Toplevel):
    """
    شاشة بداية تظهر أثناء تحميل التطبيق.
    """
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.overrideredirect(True) # إزالة إطار النافذة

        try:
            # تحميل صورة شاشة البداية
            # تأكد من وجود صورة باسم splash.png في مجلد icons
            splash_image_path = resource_path("icons/splash.png")
            self.splash_image = ImageTk.PhotoImage(Image.open(splash_image_path))
            
            img_width = self.splash_image.width()
            img_height = self.splash_image.height()

            # توسيط النافذة على الشاشة
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width // 2) - (img_width // 2)
            y = (screen_height // 2) - (img_height // 2)
            self.geometry(f'{img_width}x{img_height}+{x}+{y}')

            # عرض الصورة والنص
            canvas = tk.Canvas(self, width=img_width, height=img_height, highlightthickness=0)
            canvas.pack()
            canvas.create_image(0, 0, anchor=tk.NW, image=self.splash_image)
            
            loading_font = font.Font(family="Tahoma", size=10)
            canvas.create_text(
                img_width / 2, 
                img_height - 30, 
                text="...جاري تحميل البرنامج", 
                fill="white", # افترض أن الخلفية داكنة
                font=loading_font
            )
        except Exception as e:
            # في حال عدم وجود الصورة، اعرض نافذة بسيطة
            self.geometry("300x100")
            ttk.Label(self, text="...جاري التحميل", font=("Tahoma", 14)).pack(expand=True)

        self.update() # إجبار النافذة على الظهور فورًا

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".") # For development
    return os.path.join(base_path, relative_path)

DOWNLOAD_SESSION_FILE = "downloads.json"
SETTINGS_FILE = "settings.json"

# --- معلومات الإصدار والتحديث ---
APP_VERSION = "1.1" # قم بتحديث هذا الرقم مع كل إصدار جديد
# !! هام: استبدل هذا الرابط برابط ملف version.json الفعلي الخاص بك على GitHub
UPDATE_URL = "https://raw.githubusercontent.com/legionr4/-Advanced-Download-Manager/main/version.json"

class LocalizationManager:
    """Manages translations for the application."""
    def __init__(self, language='ar'):
        self.translations = {
            'ar': {
                # Main Window & Toolbar
                'window_title': "مدير التحميل",
                'settings': "الإعدادات",
                'downloads_folder': "مجلد التحميلات",
                'about': "حول البرنامج",
                'theme': "السمة",
                'add_url': "إضافة رابط",
                'resume_from_file': "استئناف من ملف",
                'file_menu': "ملف",
                'exit': "خروج",
                'check_for_updates': "التحقق من وجود تحديثات",
                'start': "بدء",
                'pause': "إيقاف مؤقت",
                'cancel': "إلغاء",
                'remove': "إزالة",
                'resume': "استئناف",
                'retry_now': "إعادة المحاولة الآن",
                'start_now': "بدء الآن",
                'ready_to_download': "جاهز للتحميل.",
                # Treeview
                'file': "الملف", 'size': "الحجم", 'progress': "التقدم", 'speed': "السرعة",
                'time_left': "الوقت المتبقي", 'status': "الحالة",
                # Context Menu
                'show_part_details': "إظهار تفاصيل الأجزاء",
                'open_file_location': "فتح مجلد الملف",
                'copy_download_link': "نسخ رابط التحميل",
                'reset_download': "إعادة تعيين التحميل",
                'cleanup_temp_files': "تنظيف الملفات المؤقتة",
                'delete_file_from_disk': "حذف الملف من القرص",
                'images_category': "الصور",
                # Categories
                'all_downloads': "كل التحميلات",
                'uncategorized': "غير مصنف",
                'video': "فيديو",
                'audio': "صوتيات",
                'software': "برامج",
                'documents': "مستندات",
                'compressed': "ملفات مضغوطة",
                # Statuses & Messages
                'no_results_found': "لا توجد نتائج مطابقة",
                'search': "بحث:",
                'refresh_download_link': "تحديث رابط التحميل",
                'paste_new_link_prompt': "بعد تحديث الصفحة في متصفحك، الصق رابط التحميل الجديد هنا:",
                'ready': "جاهز", 'getting_info': "جاري الحصول على المعلومات...", 'downloading': "جاري التحميل...",
                'paused_status': "متوقف مؤقتًا", 'cancelling': "جاري الإلغاء...", 'error_retrying': "خطأ، إعادة محاولة...",
                'cancelled': "تم الإلغاء", 'combining': "جاري التجميع...", 'complete': "مكتمل",
                'permanent_error': "خطأ دائم", 'cannot_determine_size': "لا يمكن تحديد الحجم",
                'scheduled_for': "مجدول إلى: {time}", 'unknown': "غير معروف",
                # Message Boxes
                'confirm_exit_title': "تأكيد الخروج",
                'confirm_exit_msg': "هل أنت متأكد من أنك تريد الخروج؟",
                'confirm_exit_active_msg': "هناك تحميلات نشطة. سيتم إيقافها مؤقتًا واستئنافها عند التشغيل التالي.\nهل أنت متأكد من أنك تريد الخروج؟",
                'select_download_first': "الرجاء تحديد تحميل من القائمة أولاً.",
                'information': "معلومة",
                'remove_completed': "إزالة المكتمل",
                'no_completed_downloads': "لا توجد تحميلات مكتملة لإزالتها.",
                'confirm_removal_title': "تأكيد الإزالة",
                'confirm_remove_completed_msg': "هل أنت متأكد من أنك تريد إزالة {count} من التحميلات المكتملة؟",
                'removed_completed_success': "تمت إزالة {count} من التحميلات المكتملة بنجاح.",
                # Update Messages
                'update_available_title': "تحديث متوفر",
                'update_available_message': "يتوفر إصدار جديد ({latest_version})!\n\nملاحظات الإصدار:\n{release_notes}\n\nهل ترغب في التحديث الآن؟",
                'no_update_available_title': "لا توجد تحديثات",
                'no_update_available_message': "أنت تستخدم أحدث إصدار بالفعل.",
                'file_not_found_on_disk': "الملف غير موجود على القرص.",
                'confirm_delete_file_title': "تأكيد حذف الملف",
                'confirm_delete_file_message': "هل أنت متأكد من أنك تريد حذف الملف '{filename}' نهائيًا من القرص؟\nلا يمكن التراجع عن هذا الإجراء.",
                'confirm_reset_title': "تأكيد إعادة التعيين",
                'confirm_reset_message': "هل تريد بالتأكيد إعادة تعيين هذا التحميل؟\nسيتم حذف جميع الأجزاء التي تم تنزيلها والبدء من الصفر.",
                # Add/Resume Dialog
                'add_new_download': "إضافة تحميل جديد",
                'file_url': "رابط الملف (URL):",
                'save_in': "حفظ في:",
                'browse': "تصفح...",
                'num_segments': "عدد الأجزاء (1-16):",
                'schedule_download': "جدولة التحميل",
                'scheduling_settings': "إعدادات الجدولة",
                'date': "التاريخ:",
                'time': "الوقت:",
                'start_download_btn': "بدء التحميل",
                'error_title': "خطأ",
                'enter_url_error': "الرجاء إدخال رابط.",
                'select_save_path_error': "الرجاء تحديد مسار الحفظ.",
                'duplicate_download_warning': "هذا الرابط موجود بالفعل في قائمة التحميلات.",
                'select_file_to_resume': "اختر ملفًا لاستئناف تحميله",
                'download_already_in_list': "هذا التحميل موجود بالفعل في القائمة.",
                'no_parts_found': "لم يتم العثور على ملفات تحميل جزئية لهذا الملف. لا يمكن الاستئناف.",
                'resume_title': "استئناف التحميل",
                'resume_prompt': "لاستئناف التحميل، الرجاء إدخال الرابط الأصلي للملف:",
                # Settings
                'server_settings': "إعدادات الخادم",
                'server_port': "رقم المنفذ (يتطلب إعادة التشغيل)",
                'port_restart_warning': "تغيير المنفذ يتطلب إعادة تشغيل البرنامج لتفعيله.",
                'language': "اللغة",
                'english': "English",
                'auto_resume_on_startup': "بدء التحميلات غير المكتملة تلقائيًا عند بدء التشغيل",
                'startup_options': "إعدادات بدء التشغيل",
                'run_on_startup': "تشغيل البرنامج عند بدء تشغيل ويندوز",
                'french': "الفرنسية",
                'spanish': "الإسبانية",
                'status_colors': "ألوان الحالة",
                'ok': "موافق",
                'apply': "تطبيق",
                'general_tab': "عام",
                'connection_tab': "الاتصال",
                'appearance_tab': "المظهر",
                'speed_limit_tab': "السرعة",
                'enable_speed_limit': "تفعيل تحديد السرعة",
                'max_speed': "السرعة القصوى:",
                'kb_s': "كيلوبايت/ث", 'mb_s': "ميجابايت/ث",
                'default_category_for_unknown': "الفئة الافتراضية للملفات غير المعروفة",
                'default_category_desc': "اختر الفئة التي سيتم تعيينها تلقائيًا للملفات التي لا يتطابق امتدادها مع أي فئة محددة.",
                'browser_integration_settings': "تكامل المتصفح",
                'general_ui_colors': "ألوان الواجهة العامة",
                'title_bar_bg': "اللون المميز للإطارات (يتطلب إعادة التشغيل)",
                'downloads_tab': "التحميلات",
                'enable_instant_search': "تفعيل البحث الفوري (يحسن الأداء)",
                'max_concurrent_downloads': "الحد الأقصى للتحميلات المتزامنة:",
                'browser_integration_desc': "لتمكين أو تعطيل اعتراض التحميل التلقائي من المتصفح، استخدم صفحة إعدادات الإضافة.",
                'open_browser_settings_btn': "فتح إعدادات إضافة المتصفح",
                'reset_colors_to_default': "إعادة الألوان للافتراضي",
                'default_save_folder': "مجلد الحفظ الافتراضي",
                'change_folder': "تغيير...",
            },
            'en': {
                # Main Window & Toolbar
                'window_title': "Download Manager",
                'settings': "Settings",
                'downloads_folder': "Downloads Folder",
                'about': "About",
                'theme': "Theme",
                'add_url': "Add URL",
                'resume_from_file': "Resume from File",
                'file_menu': "File",
                'exit': "Exit",
                'check_for_updates': "Check for Updates",
                'start': "Start",
                'pause': "Pause",
                'cancel': "Cancel",
                'remove': "Remove",
                'resume': "Resume",
                'retry_now': "Retry Now",
                'start_now': "Start Now",
                'ready_to_download': "Ready to download.",
                # Treeview
                'file': "File", 'size': "Size", 'progress': "Progress", 'speed': "Speed",
                'time_left': "Time Left", 'status': "Status",
                # Context Menu
                'show_part_details': "Show Part Details",
                'open_file_location': "Open File Location",
                'copy_download_link': "Copy Download Link",
                'reset_download': "Reset Download",
                'cleanup_temp_files': "Cleanup Temporary Files",
                'delete_file_from_disk': "Delete File From Disk",
                'images_category': "Images",
                # Categories
                'all_downloads': "All Downloads",
                'uncategorized': "Uncategorized",
                'video': "Video",
                'audio': "Audio",
                'software': "Software",
                'documents': "Documents",
                'compressed': "Compressed",
                # Statuses & Messages
                'no_results_found': "No matching results found",
                'search': "Search:",
                'refresh_download_link': "Refresh Download Link",
                'paste_new_link_prompt': "After refreshing the page in your browser, paste the new download link here:",
                'ready': "Ready", 'getting_info': "Getting info...", 'downloading': "Downloading...",
                'paused_status': "Paused", 'cancelling': "Cancelling...", 'error_retrying': "Error, retrying...",
                'cancelled': "Cancelled", 'combining': "Combining...", 'complete': "Complete",
                'permanent_error': "Permanent Error", 'cannot_determine_size': "Cannot determine size",
                'scheduled_for': "Scheduled for: {time}", 'unknown': "Unknown",
                # Message Boxes
                'confirm_exit_title': "Confirm Exit",
                'confirm_exit_msg': "Are you sure you want to exit?",
                'confirm_exit_active_msg': "There are active downloads. They will be paused and resumed on next launch.\nAre you sure you want to exit?",
                'select_download_first': "Please select a download from the list first.",
                'information': "Information",
                'remove_completed': "Remove Completed",
                'no_completed_downloads': "No completed downloads to remove.",
                'confirm_removal_title': "Confirm Removal",
                'confirm_remove_completed_msg': "Are you sure you want to remove {count} completed downloads?",
                'removed_completed_success': "Successfully removed {count} completed downloads.",
                # Update Messages
                'update_available_title': "Update Available",
                'update_available_message': "A new version ({latest_version}) is available!\n\nRelease Notes:\n{release_notes}\n\nWould you like to update now?",
                'no_update_available_title': "No Updates Available",
                'no_update_available_message': "You are already using the latest version.",
                'file_not_found_on_disk': "The file was not found on disk.",
                'confirm_delete_file_title': "Confirm File Deletion",
                'confirm_delete_file_message': "Are you sure you want to permanently delete the file '{filename}' from your disk?\nThis action cannot be undone.",
                'confirm_reset_title': "Confirm Reset",
                'confirm_reset_message': "Are you sure you want to reset this download?\nAll downloaded parts will be deleted and it will start from scratch.",
                # Add/Resume Dialog
                'add_new_download': "Add New Download",
                'file_url': "File URL:",
                'save_in': "Save in:",
                'browse': "Browse...",
                'num_segments': "Number of parts (1-16):",
                'schedule_download': "Schedule Download",
                'scheduling_settings': "Scheduling Settings",
                'date': "Date:",
                'time': "Time:",
                'start_download_btn': "Start Download",
                'error_title': "Error",
                'enter_url_error': "Please enter a URL.",
                'select_save_path_error': "Please select a save path.",
                'duplicate_download_warning': "This URL already exists in the download list.",
                'select_file_to_resume': "Select a file to resume",
                'download_already_in_list': "This download is already in the list.",
                'no_parts_found': "No partial download files found for this file. Cannot resume.",
                'resume_title': "Resume Download",
                'resume_prompt': "To resume the download, please enter the original file URL:",
                # Settings
                'server_settings': "Server Settings",
                'server_port': "Port Number (Restart Required)",
                'port_restart_warning': "Changing the port requires restarting the application to take effect.",
                'language': "Language",
                'english': "English",
                'auto_resume_on_startup': "Automatically resume incomplete downloads on startup",
                'startup_options': "Startup Options",
                'run_on_startup': "Run on Windows startup",
                'french': "French",
                'spanish': "Spanish",
                'status_colors': "Status Colors",
                'ok': "OK",
                'apply': "Apply",
                'general_tab': "General",
                'connection_tab': "Connection",
                'appearance_tab': "Appearance",
                'speed_limit_tab': "Speed Limit",
                'enable_speed_limit': "Enable speed limit",
                'max_speed': "Maximum speed:",
                'kb_s': "KB/s", 'mb_s': "MB/s",
                'default_category_for_unknown': "Default category for unknown files",
                'default_category_desc': "Choose the category to be automatically assigned to files whose extension does not match any defined category.",
                'browser_integration_settings': "Browser Integration",
                'general_ui_colors': "General UI Colors",
                'title_bar_bg': "Frame Accent Color (Restart required)",
                'downloads_tab': "Downloads",
                'enable_instant_search': "Enable instant search (improves performance)",
                'max_concurrent_downloads': "Max concurrent downloads:",
                'browser_integration_desc': "To enable or disable automatic download interception from the browser, use the extension's own settings page.",
                'open_browser_settings_btn': "Open Browser Extension Settings",
                'reset_colors_to_default': "Reset Colors to Default",
                'default_save_folder': "Default Save Folder",
                'change_folder': "Change...",
            },
            'fr': {
                # Main Window & Toolbar
                'window_title': "Gestionnaire de téléchargement",
                'settings': "Paramètres",
                'downloads_folder': "Dossier de téléchargements",
                'about': "À propos",
                'theme': "Thème",
                'add_url': "Ajouter URL",
                'resume_from_file': "Reprendre depuis un fichier",
                'file_menu': "Fichier",
                'exit': "Quitter",
                'check_for_updates': "Vérifier les mises à jour",
                'start': "Démarrer",
                'pause': "Pause",
                'cancel': "Annuler",
                'remove': "Supprimer",
                'resume': "Reprendre",
                'retry_now': "Réessayer maintenant",
                'start_now': "Démarrer maintenant",
                'ready_to_download': "Prêt à télécharger.",
                # Treeview
                'file': "Fichier", 'size': "Taille", 'progress': "Progression", 'speed': "Vitesse",
                'time_left': "Temps restant", 'status': "Statut",
                # Context Menu
                'show_part_details': "Afficher les détails des parties",
                'refresh_download_link': "Actualiser le lien",
                'open_file_location': "Ouvrir l'emplacement du fichier",
                'copy_download_link': "Copier le lien",
                'reset_download': "Réinitialiser le téléchargement",
                'cleanup_temp_files': "Nettoyer les fichiers temporaires",
                'delete_file_from_disk': "Supprimer le fichier du disque",
                'images_category': "Images",
                # Categories
                'all_downloads': "Tous les téléchargements",
                'uncategorized': "Non classé",
                'video': "Vidéo",
                'audio': "Audio",
                'software': "Logiciels",
                'documents': "Documents",
                'compressed': "Compressé",
                # Statuses & Messages
                'no_results_found': "Aucun résultat correspondant",
                'search': "Rechercher:",
                'paste_new_link_prompt': "Apr\u00e8s avoir actualis\u00e9 la page dans votre navigateur, collez le nouveau lien de t\u00e9l\u00e9chargement ici :",
                'ready': "Prêt", 'getting_info': "Obtention des informations...", 'downloading': "Téléchargement...",
                'paused_status': "En pause", 'cancelling': "Annulation...", 'error_retrying': "Erreur, nouvelle tentative...",
                'cancelled': "Annulé", 'combining': "Combinaison...", 'complete': "Terminé",
                'permanent_error': "Erreur permanente", 'cannot_determine_size': "Taille indéterminable",
                'scheduled_for': "Prévu pour : {time}", 'unknown': "Inconnu",
                # Message Boxes
                'confirm_exit_title': "Confirmer la sortie",
                'confirm_exit_msg': "Êtes-vous sûr de vouloir quitter ?",
                'confirm_exit_active_msg': "Des téléchargements sont actifs. Ils seront mis en pause.\nÊtes-vous sûr de vouloir quitter ?",
                'select_download_first': "Veuillez d'abord sélectionner un téléchargement.",
                'information': "Information",
                'remove_completed': "Supprimer les terminés",
                'no_completed_downloads': "Aucun téléchargement terminé à supprimer.",
                'confirm_removal_title': "Confirmer la suppression",
                'confirm_remove_completed_msg': "Êtes-vous sûr de vouloir supprimer {count} téléchargements terminés ?",
                'removed_completed_success': "Suppression de {count} téléchargements terminés réussie.",
                # Update Messages
                'update_available_title': "Mise à jour disponible",
                'update_available_message': "Une nouvelle version ({latest_version}) est disponible !\n\nNotes de version :\n{release_notes}\n\nSouhaitez-vous mettre à jour maintenant ?",
                'no_update_available_title': "Aucune mise à jour",
                'no_update_available_message': "Vous utilisez déjà la dernière version.",
                'file_not_found_on_disk': "Le fichier n'a pas été trouvé sur le disque.",
                'confirm_delete_file_title': "Confirmer la suppression du fichier",
                'confirm_delete_file_message': "Êtes-vous sûr de vouloir supprimer définitivement le fichier '{filename}' de votre disque ?\nCette action est irréversible.",
                'confirm_reset_title': "Confirmer la réinitialisation",
                'confirm_reset_message': "Êtes-vous sûr de vouloir réinitialiser ce téléchargement ?\nToutes les parties téléchargées seront supprimées et le téléchargement recommencera à zéro.",
                # Add/Resume Dialog
                'add_new_download': "Ajouter un nouveau téléchargement",
                'file_url': "URL du fichier :", 'save_in': "Enregistrer dans :", 'browse': "Parcourir...",
                'num_segments': "Nombre de parties (1-16) :", 'schedule_download': "Planifier le téléchargement",
                'scheduling_settings': "Paramètres de planification", 'date': "Date :", 'time': "Heure :",
                'start_download_btn': "Démarrer le téléchargement",
                'error_title': "Erreur", 'enter_url_error': "Veuillez entrer une URL.",
                'select_save_path_error': "Veuillez sélectionner un chemin de sauvegarde.",
                'duplicate_download_warning': "Cette URL existe déjà dans la liste.",
                'select_file_to_resume': "Sélectionnez un fichier à reprendre",
                'download_already_in_list': "Ce téléchargement est déjà dans la liste.",
                'no_parts_found': "Aucun fichier de téléchargement partiel trouvé. Reprise impossible.",
                'resume_title': "Reprendre le téléchargement",
                'resume_prompt': "Pour reprendre le téléchargement, veuillez entrer l'URL d'origine du fichier :",
                # Settings
                'server_settings': "Paramètres du serveur",
                'server_port': "Numéro de port (redémarrage requis)",
                'port_restart_warning': "Le changement de port nécessite un redémarrage de l'application pour prendre effet.",
                'auto_resume_on_startup': "Reprendre automatiquement les téléchargements au démarrage",
                'startup_options': "Options de d\u00e9marrage",
                'run_on_startup': "Lancer au d\u00e9marrage de Windows",
                'status_colors': "Couleurs de statut", 'ok': "OK", 'apply': "Appliquer",
                'general_tab': "Général",
                'connection_tab': "Connexion",
                'appearance_tab': "Apparence",
                'speed_limit_tab': "Vitesse",
                'enable_speed_limit': "Activer la limitation de vitesse",
                'max_speed': "Vitesse maximale :",
                'kb_s': "Ko/s", 'mb_s': "Mo/s",
                'default_category_for_unknown': "Catégorie par défaut pour les fichiers inconnus",
                'default_category_desc': "Choisissez la catégorie à attribuer automatiquement aux fichiers dont l'extension ne correspond à aucune catégorie définie.",
                'browser_integration_settings': "Intégration du navigateur",
                'general_ui_colors': "Couleurs de l'interface utilisateur",
                'title_bar_bg': "Couleur d'accentuation des cadres (redémarrage requis)",
                'downloads_tab': "Téléchargements",
                'enable_instant_search': "Activer la recherche instantanée (améliore les performances)",
                'max_concurrent_downloads': "Téléchargements simultanés max :",
                'browser_integration_desc': "Pour activer ou désactiver l'interception automatique des téléchargements, utilisez la page des paramètres de l'extension.",
                'open_browser_settings_btn': "Ouvrir les paramètres de l'extension",
                'reset_colors_to_default': "Réinitialiser les couleurs par défaut",
                'default_save_folder': "Dossier de sauvegarde par défaut",
                'change_folder': "Changer...",
            },
            'es': {
                # Main Window & Toolbar
                'window_title': "Gestor de Descargas",
                'settings': "Configuración",
                'downloads_folder': "Carpeta de Descargas",
                'about': "Acerca de",
                'theme': "Tema",
                'add_url': "Añadir URL",
                'resume_from_file': "Reanudar desde archivo",
                'file_menu': "Archivo",
                'exit': "Salir",
                'check_for_updates': "Buscar actualizaciones",
                'start': "Iniciar", 'pause': "Pausar", 'cancel': "Cancelar", 'remove': "Eliminar",
                'resume': "Reanudar", 'retry_now': "Reintentar ahora", 'start_now': "Iniciar ahora",
                'ready_to_download': "Listo para descargar.",
                # Treeview
                'file': "Archivo", 'size': "Tamaño", 'progress': "Progreso", 'speed': "Velocidad",
                'time_left': "Tiempo restante", 'status': "Estado",
                # Context Menu
                'show_part_details': "Mostrar detalles de las partes", 'open_file_location': "Abrir ubicación",
                'refresh_download_link': "Actualizar enlace",
                'copy_download_link': "Copiar enlace", 'reset_download': "Reiniciar descarga",
                'cleanup_temp_files': "Limpiar archivos temporales",
                # Statuses & Messages
                'images_category': "Imágenes",
                'delete_file_from_disk': "Eliminar archivo del disco",
                # Categories
                'all_downloads': "Todas las descargas",
                'uncategorized': "Sin categoría",
                'video': "Video",
                'audio': "Audio",
                'software': "Software",
                'documents': "Documentos",
                'compressed': "Comprimido",
                'no_results_found': "No se encontraron resultados coincidentes",
                'search': "Buscar:",
                'ready': "Listo", 'getting_info': "Obteniendo información...", 'downloading': "Descargando...",
                'paste_new_link_prompt': "Despu\u00e9s de actualizar la p\u00e1gina en su navegador, pegue el nuevo enlace de descarga aqu\u00ed:",
                'paused_status': "En pausa", 'cancelling': "Cancelando...", 'error_retrying': "Error, reintentando...",
                'cancelled': "Cancelado", 'combining': "Combinando...", 'complete': "Completado",
                'permanent_error': "Error permanente", 'cannot_determine_size': "No se puede determinar el tamaño",
                'scheduled_for': "Programado para: {time}", 'unknown': "Desconocido",
                # Message Boxes
                'confirm_exit_title': "Confirmar Salida", 'confirm_exit_msg': "¿Está seguro de que desea salir?",
                'confirm_exit_active_msg': "Hay descargas activas. Se pausarán.\n¿Está seguro de que desea salir?",
                'select_download_first': "Por favor, seleccione primero una descarga.", 'information': "Información",
                'remove_completed': "Eliminar completados",
                'no_completed_downloads': "No hay descargas completadas para eliminar.",
                'confirm_removal_title': "Confirmar eliminación",
                'confirm_remove_completed_msg': "¿Está seguro de que desea eliminar {count} descargas completadas?",
                'removed_completed_success': "Se eliminaron {count} descargas completadas con éxito.",
                # Update Messages
                'update_available_title': "Actualización Disponible",
                'update_available_message': "¡Una nueva versión ({latest_version}) está disponible!\n\nNotas de la versión:\n{release_notes}\n\n¿Desea actualizar ahora?",
                'no_update_available_title': "No hay actualizaciones",
                'no_update_available_message': "Ya está utilizando la última versión.",
                'file_not_found_on_disk': "El archivo no se encontró en el disco.",
                'confirm_delete_file_title': "Confirmar eliminación de archivo",
                'confirm_delete_file_message': "¿Está seguro de que desea eliminar permanentemente el archivo '{filename}' de su disco?\nEsta acción no se puede deshacer.",
                'confirm_reset_title': "Confirmar Reinicio",
                'confirm_reset_message': "¿Está seguro de que desea reiniciar esta descarga?\nSe eliminarán todas las partes descargadas y se comenzará desde cero.",
                # Add/Resume Dialog
                'add_new_download': "Añadir Nueva Descarga", 'file_url': "URL del archivo:", 'save_in': "Guardar en:",
                'browse': "Examinar...", 'num_segments': "Número de partes (1-16):", 'schedule_download': "Programar descarga",
                'scheduling_settings': "Ajustes de programación", 'date': "Fecha:", 'time': "Hora:",
                'start_download_btn': "Iniciar Descarga", 'error_title': "Error", 'enter_url_error': "Por favor, introduzca una URL.",
                'select_save_path_error': "Por favor, seleccione una ruta de guardado.",
                'duplicate_download_warning': "Esta URL ya existe en la lista.",
                'select_file_to_resume': "Seleccione un archivo para reanudar",
                'download_already_in_list': "Esta descarga ya está en la lista.",
                'no_parts_found': "No se encontraron archivos de descarga parcial. No se puede reanudar.",
                'resume_title': "Reanudar Descarga",
                'resume_prompt': "Para reanudar la descarga, por favor ingrese la URL original del archivo:",
                # Settings
                'server_settings': "Configuración del Servidor",
                'server_port': "Número de Puerto (Requiere Reinicio)",
                'port_restart_warning': "Cambiar el puerto requiere reiniciar la aplicación para que surta efecto.",
                'auto_resume_on_startup': "Reanudar descargas automáticamente al iniciar",
                'startup_options': "Opciones de Inicio",
                'run_on_startup': "Ejecutar al iniciar Windows",
                'status_colors': "Colores de estado", 'ok': "Aceptar", 'apply': "Aplicar",
                'general_tab': "General",
                'connection_tab': "Conexión",
                'appearance_tab': "Apariencia",
                'speed_limit_tab': "Velocidad",
                'enable_speed_limit': "Habilitar límite de velocidad",
                'max_speed': "Velocidad máxima:",
                'kb_s': "KB/s", 'mb_s': "MB/s",
                'default_category_for_unknown': "Categoría predeterminada para archivos desconocidos",
                'default_category_desc': "Elija la categoría que se asignará automáticamente a los archivos cuya extensión no coincida con ninguna categoría definida.",
                'browser_integration_settings': "Integración del Navegador",
                'general_ui_colors': "Colores de la interfaz de usuario",
                'title_bar_bg': "Color de acento del marco (se requiere reinicio)",
                'downloads_tab': "Descargas",
                'enable_instant_search': "Habilitar búsqueda instantánea (mejora el rendimiento)",
                'max_concurrent_downloads': "Máx. descargas simultáneas:",
                'browser_integration_desc': "Para habilitar o deshabilitar la intercepción automática de descargas, utilice la página de configuración de la extensión.",
                'open_browser_settings_btn': "Abrir Configuración de la Extensión",
                'reset_colors_to_default': "Restablecer colores predeterminados",
                'default_save_folder': "Carpeta de guardado predeterminada",
                'change_folder': "Cambiar...",
            },
        }
        self.set_language(language)

    def set_language(self, language):
        """Sets the current language."""
        self.language = language if language in self.translations else 'ar'

    def get_translator(self):
        """Returns a function to get a translated string by key."""
        def translate(key, **kwargs):
            return self.translations[self.language].get(key, key).format(**kwargs)
        return translate

class DownloadState(Enum):
    """Defines the possible states of a download item."""
    IDLE = auto()           # جاهز للبدء، لم يبدأ بعد
    GETTING_INFO = auto()   # جاري الحصول على معلومات الملف (الحجم، إلخ)
    DOWNLOADING = auto()    # التحميل نشط
    PAUSED = auto()         # متوقف مؤقتًا من قبل المستخدم
    COMBINING = auto()      # جاري دمج الأجزاء
    COMPLETE = auto()       # اكتمل بنجاح
    CANCELLING = auto()     # في طور الإلغاء
    CANCELLED = auto()      # تم إلغاؤه
    ERROR_RETRYING = auto() # خطأ مؤقت، سيتم إعادة المحاولة
    PERMANENT_ERROR = auto()# خطأ دائم لا يمكن التعافي منه
    SCHEDULED = auto()      # مجدول لوقت لاحق

@dataclass
class SegmentData:
    """Stores all data related to a single download segment."""
    index: int
    thread: threading.Thread = None
    filename: str = ""
    total_size: int = 0
    downloaded_size: int = 0

class DownloadItem:
    """فئة لتغليف كل ما يتعلق بمهمة تحميل واحدة."""
    def __init__(self, url, save_location, app_instance):
        self.id = str(uuid.uuid4())
        self.url = url
        self.category = 'uncategorized' # الفئة الافتراضية
        self.save_location = save_location
        self.app = app_instance  # مرجع للتطبيق الرئيسي للوصول إلى master.after
        self.cookies = None      # لتخزين الكوكيز

        # --- متغيرات الحالة والتقدم ---
        self._is_dirty = True    # علم لتحديد ما إذا كان يجب تحديث الواجهة
        self._state = DownloadState.IDLE
        self._status_text = "Ready" # نص الحالة المعروض للمستخدم
        self._total_size = 0
        self._downloaded_size = 0
        self._speed = 0
        self._time_left = float('inf')
        self._scheduled_time = None
        self.error_message = None # لتخزين رسالة الخطأ

        # --- متغيرات التحميل متعدد الأجزاء ---
        self.num_segments = 8  # العدد الافتراضي للأجزاء
        self.segments: list[SegmentData] = []

        # --- أحداث التزامن للتحكم في الخيوط ---
        self.pause_event = threading.Event()
        self.pause_event.set()  # ابدأ في حالة "عدم التوقف"
        self.cancel_event = threading.Event()
        self.segment_error_event = threading.Event()
        self.permanent_error_event = threading.Event()

        # --- مراجع ومؤقتات ---
        self._retry_timer = None
        self.treeview_item = None # مرجع لعنصر Treeview
        self.details_window = None # مرجع لنافذة التفاصيل
        self.mini_progress_window = None # مرجع لنافذة التقدم المصغرة

    def reset(self, reset_size=True):
        """Resets the download item to its initial state, ready for a new attempt."""
        self.state = DownloadState.IDLE
        self.category = self.category # Keep category on reset
        self.status_text = self.app._('ready')
        if reset_size:
            self.downloaded_size = 0
            for seg in self.segments:
                seg.downloaded_size = 0
        self.speed = 0
        self.time_left = float('inf')
        self.scheduled_time = None
        self.error_message = None
        
        # Reset events
        self.cancel_event.clear()
        self.segment_error_event.clear()
        self.permanent_error_event.clear()
        self.pause_event.set()

    @property
    def temp_dir(self):
        """Returns the dedicated temporary directory path for this download item."""
        return f"{self.save_location}.idm-parts"

    @property
    def state(self): return self._state
    @state.setter
    def state(self, value):
        if self._state != value:
            self._state = value
            self._is_dirty = True

    @property
    def status_text(self): return self._status_text
    @status_text.setter
    def status_text(self, value):
        if self._status_text != value: self._status_text = value; self._is_dirty = True

    @property
    def total_size(self): return self._total_size
    @total_size.setter
    def total_size(self, value):
        if self._total_size != value: self._total_size = value; self._is_dirty = True

    @property
    def downloaded_size(self): return self._downloaded_size
    @downloaded_size.setter
    def downloaded_size(self, value):
        if self._downloaded_size != value:
            self._downloaded_size = value
            self._is_dirty = True

    @property
    def speed(self): return self._speed
    @speed.setter
    def speed(self, value):
        # التحديث فقط إذا كان التغيير كبيرًا بما يكفي لتجنب الارتعاش
        if abs(self._speed - value) > 1024: # تغيير أكبر من 1 كيلوبايت
            self._speed = value
            self._is_dirty = True

    @property
    def time_left(self): return self._time_left
    @time_left.setter
    def time_left(self, value):
        if abs(self._time_left - value) > 1: # تغيير أكبر من ثانية واحدة
            self._time_left = value
            self._is_dirty = True

    @property
    def scheduled_time(self): return self._scheduled_time
    @scheduled_time.setter
    def scheduled_time(self, value):
        if self._scheduled_time != value: self._scheduled_time = value; self._is_dirty = True
class SpeedLimiter:
    """
    A thread-safe speed limiter using a token bucket algorithm.
    This ensures that the total download speed across all threads does not exceed the set limit.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.bucket = 0
        self.limit_bps = 0  # Limit in Bytes per second
        self.bucket_capacity = 1024 * 1024  # Default 1MB burst capacity
        self.last_fill_time = time.time()

    def set_limit(self, limit_value, unit):
        """Sets the speed limit. limit_value=0 disables the limit."""
        with self.lock:
            if limit_value > 0:
                if unit == 'mb_s':
                    self.limit_bps = limit_value * 1024 * 1024
                else: # Default to KB/s
                    self.limit_bps = limit_value * 1024
                # Set bucket capacity to be able to burst a bit, e.g., 1 second worth of data
                self.bucket_capacity = self.limit_bps
            else:
                self.limit_bps = 0
            self.bucket = 0 # Reset bucket on limit change

    def _fill_bucket(self):
        """Internal method to add tokens to the bucket based on elapsed time."""
        if self.limit_bps <= 0:
            return
        now = time.time()
        elapsed = now - self.last_fill_time
        tokens_to_add = elapsed * self.limit_bps
        self.bucket = min(self.bucket_capacity, self.bucket + tokens_to_add)
        self.last_fill_time = now

    def consume(self, amount):
        """Consumes 'amount' of bytes, blocking if necessary to maintain the speed limit."""
        if self.limit_bps <= 0 or amount <= 0:
            return # No limit, do nothing

        with self.lock:
            self._fill_bucket()
            if amount > self.bucket:
                needed = amount - self.bucket
                wait_time = needed / self.limit_bps
                time.sleep(wait_time)
            self.bucket -= amount


class FileDownloaderApp:
    def __init__(self, master, initial_settings=None):
        self.master = master
        self._app_icon = None # To hold a reference to the icon image, preventing garbage collection
        # --- Set Window Icon ---
        icon_file_path = resource_path("icons/icon.ico") # Define before try
        try:
            master.iconbitmap(icon_file_path)
        except tk.TclError as e:
            print(f"Warning: Could not load window icon from '{icon_file_path}'. Error: {e}. File might be missing, not a valid PNG, or an OS/Tkinter issue.")
        master.geometry("1080x700") # زيادة حجم النافذة لاستيعاب أشرطة الأجزاء
        master.resizable(True, True)
        
        # --- نظام الترجمة ---
        self.lang_manager = LocalizationManager(initial_settings.get('language', 'ar'))
        self._ = self.lang_manager.get_translator()

        master.title(self._('window_title'))

        self.toolbar_frame = ttk.Frame(master, padding=(5, 5, 5, 0))
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        # --- File Menu ---
        self.file_menubutton = ttk.Menubutton(self.toolbar_frame, text=self._('file_menu'), style='Toolbutton')
        self.file_menubutton.pack(side=tk.LEFT, padx=2)
        self.file_menu = tk.Menu(self.file_menubutton, tearoff=0)
        self.file_menu.add_command(label=self._('check_for_updates'), command=lambda: self.check_for_updates(on_startup=False))
        self.file_menu.add_separator()
        self.file_menubutton['menu'] = self.file_menu
        self.file_menu.add_command(label=self._('exit'), command=self.shutdown_application)

        # --- تحميل الأيقونات وتكوين الأنماط (تم نقلها إلى هنا) ---
        # يجب أن يتم ذلك بعد إنشاء النافذة وقبل إنشاء الأزرار التي تستخدم الأيقونات
        self.icons = {}
        self.load_icons()
        self.configure_styles()


        self.settings_button = ttk.Button(self.toolbar_frame, text=self._('settings'), image=(self.icons.get('settings') or {}).get('color'), compound=tk.LEFT, style='Toolbutton', command=self.show_settings_window)
        self.settings_button.pack(side=tk.LEFT, padx=2)

        self.open_folder_button = ttk.Button(self.toolbar_frame, text=self._('downloads_folder'), image=(self.icons.get('folder') or {}).get('color'), compound=tk.LEFT, style='Toolbutton', command=self.open_download_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=2)

        self.about_button = ttk.Button(self.toolbar_frame, text=self._('about'), image=(self.icons.get('about') or {}).get('color'), compound=tk.LEFT, style='Toolbutton', command=self.show_about_dialog)
        self.about_button.pack(side=tk.LEFT, padx=2)

        # --- Create a scraper instance to handle requests ---
        # This will be used instead of the standard requests library to bypass Cloudflare
        if cloudscraper:
            # We configure the scraper to mimic a common browser to increase the chances of success.
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )

        self.create_theme_menu(self.toolbar_frame)

        # --- Headers to mimic a browser and avoid being blocked ---
        self.request_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.blackmagicdesign.com/' # A common referer for this site
        }

        # --- متغيرات الحالة العامة ---
        self.downloads = {} # قاموس لتخزين مهام التحميل {id: DownloadItem}
        
        # --- Load settings passed from main ---
        if initial_settings is None:
            initial_settings = {}
        self.settings = initial_settings # <-- إضافة هذا السطر لإصلاح الخطأ
        
        # Load colors, with a fallback to defaults
        default_colors = {
            'complete': '#dff0d8',
            'paused': '#fcf8e3',
            'error': '#f2dede',
            'downloading': '#d9edf7'
        }
        self.color_settings = self.settings.get('colors', default_colors)
        self.server_port = self.settings.get('server_port', 9614)
        self.toaster = ToastNotifier() if ToastNotifier else None
        self.max_concurrent_downloads = self.settings.get('max_concurrent_downloads', 3)
        self.sort_column = None
        self.sort_reverse = False

        # --- نظام الفئات ---
        self.category_map = {
            'all': 'all_downloads',
            'uncategorized': 'uncategorized',
            'video': 'video',
            'audio': 'audio',
            'software': 'software',
            'documents': 'documents',
            'compressed': 'compressed',
            'images': 'images_category',
        }
        self.categories = {key: self._(trans_key) for key, trans_key in self.category_map.items()}
        self.current_category = 'all' # الفئة المحددة حاليًا


        # --- Speed Limiter ---
        self.speed_limiter = SpeedLimiter()
        self.update_speed_limit_from_settings()

        # --- خريطة الامتدادات إلى الفئات ---
        self.extension_to_category = {
            # Compressed
            '.zip': 'compressed', '.rar': 'compressed', '.7z': 'compressed', '.tar': 'compressed', '.gz': 'compressed', '.bz2': 'compressed',
            # Software
            '.exe': 'software', '.msi': 'software', '.dmg': 'software', '.deb': 'software', '.rpm': 'software',
            # Video
            '.mp4': 'video', '.mkv': 'video', '.avi': 'video', '.mov': 'video', '.flv': 'video', '.wmv': 'video',
            # Audio
            '.mp3': 'audio', '.flac': 'audio', '.wav': 'audio', '.ogg': 'audio',
            # Documents
            '.pdf': 'documents', '.doc': 'documents', '.docx': 'documents', '.xls': 'documents', '.xlsx': 'documents', '.ppt': 'documents', '.pptx': 'documents',
            # Images (New Category)
            '.jpg': 'images', '.jpeg': 'images', '.png': 'images', '.gif': 'images', '.bmp': 'images', '.svg': 'images', '.webp': 'images',
        }


        
        # --- إعداد عناوين الأعمدة مع إمكانية الترتيب ---
        # --- أزرار التحكم ---
        self.control_frame = ttk.Frame(self.master)
        self.control_frame.pack(pady=5, fill=tk.X, padx=10)

        self.add_url_button = ttk.Button(self.control_frame, text=self._('add_url'), image=(self.icons.get('add') or {}).get('color'), compound=tk.LEFT, command=self.show_add_download_dialog, style='Accent.TButton')
        self.add_url_button.pack(side=tk.LEFT, padx=5)

        self.resume_from_file_button = ttk.Button(self.control_frame, text=self._('resume_from_file'), image=(self.icons.get('resume_file') or {}).get('color'), compound=tk.LEFT, command=self.resume_from_file, style='Accent.TButton')
        self.resume_from_file_button.pack(side=tk.LEFT, padx=5)

        ttk.Separator(self.control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # --- إنشاء أزرار التحكم مع الاحتفاظ بمرجع دائم للأيقونات ---
        self.action_button = ttk.Button(self.control_frame, text=self._('start'), compound=tk.LEFT, command=self.toggle_selected_download)
        self.action_button.icon_start_color = (self.icons.get('start') or {}).get('color')
        self.action_button.icon_start_disabled = (self.icons.get('start') or {}).get('disabled')
        self.action_button.icon_pause_color = (self.icons.get('pause') or {}).get('color')
        self.action_button.icon_pause_disabled = (self.icons.get('pause') or {}).get('disabled')
        self.action_button.icon_resume_color = (self.icons.get('resume_file') or {}).get('color') # For refresh link
        self.action_button.configure(style='Accent.TButton')
        self.action_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = ttk.Button(self.control_frame, text=self._('cancel'), compound=tk.LEFT, command=self.cancel_selected_download)
        self.cancel_button.icon_color = (self.icons.get('cancel') or {}).get('color')
        self.cancel_button.icon_disabled = (self.icons.get('cancel') or {}).get('disabled')
        self.cancel_button.configure(style='Accent.TButton')
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        self.separator1 = ttk.Separator(self.control_frame, orient=tk.VERTICAL)
        self.separator1.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.remove_completed_button = ttk.Button(self.control_frame, text=self._('remove_completed'), image=(self.icons.get('remove') or {}).get('color'), compound=tk.LEFT, command=self.remove_completed_downloads, style='Accent.TButton')
        self.remove_completed_button.pack(side=tk.RIGHT, padx=5)

        self.remove_button = ttk.Button(self.control_frame, text=self._('remove'), compound=tk.LEFT, command=self.remove_selected_download, style='Accent.TButton')
        self.remove_button.icon_color = (self.icons.get('remove') or {}).get('color')
        self.remove_button.icon_disabled = (self.icons.get('remove') or {}).get('disabled')
        self.remove_button.pack(side=tk.RIGHT, padx=5)

        # --- Search Bar with Debouncing ---
        self.search_timer = None
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_text_changed)
        
        # Create a frame with a border to act as a container for the search entry
        search_frame = ttk.Frame(self.control_frame, style='Card.TFrame', padding=1)
        search_frame.pack(side=tk.RIGHT, padx=(0, 5), fill=tk.Y)
        
        self.clear_search_button = ttk.Button(search_frame, text="×", command=self.clear_search, style='Accent.Toolbutton', width=2)
        # The button is packed/unpacked dynamically

        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25, style='Accent.Search.TEntry')
        search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.search_label = ttk.Label(self.control_frame, text=self._('search'))
        self.search_label.pack(side=tk.RIGHT, padx=(10, 2))

        # --- PanedWindow for Categories and Downloads ---
        self.paned_window = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.paned_window.pack(expand=True, fill=tk.BOTH, padx=10)

        # --- Left Pane: Categories ---
        self.category_frame = ttk.Frame(self.paned_window, padding=5)
        self.category_tree = ttk.Treeview(self.category_frame, show="tree", selectmode="browse")
        self.category_tree.pack(expand=True, fill=tk.BOTH)
        self.paned_window.add(self.category_frame, weight=1)

        # Populate categories
        self.populate_category_tree()
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)

        # --- Right Pane: Downloads ---
        self.tree_frame = ttk.Frame(self.paned_window, padding=5)
        self.tree = ttk.Treeview(self.tree_frame, columns=("file", "size", "progress", "speed", "time_left", "status"), show="headings")
        self.paned_window.add(self.tree_frame, weight=4)

        # --- إضافة نمط لصفوف الجدول المخططة (Zebra-striping) ---
        # تم نقلها هنا لضمان أن self.tree موجود بالفعل
        self.tree.tag_configure('oddrow', background='#f0f0f0')
        self.tree.tag_configure('evenrow', background='white')

        # --- "No Results" Label ---
        self.no_results_label = ttk.Label(self.tree_frame, text=self._('no_results_found'), font=("Tahoma", 14, "italic"), foreground="gray")
        # This label will be shown/hidden in apply_filters_and_update_view

        # --- Scrollbar for Downloads Tree ---
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tree.bind("<Double-1>", self.show_mini_progress_window_on_double_click)

        # --- Register for Drag and Drop ---
        if TkinterDnD:
            self.tree.drop_target_register(DND_TEXT)
            self.tree.dnd_bind('<<Drop>>', self.handle_drop)

        # --- إعداد عناوين الأعمدة مع إمكانية الترتيب ---
        self.column_headers = {
            "file": self._('file'), "size": self._('size'), "progress": self._('progress'),
            "speed": self._('speed'), "time_left": self._('time_left'), "status": self._('status')
        }
        for col, text in self.column_headers.items():
            self.tree.heading(col, text=text, command=lambda _col=col: self.sort_by_column(_col))

        self.tree.column("file", width=200)
        self.tree.column("size", width=80, anchor=tk.CENTER)
        self.tree.column("progress", width=100, anchor=tk.CENTER)
        self.tree.column("speed", width=90, anchor=tk.CENTER)
        self.tree.column("time_left", width=90, anchor=tk.CENTER)
        self.tree.column("status", width=100, anchor=tk.CENTER)

        # --- قائمة النقر بالزر الأيمن (Context Menu) ---
        # تم التغيير: إنشاء القائمة مرة واحدة، ولكن سيتم تحديث الأوامر ديناميكيًا
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.tree.bind("<Button-3>", self.handle_right_click)

        # --- تسمية الحالة الكلية ---
        self.status_label = ttk.Label(master, text=self._('ready_to_download'))
        self.status_label.pack(pady=5, fill=tk.X, padx=10)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # تحميل الإعدادات والجلسة السابقة وبدء حلقة تحديث الواجهة
        self.apply_color_settings()
        self.load_session()
        self.process_startup_downloads() # <-- بدء التحميلات التلقائية
        self.process_download_queue() # بدء معالجة قائمة الانتظار
        self.update_ui_loop()
        self.check_scheduled_downloads()
        self.tray_icon = None
        self.setup_tray_icon()
        # --- التحقق من وجود تحديثات عند بدء التشغيل ---
        self.check_for_updates()
        # --- بدء خادم الويب المحلي لاعتراض التحميلات من المتصفح ---
        self.start_local_server()

    def populate_category_tree(self):
        """يمسح ويعيد تعبئة شجرة الفئات."""
        """Clears and repopulates the category treeview."""
        for i in self.category_tree.get_children():
            self.category_tree.delete(i)

        # Add categories in a specific order
        ordered_keys = ['all', 'uncategorized', 'video', 'audio', 'images', 'software', 'documents', 'compressed']
        for key in ordered_keys:
            if key in self.categories:
                self.category_tree.insert('', 'end', iid=key, text=self.categories[key])
        
        # Add any other dynamically loaded categories
        for key, name in self.categories.items():
            if not self.category_tree.exists(key):
                self.category_tree.insert('', 'end', iid=key, text=name)

        self.category_tree.selection_set('all')

    def update_speed_limit_from_settings(self):
        if self.settings.get('speed_limit_enabled', False):
            self.speed_limiter.set_limit(self.settings.get('speed_limit_value', 1024), self.settings.get('speed_limit_unit', 'kb_s'))
        else:
            self.speed_limiter.set_limit(0, 'kb_s') # Disable limit

    def apply_frame_color(self, frame_color, theme_bg_color=None):
        """يطبق اللون المميز على الإطارات الرئيسية وشريط الحالة."""
        if not frame_color:
            return

        style = ttk.Style()

        # تحديد لون نص متباين (فاتح أو داكن) لضمان الوضوح
        try:
            r, g, b = self.master.winfo_rgb(frame_color)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            fg_color = 'white' if brightness < 128000 else 'black'
        except (tk.TclError, ValueError):
            fg_color = 'black'

        # إنشاء نمط مخصص للإطارات الملونة
        style.configure('Accent.TFrame', background=frame_color)
        style.configure('Accent.TSeparator', background=frame_color)
        style.configure('Accent.TLabel', background=frame_color, foreground=fg_color)

        # ضمان أن خلفية شجرة الفئات تظل متوافقة مع السمة
        if theme_bg_color:
            style.configure('Treeview', background=theme_bg_color, fieldbackground=theme_bg_color)

        # تطبيق النمط على الإطارات وشريط الحالة
        self.toolbar_frame.configure(style='Accent.TFrame')
        self.control_frame.configure(style='Accent.TFrame')
        self.separator1.configure(style='Accent.TSeparator')
        self.category_frame.configure(style='Accent.TFrame')
        self.tree_frame.configure(style='Accent.TFrame')
        self.status_label.configure(style='Accent.TLabel')

    def get_category_from_filename(self, filename):
        """Determines the download category based on the file extension."""
        default_category = self.settings.get('default_unknown_category', 'uncategorized')
        if not filename:
            return default_category
        
        _, extension = os.path.splitext(filename.lower())
        return self.extension_to_category.get(extension, default_category)

    def retranslate_ui(self):
        """Updates all UI text elements with the new language."""
        self._ = self.lang_manager.get_translator()
        self.master.title(self._('window_title'))

        # Toolbar
        self.file_menubutton.config(text=self._('file_menu'))
        self.file_menu.entryconfig(0, label=self._('check_for_updates'))
        self.file_menu.entryconfig(0, label=self._('exit'))

        self.settings_button.config(text=self._('settings'))
        self.open_folder_button.config(text=self._('downloads_folder'))
        self.about_button.config(text=self._('about'))
        if hasattr(self, 'theme_menubutton'):
            self.theme_menubutton.config(text=f"{self._('theme')}: {self.master.get_theme().capitalize()}")

        # Control buttons
        self.add_url_button.config(text=self._('add_url'))
        self.resume_from_file_button.config(text=self._('resume_from_file'))
        self.cancel_button.config(text=self._('cancel'))
        self.remove_button.config(text=self._('remove'))
        # Action button text is updated dynamically in update_ui_for_selection

        # Treeview headers
        for col, key in [("file", 'file'), ("size", 'size'), ("progress", 'progress'), ("speed", 'speed'), ("time_left", 'time_left'), ("status", 'status')]:
            self.tree.heading(col, text=self._(key))
        
        # Category tree
        self.categories = {key: self._(trans_key) for key, trans_key in self.category_map.items()}
        for key, name in self.categories.items():
            if self.category_tree.exists(key):
                self.category_tree.item(key, text=name)

        # Search bar
        self.search_label.config(text=self._('search'))

        # "No results" label
        self.no_results_label.config(text=self._('no_results_found'))


    def load_icons(self):
        """Loads icons for the UI, handling potential errors."""
        # استخدم subsample لتصغير الأيقونات إذا كانت كبيرة جداً
        icon_files = {
            "add": "icons/plus-circle.png",
            "resume_file": "icons/refresh-cw.png",
            "start": "icons/play-circle.png",
            "pause": "icons/pause.png",
            "cancel": "icons/x-circle.png",
            "remove": "icons/trash-2.png",
            "settings": "icons/settings.png",
            "folder": "icons/folder.png",
            "about": "icons/info.png",
        }
        for name, path in icon_files.items():
            try:
                if not PillowAvailable:
                    # Fallback to PhotoImage if Pillow is not installed
                    full_path = resource_path(path)
                    self.icons[name] = {'color': tk.PhotoImage(file=full_path).subsample(4, 4)}
                    continue

                full_path = resource_path(path)
                original_image = Image.open(full_path).convert("RGBA")

                # Resize the image using Pillow for better quality
                size = (18, 18) # حجم الأيقونة النهائي
                resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
                
                # Create the color and disabled (grayscale) versions
                color_icon = ImageTk.PhotoImage(resized_image)
                grayscale_icon = ImageTk.PhotoImage(ImageOps.grayscale(resized_image))
                self.icons[name] = {'color': color_icon, 'disabled': grayscale_icon}
            except Exception as e:
                print(f"Warning: Icon not found or could not be loaded from '{path}'")
                self.icons[name] = None

    def configure_styles(self):
        """Configures custom ttk styles and the default application font."""
        style = ttk.Style()

        # --- تعيين الخط الافتراضي لجميع عناصر ttk ---
        # يمكنك تغيير 'Tahoma' إلى أي خط تريده مثل 'Calibri', 'Arial', 'Segoe UI'
        default_font = ('Tahoma', 10)
        style.configure('.', font=default_font)

        # --- تخصيص أنماط معينة فوق الخط الافتراضي ---
        style.configure('Search.TEntry', borderwidth=0, relief='flat')
        # لم نعد بحاجة لتحديد الخط هنا لأنه يرثه من النمط الافتراضي '.'
        # نحن فقط نحدد الـ padding.
        style.configure('TButton', padding=5)
        # Remove the border from the entry widget itself, as the frame will provide it
        style.configure('Search.TEntry', borderwidth=0, relief='flat')

        style.configure('Toolbutton', padding=5)
        
        # --- أنماط جديدة للواجهات المصغرة ---
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        style.configure('Title.TFrame', background='#3e3e3e') # لون شريط العنوان
        style.configure('Title.TLabel', background='#3e3e3e', foreground='white', font=('Tahoma', 9, 'bold'))
        # تغيير لون النص الافتراضي إلى الأسود لضمان ظهوره على الخلفيات الفاتحة
        style.configure('Close.TButton', font=('Arial', 8, 'bold'), padding=(2, 0), relief='flat', foreground='black')
        # عند مرور الفأرة، تتغير الخلفية إلى الأحمر والنص إلى الأبيض
        style.map('Close.TButton', background=[('active', '#c04040')], foreground=[('active', 'white')])
        
        # أنماط جديدة للأزرار والإدخالات داخل الإطارات الملونة
        style.configure('Accent.TButton', padding=5)
        style.configure('Accent.Toolbutton', padding=5)
        style.configure('Accent.Search.TEntry', borderwidth=0, relief='flat')

    def handle_right_click(self, event):
        """يعالج النقر بالزر الأيمن: يحدد العنصر ثم يعرض القائمة."""
        # تحديد العنصر الذي تم النقر عليه
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        
        # الحل النهائي: حدد العنصر أولاً. هذا يضمن أن الواجهة محدثة
        # قبل استدعاء show_context_menu، مما يحل مشكلة النقرة المزدوجة.
        if self.tree.selection() != (item_id,):
            self.tree.selection_set(item_id)
        
        # استدعاء دالة عرض القائمة بعد فترة قصيرة جدًا للتأكد من اكتمال التحديد
        self.master.after(10, lambda: self.show_context_menu(event))

    def show_context_menu(self, event):
        """يبني ويعرض قائمة السياق للعنصر المحدد حاليًا."""
        item = self.get_selected_download_item()
        if not item: return
        self.context_menu.delete(0, tk.END)

        # --- إضافة الأوامر مع lambda لتمرير العنصر الصحيح ---
        self.context_menu.add_command(label=self._('show_part_details'), command=lambda: self.show_details_window(item=item))
        self.context_menu.add_separator()
        self.context_menu.add_command(label=self._('open_file_location'), command=lambda: self.open_selected_item_folder(item=item))
        self.context_menu.add_command(label=self._('copy_download_link'), command=lambda: self.copy_url_to_clipboard(item=item))
        self.context_menu.add_separator()
        self.context_menu.add_command(label=self._('refresh_download_link'), command=lambda: self.refresh_download_link(item=item))
        self.context_menu.add_command(label=self._('reset_download'), command=lambda: self.reset_selected_download(item=item))
        self.context_menu.add_command(label=self._('cleanup_temp_files'), command=lambda: self.cleanup_selected_item_files(item=item))
        self.context_menu.add_separator()
        self.context_menu.add_command(label=self._('delete_file_from_disk'), command=lambda: self.delete_selected_file_from_disk(item=item))

        # --- تحديث حالة الخيارات ---
        # تفعيل الخيار إذا كان التحميل قد بدأ أو اكتمل
        if item.state not in [DownloadState.IDLE, DownloadState.SCHEDULED]:
            self.context_menu.entryconfig(2, state="normal") # Index of 'open_file_location'
        else:
            self.context_menu.entryconfig(2, state="disabled")

        # تفعيل خيار حذف الملف من القرص فقط إذا كان الملف موجودًا بالفعل
        if os.path.exists(item.save_location):
            self.context_menu.entryconfig(9, state="normal") # Index of 'delete_file_from_disk'
        else:
            self.context_menu.entryconfig(9, state="disabled")

        # تفعيل أو تعطيل خيارات الإدارة
        if item.state in [DownloadState.PAUSED, DownloadState.CANCELLED, DownloadState.ERROR_RETRYING]:
            self.context_menu.entryconfig(6, state="normal") # reset
            self.context_menu.entryconfig(7, state="normal") # cleanup
            self.context_menu.entryconfig(5, state="disabled") # refresh
        elif item.state == DownloadState.PERMANENT_ERROR:
            self.context_menu.entryconfig(5, state="normal") # refresh
        else:
            self.context_menu.entryconfig(5, state="disabled") # refresh
            self.context_menu.entryconfig(6, state="disabled") # reset
            self.context_menu.entryconfig(7, state="disabled") # cleanup
        
        # عرض القائمة
        self.context_menu.post(event.x_root, event.y_root)

    def show_about_dialog(self):
        """Displays a custom 'About' dialog box with a clickable link."""
        about_win = tk.Toplevel(self.master)
        about_win.title(self._('about'))
        about_win.geometry("400x220")
        about_win.transient(self.master)
        about_win.resizable(False, False)
        about_win.grab_set()

        # Set icon for the about window title bar
        try:
            icon_path = resource_path("icons/icon.ico")
            about_win.iconbitmap(icon_path)
        except tk.TclError:
            pass # Silently ignore if icon fails to load for a Toplevel

        main_frame = ttk.Frame(about_win, padding="15")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Top frame with icon and text ---
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, expand=True)

        # Load and display a larger icon
        try:
            img = Image.open(resource_path("icons/info.png")).resize((48, 48), Image.Resampling.LANCZOS)
            about_icon = ImageTk.PhotoImage(img)
            icon_label = ttk.Label(top_frame, image=about_icon)
            icon_label.image = about_icon # Keep a reference
            icon_label.pack(side=tk.LEFT, padx=(0, 15), anchor=tk.NW)
        except Exception:
            pass # Ignore if icon fails to load

        text_frame = ttk.Frame(top_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        header_font = font.Font(family="Tahoma", size=11, weight="bold")
        ttk.Label(text_frame, text="برنامج تحميل الملفات المتقدم", font=header_font).pack(anchor=tk.W)
        ttk.Label(text_frame, text="الإصدار: 1.1 (مع دعم الجلسات)").pack(anchor=tk.W)
        ttk.Label(text_frame, text="المطور: Eng.Mohamed").pack(anchor=tk.W)
        ttk.Label(text_frame, text="سنة: 2025").pack(anchor=tk.W)
        
        url = "https://techiraqi.netlify.app/contact"
        link_font = font.Font(family="Tahoma", size=10, underline=True)
        link_label = tk.Label(text_frame, text="للتواصل والدعم الفني", fg="blue", cursor="hand2", font=link_font)
        link_label.pack(anchor=tk.W, pady=(5, 0))
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new(url))

        ok_button = ttk.Button(main_frame, text=self._('ok'), command=about_win.destroy)
        ok_button.pack(side=tk.BOTTOM, pady=(15, 0))

    def create_theme_menu(self, parent_frame):
        """Creates a Menubutton on the toolbar to select a ttk theme."""
        if hasattr(self.master, 'get_themes') and hasattr(self.master, 'set_theme') and hasattr(self.master, 'get_theme'):
            
            current_theme_name = self.master.get_theme()
            self.theme_menubutton = ttk.Menubutton(parent_frame, text=f"{self._('theme')}: {current_theme_name.capitalize()}", style='Accent.Toolbutton')
            self.theme_menubutton.pack(side=tk.RIGHT, padx=2)

            theme_menu = tk.Menu(self.theme_menubutton, tearoff=0)
            self.theme_menubutton['menu'] = theme_menu

            current_theme_var = tk.StringVar(value=self.settings.get('theme', 'arc'))

            def change_theme():
                new_theme = current_theme_var.get()
                self.master.set_theme(new_theme)
                self.theme_menubutton.config(text=f"{self._('theme')}: {new_theme.capitalize()}")
                self.save_settings()

            for theme in sorted(self.master.get_themes()):
                theme_menu.add_radiobutton(label=theme.capitalize(), variable=current_theme_var, value=theme, command=change_theme)

    def open_download_folder(self):
        """Opens the default download folder in the file explorer."""
        folder_path = self.get_default_download_folder()
        try:
            os.startfile(folder_path)
        except FileNotFoundError:
            messagebox.showerror("خطأ", f"المجلد الافتراضي غير موجود:\n{folder_path}", parent=self.master)
        except Exception as e:
            messagebox.showerror("خطأ", f"لم يتمكن من فتح المجلد:\n{e}", parent=self.master)

    def open_selected_item_folder(self, item=None):
        """يفتح المجلد الذي يحتوي على ملف التحميل المحدد."""
        item = item or self.get_selected_download_item()
        if not item:
            return

        folder_path = os.path.dirname(item.save_location)
        
        try:
            if os.path.isdir(folder_path):
                os.startfile(folder_path)
            else:
                messagebox.showwarning("المجلد غير موجود", f"المجلد الهدف غير موجود بعد:\n{folder_path}", parent=self.master)
        except Exception as e:
            messagebox.showerror("خطأ", f"لم يتمكن من فتح المجلد:\n{e}", parent=self.master)

    def copy_url_to_clipboard(self, item=None):
        """Copies the URL of the selected download item to the clipboard."""
        item = item or self.get_selected_download_item()
        if not item:
            return
        
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(item.url)
            self.status_label.config(text=self._('link_copied_success')) # Assuming this key exists
        except tk.TclError:
            messagebox.showerror(self._('error_title'), self._('clipboard_error'), parent=self.master) # Assuming these keys exist

    def reset_selected_download(self, item=None):
        """Resets a download by deleting its part files and setting its state to idle."""
        item = item or self.get_selected_download_item()
        if not item:
            return

        if messagebox.askyesno(
            self._('confirm_reset_title'),
            self._('confirm_reset_message'),
            parent=self.master
        ):
            # Cancel any pending retry timers
            if item._retry_timer:
                self.master.after_cancel(item._retry_timer)
                item._retry_timer = None
            
            # Cleanup part files
            self.cleanup_temp_files(item=item)

            # Reset item state
            item.reset()

    def show_settings_window(self):
        """يفتح نافذة الإعدادات."""
        SettingsWindow(self.master, self)

    def sort_by_column(self, col):
        """Sorts the treeview items by the clicked column."""
        # 1. Update the sort state
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        # 2. Let the main filter/update function handle the re-ordering
        self.apply_filters_and_update_view()

        # تحديث مؤشرات الترتيب في العناوين
        for c, text in [(col, self._(col)) for col in self.column_headers.keys()]:
            indicator = ' ▼' if self.sort_reverse else ' ▲'
            self.tree.heading(c, text=text + (indicator if c == col else ''))

    def save_settings(self):
        """Saves the current settings (colors and theme) to a file."""
        settings_to_save = {
            'colors': self.color_settings,
            'theme': None,
            'language': self.lang_manager.language,
            'run_on_startup': self.is_in_startup(),
            'server_port': self.server_port,
            'default_unknown_category': self.settings.get('default_unknown_category', 'uncategorized'),
            'auto_resume_on_startup': self.settings.get('auto_resume_on_startup', True),
            'default_download_folder': self.settings.get('default_download_folder'),
            'title_bar_bg_color': self.settings.get('title_bar_bg_color', '#4a4a4a'),
            'window_bg_color': self.settings.get('window_bg_color', '#f0f0f0'),
            'instant_search_enabled': self.settings.get('instant_search_enabled', True),
            **self.get_speed_limit_settings(), # Add speed limit settings
            'max_concurrent_downloads': self.max_concurrent_downloads,
        }
        # Get theme only if using ThemedTk
        if hasattr(self.master, 'get_theme'):
            settings_to_save['theme'] = self.master.get_theme()


        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_speed_limit_settings(self):
        """Returns a dictionary of the current speed limit settings."""
        return {
            'speed_limit_enabled': self.settings.get('speed_limit_enabled', False),
            'speed_limit_value': self.settings.get('speed_limit_value', 1024),
            'speed_limit_unit': self.settings.get('speed_limit_unit', 'kb_s'),
        }


    def apply_color_settings(self):
        """Applies the colors from self.color_settings to the treeview tags."""
        for tag, color in self.color_settings.items():
            if color: # Ensure color is not empty
                self.tree.tag_configure(tag, background=color)

    def paste_from_clipboard(self, entry_widget):
        """يلصق النص من الحافظة إلى حقل إدخال URL."""
        try:
            clipboard_content = self.master.clipboard_get()
            if clipboard_content:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, clipboard_content)
        except tk.TclError:
            self.status_label.config(text=self._('clipboard_empty_error')) # Assuming this key exists


    def get_default_download_folder(self):
        """Gets the default download folder from settings, with fallbacks."""
        # 1. Check for the setting
        saved_path = self.settings.get('default_download_folder')
        if saved_path and os.path.isdir(saved_path):
            return saved_path

        # 2. Fallback to user's Downloads folder
        try:
            downloads_path = str(Path.home() / "Downloads")
            if not os.path.exists(downloads_path):
                os.makedirs(downloads_path, exist_ok=True)
            return downloads_path
        except Exception:
            pass

        # 3. Fallback to current working directory
        return os.getcwd()
    def suggest_filename_from_url(self, url_str):
        """يقترح اسم ملف صالح بناءً على الرابط."""
        if not url_str:
            return "downloaded_file"

        def sanitize(name):
            """يزيل الأحرف غير الصالحة من اسم الملف."""
            invalid_chars = r'<>:"/\|?*'
            return "".join('_' if c in invalid_chars else c for c in name)

        try:
            # إزالة أي معاملات من الرابط
            path_part = url_str.split('?')[0]
            # محاولة الحصول على اسم الملف من الجزء الأخير من المسار
            suggested_name = sanitize(path_part.split('/')[-1])
            # إذا كان الاسم المقترح صالحًا ويحتوي على امتداد، استخدمه
            if suggested_name and '.' in suggested_name:
                return suggested_name
        except Exception:
            pass # تجاهل الأخطاء والمتابعة إلى القيمة الافتراضية
        
        return "downloaded_file"

    def get_unique_save_path(self, path):
        """يضمن أن مسار الحفظ فريد عن طريق إضافة رقم إذا كان الملف موجودًا بالفعل."""
        if not os.path.exists(path):
            return path
        
        directory, filename = os.path.split(path)
        name, ext = os.path.splitext(filename)
        
        counter = 1
        while True:
            new_filename = f"{name} ({counter}){ext}"
            new_path = os.path.join(directory, new_filename)
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def format_size(self, size_bytes):
        if size_bytes is None: return "N/A"
        if size_bytes == 0: return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = 0
        try:
            size_bytes_float = float(size_bytes)
        except (ValueError, TypeError):
            return "N/A"
        while size_bytes_float >= 1024 and i < len(size_name) - 1:
            size_bytes_float /= 1024.0
            i += 1
        return f"{size_bytes_float:.2f} {size_name[i]}"

    def format_time(self, seconds):
        if seconds is None or seconds < 0 or seconds == float('inf'):
            return "غير معروف"
        minutes, secs = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0: return f"{hours}س {minutes}د {secs}ث"
        if minutes > 0: return f"{minutes}د {secs}ث"
        return f"{secs}ث"

    def get_selected_download_item(self):
        """Returns the DownloadItem instance for the selected item in the tree."""
        selected_ids = self.tree.selection()
        if not selected_ids:
            return None
        item_id = selected_ids[0]
        return self.downloads.get(item_id)

    def toggle_selected_download(self):
        item = self.get_selected_download_item()
        if not item:
            messagebox.showinfo(self._('information'), self._('select_download_first'), parent=self.master)
            return

        if item.state in [DownloadState.IDLE, DownloadState.PAUSED, DownloadState.SCHEDULED, DownloadState.ERROR_RETRYING, DownloadState.CANCELLED, DownloadState.PERMANENT_ERROR]:
            self.start_download(item)
        elif item.state == DownloadState.DOWNLOADING:
            self.pause_download(item)

    def start_download(self, item):
        """Adds a download to the queue and processes the queue."""
        if item.state == DownloadState.ERROR_RETRYING and item._retry_timer:
            self.master.after_cancel(item._retry_timer)
            item._retry_timer = None

        # If scheduled, unschedule it
        if item.state == DownloadState.SCHEDULED:
            item.scheduled_time = None

        # Set to IDLE to be picked up by the queue processor
        item.state = DownloadState.IDLE
        item.status_text = self._('ready') # Or 'Queued' if you add that translation
        item.pause_event.set() # Ensure download can run
        self.update_ui_for_selection()
        self.process_download_queue()

    def process_download_queue(self):
        """Checks for available slots and starts the next download in the queue."""
        active_downloads = sum(1 for item in self.downloads.values() if item.state == DownloadState.DOWNLOADING)
        
        if active_downloads >= self.max_concurrent_downloads:
            return # Limit reached

        # Find the next item to download (in IDLE state)
        # We can add sorting logic here later (e.g., by date added)
        next_item = next((item for item in self.downloads.values() if item.state == DownloadState.IDLE), None)

        if next_item:
            self._initiate_download(next_item)

    def _initiate_download(self, item):
        """Internal method to start the download process for a specific item."""
        item.cancel_event.clear() # Reset cancellation flag if resuming
        item.status_text = self._('getting_info')
        item.state = DownloadState.GETTING_INFO
        
        # استخدم خيط منفصل للحصول على الحجم لتجنب تجميد الواجهة
        info_thread = threading.Thread(target=self.get_file_info_and_start_download, args=(item,))
        info_thread.daemon = True
        info_thread.start()

    def handle_drop(self, event):
        """Handles a URL dropped onto the treeview."""
        url = event.data
        # Clean up potential curly braces from some drag sources
        if url.startswith('{') and url.endswith('}'):
            url = url[1:-1]

        if url and url.strip().startswith(('http://', 'https://')):
            self.show_add_download_dialog(initial_url=url.strip())

    def show_add_download_dialog(self, initial_url=None):
        dialog = tk.Toplevel(self.master)
        dialog.title(self._('add_new_download'))

        # --- Set Window Icon ---
        try:
            icon_path = resource_path("icons/icon.ico")
            dialog.iconbitmap(icon_path)
        except tk.TclError:
            pass # Silently ignore if icon fails to load for a Toplevel

        dialog.geometry("550x420")
        dialog.transient(self.master)
        dialog.grab_set()

        accent_color = self.settings.get('title_bar_bg_color', '#4a4a4a')

        url_frame = ttk.Frame(dialog)
        url_frame.pack(pady=(10, 5), padx=10, fill=tk.X)
        ttk.Label(url_frame, text=self._('file_url')).pack(anchor=tk.W)
        url_entry = ttk.Entry(url_frame, width=70)
        url_entry.pack(fill=tk.X, expand=True)

        if initial_url:
            url_entry.insert(0, initial_url)
        else:
            try:
                clipboard_content = self.master.clipboard_get()
                if clipboard_content.startswith('http'):
                    url_entry.insert(0, clipboard_content)
            except tk.TclError:
                pass

        # --- Save Path Frame ---
        save_frame = ttk.Frame(dialog)
        save_frame.pack(pady=5, padx=10, fill=tk.X)
        ttk.Label(save_frame, text=self._('save_in')).pack(anchor=tk.W)
        
        save_path_entry = ttk.Entry(save_frame)
        save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def browse_save_location():
            url = url_entry.get().strip()
            initial_filename = self.suggest_filename_from_url(url)
            save_path = filedialog.asksaveasfilename(
                initialdir=self.get_default_download_folder(),
                initialfile=initial_filename,
                title="اختر مكان حفظ الملف",
                parent=dialog
            )
            if save_path:
                save_path_entry.delete(0, tk.END)
                save_path_entry.insert(0, save_path)

        browse_button = ttk.Button(save_frame, text=self._('browse'), command=browse_save_location)
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))

        # --- Segments Frame ---
        segments_frame = ttk.Frame(dialog)
        segments_frame.pack(pady=5, padx=10, fill=tk.X)
        ttk.Label(segments_frame, text=self._('num_segments')).pack(side=tk.LEFT)

        segments_var = tk.StringVar(value='8')
        segments_spinbox = ttk.Spinbox(
            segments_frame,
            from_=1,
            to=16,
            textvariable=segments_var,
            width=5
        )
        segments_spinbox.pack(side=tk.LEFT, padx=5)

        # --- Scheduling Frame ---
        schedule_outer_frame = ttk.Frame(dialog)
        schedule_outer_frame.pack(pady=10, padx=10, fill=tk.X)

        datetime_frame = ttk.LabelFrame(schedule_outer_frame, text=self._('scheduling_settings'), padding="10")

        def toggle_schedule_controls():
            if schedule_var.get():
                datetime_frame.pack(fill=tk.X, expand=True, pady=(5,0))
            else:
                datetime_frame.pack_forget()

        schedule_var = tk.BooleanVar(value=False)
        schedule_check = ttk.Checkbutton(schedule_outer_frame, text=self._('schedule_download'), variable=schedule_var, command=toggle_schedule_controls)
        schedule_check.pack(anchor=tk.W)

        now = datetime.datetime.now()

        # Date controls
        date_frame = ttk.Frame(datetime_frame)
        date_frame.pack(fill=tk.X, pady=2)
        ttk.Label(date_frame, text=self._('date')).pack(side=tk.LEFT)
        year_var = tk.StringVar(value=str(now.year))
        ttk.Spinbox(date_frame, from_=now.year, to=now.year + 5, textvariable=year_var, width=6).pack(side=tk.LEFT, padx=2)
        month_var = tk.StringVar(value=str(now.month))
        ttk.Spinbox(date_frame, from_=1, to=12, textvariable=month_var, width=4).pack(side=tk.LEFT, padx=2)
        day_var = tk.StringVar(value=str(now.day))
        ttk.Spinbox(date_frame, from_=1, to=31, textvariable=day_var, width=4).pack(side=tk.LEFT, padx=2)

        # Time controls
        time_frame = ttk.Frame(datetime_frame)
        time_frame.pack(fill=tk.X, pady=2)
        ttk.Label(time_frame, text=self._('time')).pack(side=tk.LEFT)
        hour_var = tk.StringVar(value=str(now.hour))
        ttk.Spinbox(time_frame, from_=0, to=23, textvariable=hour_var, width=4, format="%02.0f").pack(side=tk.LEFT, padx=2)
        minute_var = tk.StringVar(value=str(now.minute))
        ttk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=4, format="%02.0f").pack(side=tk.LEFT, padx=2)

        # --- Category Frame ---
        category_frame = ttk.Frame(dialog)
        category_frame.pack(pady=5, padx=10, fill=tk.X)
        ttk.Label(category_frame, text=self._('category')).pack(side=tk.LEFT, padx=(0, 5))

        # --- Auto-detect and set category ---
        category_var = tk.StringVar()
        category_names = sorted([name for key, name in self.categories.items() if key != 'all'])
        category_combo = ttk.Combobox(category_frame, textvariable=category_var, values=category_names, state="readonly")
        category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def autodetect_category(event=None):
            """Suggests a category based on the URL's filename."""
            filename = self.suggest_filename_from_url(url_entry.get().strip())
            detected_category_key = self.get_category_from_filename(filename)
            if detected_category_key in self.categories:
                category_var.set(self.categories[detected_category_key])
            else:
                category_var.set(self._('uncategorized'))

        url_entry.bind("<FocusOut>", autodetect_category) # Update when user leaves the URL field
        autodetect_category() # Run once at the beginning to set initial value
        # Initially hide the frame
        toggle_schedule_controls()

        def on_ok_and_add():
            """Handles the OK button click in the add download dialog."""
            url = url_entry.get().strip()
            save_path = save_path_entry.get().strip()

            if not url:
                messagebox.showerror(self._('error_title'), self._('enter_url_error'), parent=dialog)
                return

            if not save_path:
                messagebox.showerror(self._('error_title'), self._('select_save_path_error'), parent=dialog)
                return

            # Check if a download to this exact path already exists
            if any(item.save_location == save_path for item in self.downloads.values()):
                messagebox.showwarning(self._('duplicate_download_warning'), "يوجد تحميل آخر محفوظ في نفس المسار بالفعل.", parent=dialog)
                return
            
            try:
                num_segments = int(segments_spinbox.get())
                if not 1 <= num_segments <= 16:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال عدد أجزاء صحيح بين 1 و 16.", parent=dialog)
                return

            scheduled_time = None
            if schedule_var.get():
                try:
                    scheduled_time = datetime.datetime(
                        int(year_var.get()), int(month_var.get()), int(day_var.get()),
                        int(hour_var.get()), int(minute_var.get())
                    )
                    if scheduled_time < datetime.datetime.now():
                        messagebox.showerror("خطأ في التوقيت", "لا يمكن جدولة تحميل في وقت قد مضى.", parent=dialog)
                        return
                except ValueError:
                    messagebox.showerror("خطأ في التاريخ/الوقت", "الرجاء إدخال تاريخ ووقت صحيحين.", parent=dialog)
                    return

            # Get or create category
            selected_category_name = category_var.get().strip()
            if not selected_category_name:
                selected_category_name = self._('uncategorized')
            
            # Find the internal key for the selected category name, or use the new name as key
            category_key = next((key for key, name in self.categories.items() if name == selected_category_name), selected_category_name.lower().replace(' ', '_'))
            if category_key not in self.categories and selected_category_name:
                self.categories[category_key] = selected_category_name
            
            if True: # Always proceed if save_path is provided
                # --- منطق استئناف التحميل المضاف ---
                # تحقق من وجود مجلد أجزاء تحميل سابقة
                temp_dir_path = f"{save_path}.idm-parts"
                parts_dir_exists = os.path.isdir(temp_dir_path)
                
                if parts_dir_exists:
                    if messagebox.askyesno("استئناف التحميل", "تم العثور على أجزاء تحميل سابقة لهذا الملف. هل ترغب في استئناف التحميل؟", parent=dialog):
                        # نعم، قم بالاستئناف. سيقوم add_download_item بحساب التقدم
                        self.add_download_item(url, save_path, num_segments=num_segments, scheduled_time=scheduled_time, category=category_key)
                        dialog.destroy()
                    elif messagebox.askyesno("الكتابة فوق الملف", "هل تريد حذف الأجزاء السابقة والبدء في تحميل جديد؟", parent=dialog):
                        # لا، ولكن وافق على الحذف والبدء من جديد
                        try:
                            shutil.rmtree(temp_dir_path)
                        except OSError as e:
                            messagebox.showerror("خطأ", f"لم يتمكن من حذف المجلد المؤقت: {temp_dir_path}\n{e}", parent=dialog)
                            return # إحباط العملية
                        self.add_download_item(url, save_path, num_segments=num_segments, scheduled_time=scheduled_time, category=category_key)
                        dialog.destroy()
                else:
                    # لا توجد أجزاء سابقة، أضف التحميل كالمعتاد
                    self.add_download_item(url, save_path, num_segments=num_segments, scheduled_time=scheduled_time, category=category_key)
                    dialog.destroy()

        # --- Buttons Frame ---
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(pady=20, padx=10, fill=tk.X)
        ok_button = ttk.Button(buttons_frame, text=self._('start_download_btn'), command=on_ok_and_add)
        ok_button.pack(side=tk.RIGHT)
        cancel_button = ttk.Button(buttons_frame, text=self._('cancel'), command=dialog.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))

        # --- تطبيق لون شريط العنوان المخصص (مثل النوافذ الأخرى) ---
        try:
            if sys.platform == "win32" and sys.getwindowsversion().major >= 10:
                dialog.update_idletasks()
                HWND = windll.user32.GetParent(dialog.winfo_id())
                if HWND:
                    def hex_to_bgr(hex_color):
                        hex_color = hex_color.lstrip('#')
                        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                        return (b << 16) | (g << 8) | r
                    
                    bg_color_bgr = hex_to_bgr(accent_color)
                    windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(bg_color_bgr)), sizeof(c_int))
                    # تعديل: حساب لون نص متباين (أسود أو أبيض) لضمان ظهوره
                    try:
                        bg_hex = accent_color.lstrip('#')
                        r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
                        brightness = (r * 299 + g * 587 + b * 114) / 1000
                        fg_hex = '#000000' if brightness > 128 else '#FFFFFF'
                    except Exception:
                        fg_hex = '#000000' # الافتراضي هو الأسود
                    
                    text_color_bgr = hex_to_bgr(fg_hex)
                    windll.dwmapi.DwmSetWindowAttribute(HWND, 36, byref(c_int(text_color_bgr)), sizeof(c_int))
        except Exception:
            pass # تجاهل الخطأ بصمت إذا فشل التخصيص

        self.master.wait_window(dialog)

    def resume_from_file(self):
        """Allows a user to resume a download by selecting its target file and providing the original URL."""
        selected_path = filedialog.askopenfilename(
            initialdir=self.get_default_download_folder(),
            title=self._('select_file_to_resume'),
            parent=self.master
        )

        if not selected_path:
            return  # User cancelled

        # --- Enhanced logic to handle selecting a part file by mistake ---
        save_path = selected_path
        if ".idm-parts" in selected_path:
            path_parts = selected_path.split(".idm-parts")
            if len(path_parts) > 0:
                save_path = path_parts[0]

        # Check if this download is already in the current list
        for item in self.downloads.values():
            if os.path.normpath(item.save_location) == os.path.normpath(save_path):
                messagebox.showinfo(self._('information'), self._('download_already_in_list'), parent=self.master)
                return

        # Check if the corresponding .idm-parts directory exists
        temp_dir_path = f"{save_path}.idm-parts"
        if not os.path.isdir(temp_dir_path):
            messagebox.showerror(self._('error_title'), self._('no_parts_found'), parent=self.master)
            return
        
        # --- تحسين: اكتشاف عدد الأجزاء تلقائياً ---
        try:
            part_files = [f for f in os.listdir(temp_dir_path) if f.startswith('part') and f[4:].isdigit()]
            if not part_files:
                messagebox.showerror(self._('error_title'), self._('no_parts_found'), parent=self.master)
                return
            num_segments = len(part_files)
        except Exception as e:
            messagebox.showerror(self._('error_title'), f"Failed to read temporary directory:\n{e}", parent=self.master)
            return

        # Ask for the original URL
        url = simpledialog.askstring(self._('resume_title'), self._('resume_prompt'), parent=self.master)

        if url:
            # add_download_item will calculate progress from existing parts
            self.add_download_item(url, save_path, num_segments=num_segments)

    def add_download_from_browser(self, url, cookies=None):
        """A thread-safe method to add and start a download coming from the local web server directly."""
        # This is called from the server thread, so we use `after` to run on the main UI thread.
        self.master.after(0, self.start_download_from_browser, url, cookies)

    def start_download_from_browser(self, url, cookies):
        """Adds and starts a download directly without showing the dialog."""
        # 2. Determine save path
        default_folder = self.get_default_download_folder()
        suggested_filename = self.suggest_filename_from_url(url)
        initial_save_path = os.path.join(default_folder, suggested_filename)

        # 1. Check for duplicate save path
        if any(item.save_location == initial_save_path for item in self.downloads.values()):
            # If a download to the same path exists, just bring the window to the front
            # to alert the user, but don't add a new one.
            if self.toaster:
                self.toaster.show_toast("تحميل مكرر", f"الملف '{suggested_filename}' موجود بالفعل في القائمة.", duration=5, threaded=True)
            self.master.deiconify()
            self.master.lift()
            # Select the existing item in the list
            existing_item_id = next((item_id for item_id, item in self.downloads.items() if item.save_location == initial_save_path), None)
            if existing_item_id:
                self.tree.selection_set(existing_item_id)
            return

        # 3. Ensure unique filename
        final_save_path = self.get_unique_save_path(initial_save_path)

        # 4. Add the item (using a default of 8 segments)
        item = self.add_download_item(url, final_save_path, num_segments=8, cookies=cookies)

        # 5. Start the download
        self.start_download(item)
        
        # 6. Bring window to front to show the new download
        self.master.deiconify()
        self.master.lift()
        
    def add_download_item(self, url, save_path, num_segments=8, scheduled_time=None, category='uncategorized', state_from_session=None, cookies=None):
        """Adds a new download item to the list and UI, calculating progress from existing part files."""
        # --- Auto-categorization Logic ---
        # If the category is the default 'uncategorized', try to determine it from the filename.
        if category == 'uncategorized':
            category = self.get_category_from_filename(os.path.basename(save_path))

        item = DownloadItem(url, save_path, self)
        item.num_segments = num_segments # Set the number of segments from the dialog
        item.category = category

        if state_from_session:
            item.id = state_from_session.get('id', item.id)
            item.total_size = state_from_session.get('total_size', 0)
            item.downloaded_size = state_from_session.get('downloaded_size', 0)
            # Let the session file override the num_segments if it exists there
            item.num_segments = state_from_session.get('num_segments', num_segments)
            item.cookies = state_from_session.get('cookies') # تحميل الكوكيز من الجلسة
            item.category = state_from_session.get('category', 'uncategorized')
            
            saved_time_str = state_from_session.get('scheduled_time')
            if saved_time_str:
                item.scheduled_time = datetime.datetime.fromisoformat(saved_time_str)
                item.state = DownloadState.SCHEDULED
                item.status_text = self._('scheduled_for', time=item.scheduled_time.strftime('%Y-%m-%d %H:%M'))
            else:
                item.state = DownloadState[state_from_session.get('state', 'IDLE')]
                item.status_text = self._('paused_status') if item.state != DownloadState.COMPLETE else self._('complete')
        else:
            # تعيين الكوكيز للتحميلات الجديدة
            item.cookies = cookies

        # --- منطق حساب التقدم المنقول ---
        # سواء من جلسة سابقة أو إضافة يدوية، تحقق من الأجزاء الموجودة
        downloaded_size = 0
        if os.path.isdir(item.temp_dir):
            for part_filename in os.listdir(item.temp_dir):
                part_file = os.path.join(item.temp_dir, part_filename)
                if os.path.isfile(part_file):
                    downloaded_size += os.path.getsize(part_file)
        item.downloaded_size = downloaded_size

        # Handle new scheduled items that are not from session
        if scheduled_time and not state_from_session:
            item.scheduled_time = scheduled_time
            item.state = DownloadState.SCHEDULED
            item.status_text = self._('scheduled_for', time=item.scheduled_time.strftime('%Y-%m-%d %H:%M'))

        self.downloads[item.id] = item

        # Add new category to UI if it doesn't exist
        if item.category not in self.categories:
            self.categories[item.category] = item.category # Use key as name
            self.category_tree.insert('', 'end', iid=item.category, text=item.category)
        
        # إضافة العنصر إلى Treeview
        progress_str = f"{(item.downloaded_size / item.total_size * 100):.1f}%" if item.total_size > 0 else "0.0%"
        # Only add to tree if it matches the current filter
        if self.current_category == 'all' or self.current_category == item.category:
            item.treeview_item = self.tree.insert("", "end", iid=item.id, values=(
                os.path.basename(item.save_location),
                self.format_size(item.total_size),
                progress_str,
                "-", # Speed
                "-", # Time Left
                item.status_text
            ))
        return item

    def get_file_info_and_start_download(self, item):
        """يحصل على حجم الملف ثم يبدأ التحميل متعدد الأجزاء."""
        try:
            # محاولة الحصول على الحجم الكلي باستخدام طلب HEAD
            response = self.scraper.head(item.url, timeout=20, allow_redirects=True, headers=self.get_request_headers(item))
            response.raise_for_status()
            item.total_size = int(response.headers.get('content-length', 0))

            if item.total_size <= 0:
                 # إذا لم يعمل HEAD أو لم يعط حجمًا، جرب GET مع نطاق صغير
                 headers = self.get_request_headers(item)
                 headers['Range'] = 'bytes=0-1023'
                 response = self.scraper.get(item.url, headers=headers, stream=True, timeout=20, allow_redirects=True)
                 response.raise_for_status()
                 content_range = response.headers.get('Content-Range')
                 if content_range:
                     item.total_size = int(content_range.split('/')[-1])
                 else:
                     # إذا لم نحصل على الحجم حتى الآن، لا يمكننا تقسيم الملف
                     item.state = DownloadState.PERMANENT_ERROR
                     item.status_text = self._('cannot_determine_size')
                     self.master.after(0, lambda: messagebox.showerror("خطأ", "لا يمكن تحديد حجم الملف. لا يمكن إجراء تحميل متعدد الأجزاء."))
                     return # لا يمكن المتابعة

            # إذا وصلنا إلى هنا، لدينا الحجم الكلي (أو 0 إذا كان غير مدعوم تمامًا)
            self.master.after(0, self.start_multi_part_download, item)

            # --- إنشاء نافذة التقدم المصغرة ---
            self.master.after(0, self.show_mini_progress_window, item)


        except Exception as e: # Catches Cloudscraper errors and others
            self.master.after(0, self.handle_download_failure_ui, item)
            item.state = DownloadState.PERMANENT_ERROR
            item.status_text = self._('permanent_error')
            # Use a default argument (e=e) to capture the value of 'e' at definition time
            self.master.after(0, lambda e=e: messagebox.showerror("خطأ في الحصول على معلومات الملف", f"حدث خطأ أثناء الحصول على معلومات الملف:\n{e}"))

    def get_request_headers(self, item):
        """ينشئ ترويسات الطلب مع إضافة الكوكيز إذا كانت موجودة."""
        headers = self.request_headers.copy()
        if item.cookies:
            headers['Cookie'] = item.cookies
        return headers

    def show_mini_progress_window(self, item):
        """ينشئ أو يركز على نافذة التقدم المصغرة."""
        if item.mini_progress_window and item.mini_progress_window.winfo_exists():
            item.mini_progress_window.lift()
            item.mini_progress_window.focus()
        else:
            item.mini_progress_window = MiniProgressWindow(self.master, item)


    def start_multi_part_download(self, item):
        """يبدأ عملية التحميل متعدد الأجزاء."""
        if item.total_size <= 0:
            # إذا كان الحجم لا يزال غير معروف، نعود للتحميل العادي بخيط واحد
            item.status_text = self._('unknown_size_single_thread') # Assuming this key exists
            item.num_segments = 1 # تحميل كجزء واحد

        # إنشاء المجلد المؤقت للأجزاء
        os.makedirs(item.temp_dir, exist_ok=True)

        item.state = DownloadState.DOWNLOADING
        self.update_ui_for_selection()

        # إعداد متغيرات الأجزاء
        item.segments = []
        item.pause_event.set() # Ensure download can run
        item.segment_error_event.clear()
        item.permanent_error_event.clear()

        # لا تقم بإعادة تعيين downloaded_size هنا.
        # سيتم تحديثه بشكل صحيح في حلقة المراقبة بناءً على أحجام الأجزاء الفعلية.
        
        segment_ranges = []
        if item.total_size > 0:
            segment_size = item.total_size // item.num_segments
            for i in range(item.num_segments):
                start_byte = i * segment_size
                end_byte = start_byte + segment_size - 1
                if i == item.num_segments - 1: # الجزء الأخير يأخذ ما تبقى
                    end_byte = item.total_size - 1
                segment_ranges.append((start_byte, end_byte))
        else: # حجم غير معروف، جزء واحد فقط
             segment_ranges.append((0, None)) # من البداية إلى النهاية
             item.num_segments = 1 # تأكيد أننا نتعامل مع جزء واحد فقط

        # بدء خيوط تحميل الأجزاء
        for i in range(item.num_segments):
            start_byte, end_byte = segment_ranges[i]
            segment_filename = os.path.join(item.temp_dir, f"part{i}")
            total_size = (end_byte - start_byte + 1) if item.total_size > 0 else 0
            segment = SegmentData(index=i, filename=segment_filename, total_size=total_size)
            item.segments.append(segment)

            # We no longer delete existing part files here to support resuming.

            thread = threading.Thread(target=self.download_segment, args=(item, start_byte, end_byte, i))
            thread.daemon = True
            segment.thread = thread
            thread.start()

        # بدء خيط مراقبة وتجميع الأجزاء
        monitor_thread = threading.Thread(target=self.monitor_and_combine_segments, args=(item,))
        monitor_thread.daemon = True
        monitor_thread.start()

        item.status_text = self._('downloading')


    def download_segment(self, item, original_segment_start_byte, original_segment_end_byte, segment_index):
        """دالة لتنزيل جزء محدد من الملف في خيط منفصل."""
        try:
            # Check for immediate cancellation or error before starting the request
            if item.cancel_event.is_set() or item.segment_error_event.is_set():
                 return # Exit thread early
            
            segment = item.segments[segment_index]
            segment_filename = segment.filename
            segment_total_size_for_this_part = segment.total_size
            resumed_bytes = 0
            file_mode = 'wb'

            if os.path.exists(segment_filename):
                resumed_bytes = os.path.getsize(segment_filename)
                if segment_total_size_for_this_part > 0 and resumed_bytes > segment_total_size_for_this_part:
                    # The part file is larger than expected, possibly corrupted. Restart it.
                    try:
                        os.remove(segment_filename)
                        resumed_bytes = 0
                    except OSError:
                        # If deletion fails, 'wb' mode below will truncate it.
                        resumed_bytes = 0 
                elif resumed_bytes > 0:
                    file_mode = 'ab'

            # This lock is not strictly needed here as it's before the network request, but it's good practice
            # if other threads were to modify this. Let's keep it for safety.
            segment.downloaded_size = resumed_bytes

            request_actual_start_byte = original_segment_start_byte + resumed_bytes
            
            if segment_total_size_for_this_part > 0 and resumed_bytes >= segment_total_size_for_this_part:
                self.master.after(0, lambda idx=segment_index: self.update_segment_ui(idx, 100, "مكتمل (مستأنف)"))
                return # Segment already downloaded

            headers = {}
            if original_segment_end_byte is not None: # If not downloading the whole file as one unknown-size segment
                if request_actual_start_byte > original_segment_end_byte: # Should be caught by resumed_bytes check
                    return 
                headers['Range'] = f'bytes={request_actual_start_byte}-{original_segment_end_byte}'

            # Add the default User-Agent to the headers for this segment request
            response = self.scraper.get(item.url, headers={**self.get_request_headers(item), **headers}, stream=True, timeout=60, allow_redirects=True)
            response.raise_for_status()

            if segment_index == 0 and item.total_size == 0:
                 content_length = response.headers.get('content-length')
                 if content_length:
                     # إذا حصلنا على Content-Length هنا، فهذا هو حجم الملف الكلي
                     # وهذا يعني أن الخادم لم يدعم Range أو أننا حملنا جزءًا واحدًا
                     # نحدث الحجم الكلي ونعتبر هذا الجزء هو الملف بأكمله
                     with overall_progress_lock:
                         item.total_size = int(content_length)
                         segment.total_size = item.total_size
                         segment_total_size_for_this_part = item.total_size

            # If server ignores Range and sends full content, or for single segment downloads
            # 'content-length' here would be the size of the *remaining* part if Range was respected,
            # or full size if Range was ignored or not sent.

            downloaded_this_segment = resumed_bytes # Initialize with what's already on disk for this segment
            last_speed_sample_time = time.time()
            downloaded_since_last_sample = 0

            # Use file_mode to correctly handle resume by appending or starting fresh.
            with open(segment_filename, file_mode) as f:
                for chunk in response.iter_content(chunk_size=65536): # 64KB chunk size
                    if item.cancel_event.is_set() or item.segment_error_event.is_set():
                        break # الخروج من الحلقة إذا تم الإلغاء أو حدث خطأ في جزء آخر

                    item.pause_event.wait() # This will block if pause_event is cleared (paused).
                    
                    # --- Speed Limit Logic (Moved to the correct place) ---
                    # Consume tokens from the bucket. This will block if the speed limit is reached.
                    self.speed_limiter.consume(len(chunk))

                    f.write(chunk)
                    chunk_len = len(chunk)
                    downloaded_this_segment += chunk_len
                    downloaded_since_last_sample += chunk_len

                    # تحديث التقدم الخاص بهذا الجزء والمتغير الكلي
                    with overall_progress_lock:
                        segment.downloaded_size = downloaded_this_segment
                        # التقدم الكلي سيتم حسابه في دالة المراقبة

                    current_time = time.time()
                    time_since_last_sample = current_time - last_speed_sample_time
                    if time_since_last_sample >= 0.5:
                         # يمكن حساب سرعة كل جزء هنا إذا أردت عرضها
                         last_speed_sample_time = current_time
                         downloaded_since_last_sample = 0

            # بعد الانتهاء من حلقة التحميل لهذا الجزء
            if item.cancel_event.is_set() or item.segment_error_event.is_set():
                 pass # سيتم التعامل معه في monitor_and_combine_segments
            elif segment_total_size_for_this_part == 0 and downloaded_this_segment > 0: # حجم غير معروف واكتمل
                 # If total size was unknown, and this is the only segment, update its total size
                 if item.num_segments == 1 and segment_index == 0:
                     segment.total_size = downloaded_this_segment # Update the actual size
            else: # توقف غير مكتمل (قد يكون خطأ اتصال لم يتم التقاطه كـ RequestException)
                 if not (downloaded_this_segment >= segment_total_size_for_this_part and segment_total_size_for_this_part > 0):
                    item.segment_error_event.set() # إشارة إلى خطأ

        except HTTPError as e:
            # خطأ في بروتوكول HTTP (مثل 404, 403, 500)
            status_code = e.response.status_code
            item.error_message = f"خطأ HTTP {status_code}: {e.response.reason}"
            if 400 <= status_code < 500 and status_code not in [408, 429]: # 408=Timeout, 429=Too Many Requests
                # أخطاء العميل (4xx) تعتبر دائمة في العادة
                item.permanent_error_event.set()
            else:
                # أخطاء الخادم (5xx) أو الأخطاء القابلة لإعادة المحاولة (408, 429)
                item.segment_error_event.set()
        except (ConnectionError, Timeout) as e:
            # أخطاء الشبكة والاتصال
            item.error_message = f"خطأ في الشبكة: {type(e).__name__}"
            item.segment_error_event.set() # إشارة إلى خطأ قابل لإعادة المحاولة
        except OSError as e:
            # خطأ في نظام التشغيل، مثل "القرص ممتلئ"
            item.error_message = f"خطأ في نظام الملفات: {e}"
            item.permanent_error_event.set() # هذا خطأ دائم
        except RequestException as e:
            # التقاط أي استثناءات أخرى من مكتبة الطلبات
            item.error_message = f"خطأ في الطلب: {type(e).__name__}"
            item.segment_error_event.set()
        except Exception as e:
            item.error_message = f"خطأ غير متوقع: {e}"
            item.permanent_error_event.set() # اعتباره خطأ دائمًا لأنه غير متوقع

    def monitor_and_combine_segments(self, item):
        """يراقب تقدم الأجزاء، يحدث شريط التقدم الكلي، ويقوم بالتجميع عند الانتهاء."""
        start_time = time.time()
        last_overall_update_time = time.time()
        last_downloaded_size = 0

        # حلقة مراقبة
        while not item.cancel_event.is_set() and not item.segment_error_event.is_set() and not item.permanent_error_event.is_set():
            all_segments_done = True
            current_total_downloaded = 0
            
            with overall_progress_lock:
                current_total_downloaded = sum(seg.downloaded_size for seg in item.segments)
                # تحقق مما إذا كانت جميع الأجزاء قد وصلت إلى حجمها المتوقع
                # هذا التحقق معقد إذا كان الحجم الكلي غير معروف أو إذا فشل جزء
                # للتبسيط، نعتبر الجزء مكتملًا إذا انتهى الخيط الخاص به
                all_segments_done = all(not seg.thread.is_alive() for seg in item.segments if seg.thread)
                
            item.downloaded_size = current_total_downloaded # تحديث التقدم الكلي

            # تحديث شريط التقدم الكلي ومعلومات السرعة/الوقت المتبقي
            current_time = time.time()

            if current_time - last_overall_update_time >= 0.5:
                speed = (item.downloaded_size - last_downloaded_size) / (current_time - last_overall_update_time) if (current_time - last_overall_update_time) > 0 else 0
                item.speed = speed

                if item.total_size > 0 and speed > 0:
                    remaining_bytes = item.total_size - item.downloaded_size
                    time_left = remaining_bytes / speed
                    item.time_left = time_left
                else:
                    item.time_left = float('inf')

                last_overall_update_time = current_time
                last_downloaded_size = item.downloaded_size

            if all_segments_done:
                break # الخروج من حلقة المراقبة إذا انتهت جميع الخيوط

            time.sleep(0.1) # انتظر قليلاً قبل التحقق مرة أخرى

        # بعد الخروج من حلقة المراقبة
        item.speed = 0 # Reset speed when not actively downloading
        if item.cancel_event.is_set() or item.segment_error_event.is_set() or item.permanent_error_event.is_set():
            self.master.after(0, self.handle_cancel_or_error, item)
            self.master.after(100, self.process_download_queue) # Try to start next download
        else:
            # جميع الأجزاء انتهت بنجاح (بافتراض عدم وجود أخطاء لم يتم التقاطها)
            self.master.after(0, self.combine_segments, item)


    def handle_cancel_or_error(self, item):
        """ينظف بعد الإلغاء أو يتعامل مع الخطأ القابل لإعادة المحاولة أو الخطأ الدائم."""
        if item.permanent_error_event.is_set():
            # التعامل مع الخطأ الدائم
            self.handle_permanent_error(item, item.error_message or self._('permanent_error'))
            return  # Exit early

        self.handle_download_failure_ui(item)

        if item.segment_error_event.is_set():
            # خطأ في التحميل، قم بجدولة إعادة المحاولة
            item.status_text = item.error_message or self._('error_retrying')
            item.state = DownloadState.ERROR_RETRYING
            self.update_ui_for_selection()

            if self.toaster:
                try:
                    self.toaster.show_toast(
                        "خطأ في التحميل",
                        f"حدث خطأ أثناء تحميل '{os.path.basename(item.save_location)}'. سيتم إعادة المحاولة بعد 30 ثانية.",
                        duration=10,
                        threaded=True
                    )
                except Exception as e:
                    print(f"Failed to show retry notification: {e}")
            
            # لا تحذف الملفات المؤقتة للاستئناف
            # جدولة إعادة المحاولة
            if item._retry_timer: self.master.after_cancel(item._retry_timer)
            item._retry_timer = self.master.after(30000, self.start_download, item) # 30000 ms = 30 seconds
        elif item.cancel_event.is_set():
            # إلغاء من قبل المستخدم
            item.state = DownloadState.CANCELLED
            item.status_text = self._('cancelled')
            # تم تعديل المنطق: لم نعد نحذف الملفات المؤقتة تلقائيًا عند الإلغاء
            # سيتم سؤال المستخدم عند الإزالة أو يمكنه الحذف يدويًا
            self.update_ui_for_selection()

    def handle_download_failure_ui(self, item):
        """يغلق نافذة التقدم المصغرة بعد فترة عند الفشل."""
        if item.mini_progress_window and item.mini_progress_window.winfo_exists():
            # لا تغلق النافذة فورًا، دع المستخدم يرى الخطأ
            self.master.after(10000, lambda: item.mini_progress_window.destroy() if item.mini_progress_window else None)

    def handle_permanent_error(self, item, error_message):
        """يتعامل مع الأخطاء التي لا يمكن التعافي منها (مثل 404)."""
        item.state = DownloadState.PERMANENT_ERROR
        item.status_text = error_message or self._('permanent_error')
        messagebox.showerror("خطأ دائم", error_message)

        if self.toaster:
            try:
                self.toaster.show_toast(
                    "فشل التحميل",
                    f"حدث خطأ دائم أثناء تحميل '{os.path.basename(item.save_location)}'.",
                    duration=10,
                    threaded=True
                )
            except Exception as e:
                print(f"Failed to show error notification: {e}")
        
        self.handle_download_failure_ui(item)
        # لم نعد نحذف الملفات تلقائيًا هنا أيضًا

    def combine_segments(self, item):
        """يدمج الملفات المؤقتة في الملف النهائي."""
        item.state = DownloadState.COMBINING
        item.status_text = self._('combining')

        try:
            with open(item.save_location, 'wb') as final_file:
                for segment in sorted(item.segments, key=lambda s: s.index):
                    segment_filename = segment.filename
                    if item.cancel_event.is_set(): # تحقق من الإلغاء أثناء التجميع
                         item.status_text = self._('cancelling')
                         return # الخروج قبل إكمال التجميع
                         
                    if not os.path.exists(segment_filename):
                        raise IOError(f"الملف الجزئي مفقود أثناء التجميع: {segment_filename}")

                    with open(segment_filename, 'rb') as segment_file_part:
                        final_file.write(segment_file_part.read())
            
            # إذا اكتمل التجميع بنجاح
            item.state = DownloadState.COMPLETE
            item.status_text = self._('complete')

            # إغلاق نافذة التقدم المصغرة بعد فترة للسماح للمستخدم برؤية الاكتمال
            if item.mini_progress_window and item.mini_progress_window.winfo_exists():
                self.master.after(10000, lambda: item.mini_progress_window.destroy() if item.mini_progress_window else None)

            # إرسال إشعار سطح المكتب
            if self.toaster:
                try:
                    self.toaster.show_toast(
                        "اكتمل التحميل",
                        f"تم تحميل الملف '{os.path.basename(item.save_location)}' بنجاح.",
                        duration=10,
                        threaded=True
                    )
                except Exception as e:
                    print(f"Failed to show completion notification: {e}")
            
            # حذف الملفات المؤقتة بعد النجاح
            self.master.after(100, self.process_download_queue) # Start next download
            for segment_file in [s.filename for s in item.segments]:
                try:
                    if os.path.exists(segment_file):
                        os.remove(segment_file)
                except OSError: pass
            try:
                if os.path.exists(item.temp_dir):
                    os.rmdir(item.temp_dir) # حذف المجلد المؤقت الفارغ
            except OSError: pass # تجاهل الخطأ إذا لم يكن المجلد فارغًا لسبب ما
        except IOError as e:
            item.state = DownloadState.PERMANENT_ERROR
            item.status_text = self._('combining_error') # Assuming this key exists
            self.master.after(0, lambda: messagebox.showerror("خطأ في التجميع", str(e)))
            self.handle_download_failure_ui(item)
        except Exception as e:
            item.state = DownloadState.PERMANENT_ERROR
            item.status_text = self._('fatal_error') # Assuming this key exists
            self.master.after(0, lambda: messagebox.showerror("خطأ فادح", str(e)))
            self.handle_download_failure_ui(item)

    def pause_download(self, item):
        if item.state == DownloadState.DOWNLOADING:
            item.state = DownloadState.PAUSED
            item.status_text = self._('paused_status')
            item.pause_event.clear() # Clear the event to make wait() block
            self.update_ui_for_selection()

    def cancel_download(self, item):
        """Cancels a specific download item, not necessarily the selected one."""
        if not item: return
        self.cancel_item(item)

    def cancel_selected_download(self):
        item = self.get_selected_download_item() # Get the selected item from the tree
        if item.state in [DownloadState.DOWNLOADING, DownloadState.PAUSED, DownloadState.ERROR_RETRYING, DownloadState.COMBINING]:
            item.cancel_event.set()
            item.pause_event.set() # Unblock any paused threads so they can see the cancel signal
            if item._retry_timer:
                self.master.after_cancel(item._retry_timer)
                item._retry_timer = None
            item.status_text = self._('cancelling')
            self.update_ui_for_selection()

    def cancel_item(self, item):
        """Helper function to cancel a download item."""
        if item and item.state in [DownloadState.DOWNLOADING, DownloadState.PAUSED, DownloadState.ERROR_RETRYING, DownloadState.COMBINING, DownloadState.SCHEDULED]:
            item.cancel_event.set()
            item.pause_event.set() # Unblock any paused threads so they can see the cancel signal
            if item._retry_timer:
                self.master.after_cancel(item._retry_timer)
                item._retry_timer = None
            item.status_text = self._('cancelling')

    def get_startup_executable_path(self):
        """يحدد الأمر الذي سيتم تشغيله عند بدء التشغيل."""
        # إذا كان يعمل كملف تنفيذي مجمّد (مثل PyInstaller)
        if getattr(sys, 'frozen', False):
            return sys.executable
        # إذا كان يعمل كسكربت
        else:
            # استخدم pythonw.exe للتشغيل في الخلفية بدون نافذة طرفية
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            script_path = os.path.abspath(sys.argv[0])
            return f'"{python_exe}" "{script_path}"'

    def set_startup(self, enable=True):
        """يضيف أو يزيل التطبيق من بدء تشغيل ويندوز."""
        app_name = "Advanced Download Manager" # الاسم الذي سيظهر في مدير المهام
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                executable_path = self.get_startup_executable_path()
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, executable_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass # لا بأس إذا كان المفتاح غير موجود
            winreg.CloseKey(key)
            return True
        except Exception as e:
            messagebox.showerror("خطأ في التسجيل", f"فشل تعديل إعدادات بدء التشغيل:\n{e}", parent=self.master)
            return False

    def is_in_startup(self):
        """يتحقق مما إذا كان التطبيق مهيأ للعمل عند بدء التشغيل."""
        app_name = "Advanced Download Manager"
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return True
        except (FileNotFoundError, Exception):
            return False

    def remove_completed_downloads(self):
        """Removes all completed download items from the list."""
        completed_ids = [item_id for item_id, item in self.downloads.items() if item.state == DownloadState.COMPLETE]

        if not completed_ids:
            messagebox.showinfo(self._('information'), self._('no_completed_downloads'), parent=self.master)
            return

        if messagebox.askyesno(
            self._('confirm_removal_title'),
            self._('confirm_remove_completed_msg', count=len(completed_ids)),
            parent=self.master
        ):
            for item_id in completed_ids:
                if item_id in self.downloads:
                    del self.downloads[item_id]
                if self.tree.exists(item_id):
                    self.tree.delete(item_id)
            
            self.update_ui_for_selection()
            self.status_label.config(text=self._('removed_completed_success', count=len(completed_ids)))


    def remove_selected_download(self):
        item = self.get_selected_download_item()
        if not item: return

        if item.state in [DownloadState.DOWNLOADING, DownloadState.COMBINING]:
            if not messagebox.askyesno("تحذير", "التحميل نشط. هل تريد إلغاءه وإزالته؟"):
                return
            self.cancel_selected_download()
        
        # تأكيد الإزالة من القائمة
        if messagebox.askyesno("تأكيد الإزالة", "هل تريد بالتأكيد إزالة هذا التحميل من القائمة؟", parent=self.master):
            should_delete_final_file = False
            
            # إذا كان التحميل مكتملاً والملف موجود، اسأل عن حذفه من القرص
            if item.state == DownloadState.COMPLETE and os.path.exists(item.save_location):
                if messagebox.askyesno("حذف الملف من القرص", f"هل تريد أيضًا حذف الملف المحفوظ '{os.path.basename(item.save_location)}' نهائيًا من القرص؟", icon='warning', parent=self.master):
                    should_delete_final_file = True
            
            # اسأل عن حذف الملفات المؤقتة إذا كان التحميل في حالة مناسبة
            elif item.state in [DownloadState.PAUSED, DownloadState.CANCELLED, DownloadState.ERROR_RETRYING, DownloadState.PERMANENT_ERROR]:
                if messagebox.askyesno("تنظيف", "هل تريد أيضًا حذف الملفات المؤقتة (.part) المرتبطة بهذا التحميل؟", parent=self.master):
                    self.cleanup_temp_files(item)

            # --- تنفيذ الحذف ---
            if should_delete_final_file:
                try:
                    os.remove(item.save_location)
                    # Also clean up any lingering temp files associated with it
                    self.cleanup_temp_files(item)
                except OSError as e:
                    messagebox.showerror("خطأ في الحذف", f"لم يتمكن من حذف الملف من القرص:\n{e}", parent=self.master)
                    # لا نوقف العملية، فقط نعلم المستخدم ونكمل إزالة العنصر من القائمة

            # --- إزالة العنصر من البرنامج ---
            if item.id in self.downloads:
                # إغلاق النوافذ المفتوحة المرتبطة
                if item.details_window and item.details_window.winfo_exists(): item.details_window.destroy()
                if item.mini_progress_window and item.mini_progress_window.winfo_exists(): item.mini_progress_window.destroy()
                
                # إلغاء أي مؤقتات
                if item._retry_timer: self.master.after_cancel(item._retry_timer)
                
                del self.downloads[item.id]

            # إزالة العنصر من الواجهة
            if self.tree.exists(item.id):
                self.tree.delete(item.id)
            
            self.update_ui_for_selection()

    def cleanup_selected_item_files(self, item=None):
        """ينظف الملفات المؤقتة للعنصر المحدد حاليًا."""
        item = item or self.get_selected_download_item()
        if not item:
            return
        
        deleted_count = self.cleanup_temp_files(item)
        
        if deleted_count > 0:
            messagebox.showinfo("نجاح", f"تم حذف {deleted_count} ملفًا مؤقتًا بنجاح.", parent=self.master)
            item.reset(reset_size=True)
        else:
            messagebox.showinfo("معلومة", "لم يتم العثور على ملفات مؤقتة للحذف.", parent=self.master)

    def delete_selected_file_from_disk(self, item=None):
        """Deletes the selected download's file from the disk and removes the item from the list."""
        item = item or self.get_selected_download_item()
        if not item:
            return

        # Check if the file actually exists
        if not os.path.exists(item.save_location):
            messagebox.showinfo(self._('information'), self._('file_not_found_on_disk'), parent=self.master)
            return

        # Confirmation message
        if messagebox.askyesno(
            self._('confirm_delete_file_title'),
            self._('confirm_delete_file_message', filename=os.path.basename(item.save_location)),
            icon='warning',
            parent=self.master
        ):
            # Cancel any active download process
            if item.state in [DownloadState.DOWNLOADING, DownloadState.COMBINING, DownloadState.ERROR_RETRYING]:
                self.cancel_item(item)
                time.sleep(0.1) # Give it a moment to process cancellation

            # Delete the final file
            try:
                os.remove(item.save_location)
            except OSError as e:
                messagebox.showerror(self._('error_title'), f"Could not delete file from disk:\n{e}", parent=self.master)
                return # Don't proceed if file deletion failed

            # Also clean up temporary files
            self.cleanup_temp_files(item=item)

            # Remove the item from the application's memory and UI
            if item.id in self.downloads:
                if item.details_window and item.details_window.winfo_exists(): item.details_window.destroy()
                if item.mini_progress_window and item.mini_progress_window.winfo_exists(): item.mini_progress_window.destroy()
                if item._retry_timer: self.master.after_cancel(item._retry_timer)
                del self.downloads[item.id]
            if self.tree.exists(item.id):
                self.tree.delete(item.id)
            self.update_ui_for_selection()

    def refresh_download_link(self, item=None):
        """Opens the browser for the user to get a new link, then resumes the download."""
        item = item or self.get_selected_download_item()
        if not item or item.state != DownloadState.PERMANENT_ERROR:
            return

        # 1. Open the browser to the old URL
        try:
            webbrowser.open_new(item.url)
        except Exception as e:
            messagebox.showwarning(self._('error_title'), f"Could not open browser: {e}", parent=self.master)

        # 2. Ask the user for the new URL
        new_url = simpledialog.askstring(
            self._('refresh_download_link'),
            self._('paste_new_link_prompt'),
            parent=self.master
        )

        if new_url and new_url.strip():
            # 3. Update the item with the new URL
            item.url = new_url.strip()

            # 4. Reset the item's state to be ready for a new download attempt
            item.state = DownloadState.IDLE
            item.status_text = self._('ready')
            item.permanent_error_event.clear() # Clear the error flag
            self.start_download(item)

    def cleanup_temp_files(self, item=None):
        """يحذف جميع ملفات .part المرتبطة بعنصر تحميل معين."""
        item = item or self.get_selected_download_item()
        if not item or not os.path.isdir(item.temp_dir): return 0
        
        for i in range(5):  # Retry up to 5 times
            try:
                # Remove read-only attributes from files
                for filename in os.listdir(item.temp_dir):
                    filepath = os.path.join(item.temp_dir, filename)
                    os.chmod(filepath, stat.S_IWRITE)

                shutil.rmtree(item.temp_dir)
                return 1  # Return 1 to indicate the directory was removed
            except OSError as e:
                print(f"Could not delete temp directory {item.temp_dir}: {e}")
                if i < 4:
                    time.sleep(2)  # Wait for 2 seconds before retrying
                else:
                    return 0

    def on_item_select(self, event=None):
        """يتم استدعاؤها عند تحديد عنصر، وتقوم بتحديث أزرار التحكم فقط."""
        self.update_ui_for_selection()

    def show_mini_progress_window_on_double_click(self, event):
        """يفتح نافذة التقدم المصغرة للعنصر الذي تم النقر عليه مرتين."""
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        item = self.downloads.get(item_id)
        if not item:
            return

        # لا تفتح النافذة إلا إذا كان التحميل قد بدأ أو في حالة خطأ
        if item.state not in [DownloadState.DOWNLOADING, DownloadState.PAUSED, DownloadState.ERROR_RETRYING, DownloadState.PERMANENT_ERROR, DownloadState.COMBINING]:
            return
            
        self.show_mini_progress_window(item)

    def on_category_select(self, event=None):
        """Handles selection of a category in the category tree."""
        selected_ids = self.category_tree.selection()
        if not selected_ids:
            return
        
        category_id = selected_ids[0]
        if category_id != self.current_category:
            self.current_category = category_id
            # Cancel any pending search filter update since we are doing a full update now
            if self.search_timer:
                self.master.after_cancel(self.search_timer)
                self.search_timer = None
            self.apply_filters_and_update_view()

    def clear_search(self):
        """Clears the search variable, which in turn clears the entry and triggers a filter update."""
        self.search_var.set("")

    def on_search_text_changed(self, *args):
        """Manages clear button visibility and debounces the expensive filter action."""
        if self.search_var.get():
            self.clear_search_button.pack(side=tk.RIGHT, fill=tk.Y, padx=(2, 0))
        else:
            self.clear_search_button.pack_forget()

        # Check if debouncing is enabled in settings
        if self.settings.get('instant_search_enabled', True):
            if self.search_timer:
                self.master.after_cancel(self.search_timer)
            self.search_timer = self.master.after(300, self.apply_filters_and_update_view)
        else:
            # If disabled, filter immediately
            self.apply_filters_and_update_view()

    def apply_filters_and_update_view(self):
        """Shows/hides downloads in the main tree based on the selected category and search query."""
        # --- إعادة كتابة المنطق لحل مشكلة اختفاء الملفات ---
        search_term = self.search_var.get().lower().strip()

        # 1. الحصول على قائمة بالعناصر التي تطابق الفلاتر
        filtered_items = []
        for item in self.downloads.values():
            category_match = (self.current_category == 'all' or item.category == self.current_category)
            search_match = (not search_term or search_term in os.path.basename(item.save_location).lower())
            if category_match and search_match:
                filtered_items.append(item)

        # 2. إذا كان هناك ترتيب نشط، قم بترتيب القائمة المفلترة
        if self.sort_column:
            def get_sort_key(item):
                col = self.sort_column
                if col == "file": return os.path.basename(item.save_location).lower()
                elif col == "size": return item.total_size
                elif col == "progress": return (item.downloaded_size / item.total_size) if item.total_size > 0 else 0
                elif col == "speed": return item.speed
                elif col == "time_left": return item.time_left if item.time_left != float('inf') else 999999999
                elif col == "status": return item.status_text
                return 0
            filtered_items.sort(key=get_sort_key, reverse=self.sort_reverse)

        # 3. إخفاء جميع العناصر الحالية في الجدول
        for item_id in self.tree.get_children():
            self.tree.detach(item_id)

        # 4. إعادة إظهار العناصر المفلترة والمرتبة بالترتيب الصحيح
        for i, item in enumerate(filtered_items):
            if self.tree.exists(item.id):
                self.tree.move(item.id, '', i)

        # Show or hide the "No results" label
        if not filtered_items and (search_term or self.current_category != 'all'):
            self.no_results_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        else:
            self.no_results_label.place_forget()

    def show_details_window(self, item=None, event=None):
        """يفتح نافذة تفاصيل الأجزاء للعنصر المحدد."""
        # الحل النهائي: إذا لم يتم تمرير عنصر، حاول الحصول عليه من التحديد.
        # هذا يجعل الدالة تعمل بشكل صحيح سواء تم استدعاؤها من قائمة السياق (مع تمرير العنصر)
        # أو من أي مكان آخر يعتمد على التحديد.
        effective_item = item or self.get_selected_download_item()
        if not effective_item:
            return

        # تحقق مما إذا كانت النافذة موجودة بالفعل وبحالة جيدة
        if effective_item.details_window and effective_item.details_window.winfo_exists():
            effective_item.details_window.lift()
            effective_item.details_window.focus()
        else:
            # إذا لم تكن موجودة أو تم إغلاقها، أنشئ واحدة جديدة
            # أغلق أي نافذة تفاصيل قديمة قد تكون مفتوحة لعنصر آخر
            self.close_all_details_windows(except_item=effective_item)
            effective_item.details_window = DetailsWindow(self.master, effective_item)

    def update_ui_for_selection(self):
        item = self.get_selected_download_item()
        if not item:
            # No item selected, disable all action buttons
            self.action_button.config(text=self._('start'), state=tk.DISABLED, image=self.action_button.icon_start_disabled)
            self.cancel_button.config(state=tk.DISABLED, image=self.cancel_button.icon_disabled)
            self.remove_button.config(state=tk.DISABLED, image=self.remove_button.icon_disabled)
            return

        # An item is selected, enable the remove button
        self.remove_button.config(state=tk.NORMAL, image=self.remove_button.icon_color)

        action_text, action_icon_key, action_cmd, action_state, cancel_state = self.get_button_states(item)

        # Determine the correct icon for the action button
        if action_icon_key == 'pause':
            action_icon = self.action_button.icon_pause_color if action_state == tk.NORMAL else self.action_button.icon_pause_disabled
        elif action_icon_key == 'resume_file':
            action_icon = self.action_button.icon_resume_color
        else: # 'start'
            action_icon = self.action_button.icon_start_color if action_state == tk.NORMAL else self.action_button.icon_start_disabled

        self.action_button.config(text=action_text, command=action_cmd, state=action_state, image=action_icon)
        self.cancel_button.config(state=cancel_state, image=self.cancel_button.icon_color if cancel_state == tk.NORMAL else self.cancel_button.icon_disabled)

    def get_button_states(self, item):
        """Returns a tuple of (text, icon_key, command, action_state, cancel_state) for a given item."""
        state = item.state
        if state == DownloadState.PERMANENT_ERROR:
            return self._('refresh_download_link'), 'resume_file', self.refresh_download_link, tk.NORMAL, tk.DISABLED
        elif state in [DownloadState.IDLE, DownloadState.CANCELLED]:
            return self._('start'), 'start', self.toggle_selected_download, tk.NORMAL, tk.DISABLED
        elif state == DownloadState.DOWNLOADING:
            return self._('pause'), 'pause', self.toggle_selected_download, tk.NORMAL, tk.NORMAL
        elif state == DownloadState.PAUSED:
            return self._('resume'), 'start', self.toggle_selected_download, tk.NORMAL, tk.NORMAL
        elif state == DownloadState.ERROR_RETRYING:
            return self._('retry_now'), 'start', self.toggle_selected_download, tk.NORMAL, tk.NORMAL
        elif state == DownloadState.SCHEDULED:
            return self._('start_now'), 'start', self.toggle_selected_download, tk.NORMAL, tk.NORMAL
        else: # COMPLETE, COMBINING, GETTING_INFO, CANCELLING
            return self._('start'), 'start', None, tk.DISABLED, tk.DISABLED

    def update_ui_loop(self):
        """Updates the Treeview with the latest status of all downloads."""
        # --- تحسين الأداء: تحديث العناصر المرئية فقط ---
        
        # 1. الحصول على جميع العناصر الموجودة حاليًا في الجدول (التي تمت تصفيتها حسب الفئة)
        all_item_ids_in_view = self.tree.get_children()
        if not all_item_ids_in_view:
            self.update_ui_for_selection()
            self.master.after(1000, self.update_ui_loop)
            return

        # 2. تحديد العناصر المرئية بناءً على موضع شريط التمرير
        first, last = self.tree.yview()
        total_items = len(all_item_ids_in_view)
        
        # إضافة هامش (buffer) لجعل التمرير أكثر سلاسة
        buffer = 15 
        start_index = max(0, int(total_items * first) - buffer)
        end_index = min(total_items, int(total_items * last) + buffer)

        visible_item_ids = all_item_ids_in_view[start_index:end_index]

        # 3. المرور على العناصر المرئية فقط وتحديثها إذا لزم الأمر
        for i, item_id in enumerate(visible_item_ids):
            item = self.downloads.get(item_id)
            if not item or not item._is_dirty:
                continue

            # تحديد علامة الصف (فردي أو زوجي) بناءً على موقعه في القائمة المرئية
            row_tag = 'oddrow' if (start_index + i) % 2 == 0 else 'evenrow'

            progress_str = f"{(item.downloaded_size / item.total_size * 100):.1f}%" if item.total_size > 0 else "0.0%"
            speed_str = f"{self.format_size(item.speed)}/s" if item.speed > 0 else "-"
            time_left_str = self.format_time(item.time_left) if item.state == DownloadState.DOWNLOADING else self._('unknown')

            # تحديد لون الصف
            state_tag = {'complete': 'complete', 'paused': 'paused', 'downloading': 'downloading', 'error_retrying': 'error', 'permanent_error': 'error'}.get(item.state.name.lower())
            
            final_tags = (row_tag, state_tag) if state_tag else (row_tag,)

            self.tree.item(item_id, values=(
                os.path.basename(item.save_location),
                self.format_size(item.total_size),
                progress_str,
                speed_str,
                time_left_str,
                self._(item.status_text, time=item.scheduled_time.strftime('%Y-%m-%d %H:%M') if item.scheduled_time else "")
            ), tags=final_tags)
            item._is_dirty = False # إنزال العلم بعد التحديث
        
        self.update_ui_for_selection()
        self.master.after(1000, self.update_ui_loop) # تكرار كل ثانية

    def check_scheduled_downloads(self):
        """Checks for scheduled downloads that are due and starts them."""
        now = datetime.datetime.now()
        due_items = []
        for item in self.downloads.values():
            if item.state == DownloadState.SCHEDULED and item.scheduled_time and item.scheduled_time <= now:
                due_items.append(item)
        
        for item in due_items:
            self.start_download(item)
        self.master.after(5000, self.check_scheduled_downloads) # Check every 5 seconds

    def save_session(self):
        """Saves the state of non-completed downloads to a JSON file."""
        session_data = []
        for item in self.downloads.values():
            if item.state != DownloadState.COMPLETE:
                # Set downloading states to paused for next session
                save_state = item.state
                if save_state in [DownloadState.DOWNLOADING, DownloadState.COMBINING, DownloadState.ERROR_RETRYING, DownloadState.IDLE]:
                    save_state = DownloadState.PAUSED

                item_data = {
                    "id": item.id,
                    "url": item.url,
                    "save_location": item.save_location,
                    "state": save_state.name, # Save the enum member's name
                    "total_size": item.total_size,
                    "num_segments": item.num_segments,
                    "category": item.category,
                    "cookies": item.cookies, # حفظ الكوكيز
                }
                if item.scheduled_time and item.state == DownloadState.SCHEDULED:
                    item_data['scheduled_time'] = item.scheduled_time.isoformat()
                
                session_data.append(item_data)
        try:
            with open(DOWNLOAD_SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=4)
        except Exception as e:
            print(f"Error saving session: {e}")

    def load_session(self):
        """Loads downloads from a previous session."""
        if not os.path.exists(DOWNLOAD_SESSION_FILE):
            return
        
        try:
            with open(DOWNLOAD_SESSION_FILE, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            for saved_item in session_data:
                # الآن add_download_item يعيد حساب الحجم الذي تم تنزيله بنفسه
                self.add_download_item(
                    saved_item['url'], 
                    saved_item['save_location'], 
                    category=saved_item.get('category', 'uncategorized'),
                    state_from_session=saved_item
                )

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading session file (it might be corrupt): {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading session: {e}")

    def setup_tray_icon(self):
        """Sets up and runs the system tray icon in a separate thread."""
        if not pystray or not PillowAvailable:
            return

        try:
            icon_path = resource_path("icons/icon.ico")
            image = Image.open(icon_path)
            menu = pystray.Menu(
                pystray.MenuItem(lambda text: 'إظهار' if self.master.state() == 'withdrawn' else 'إخفاء', self.toggle_window),
                pystray.MenuItem('خروج', self.shutdown_application)
            )
            self.tray_icon = pystray.Icon("IDM", image, "مدير التحميل المتقدم", menu)

            # Run the icon in a non-daemon thread to ensure it's handled correctly on exit
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=False)
            tray_thread.start()
        except Exception as e:
            print(f"Failed to create system tray icon: {e}")

    def toggle_window(self):
        """Shows or hides the main window."""
        if self.master.state() == 'withdrawn':
            self.master.deiconify()
            self.master.lift()
        else:
            self.master.withdraw()

    def on_closing(self, force=False):
        """Handles the 'X' button click. Asks for confirmation before exiting."""
        self.shutdown_application(force=force)

    def shutdown_application(self, force=False):
        """Handles the complete shutdown of the application."""
        # Check for active downloads to display a more specific warning
        if force:
            confirm = True
        else:
            confirm = False
            active_downloads = any(
            item.state in [DownloadState.DOWNLOADING, DownloadState.COMBINING, DownloadState.ERROR_RETRYING] 
            for item in self.downloads.values()
        )
        message = self._('confirm_exit_msg')
        if active_downloads:
            message = self._('confirm_exit_active_msg')

            confirm = messagebox.askyesno(self._('confirm_exit_title'), message, parent=self.master)
        if confirm:
            if self.tray_icon:
                self.tray_icon.stop()
            self.save_session()
            # Cancel all running threads
            for item in self.downloads.values():
                if item.state in [DownloadState.DOWNLOADING, DownloadState.COMBINING, DownloadState.ERROR_RETRYING]:
                    item.cancel_event.set()
                    item.pause_event.set() # Allow threads to wake up and terminate
            self.master.destroy()
            # Attempt to gracefully shut down the server
            if hasattr(self, 'http_server') and self.http_server:
                # Shutdown needs to be from another thread
                threading.Thread(target=self.http_server.shutdown, daemon=True).start()
            sys.exit() # Ensure the process terminates cleanly

    def close_all_details_windows(self, except_item=None):
        """يغلق جميع نوافذ التفاصيل المفتوحة، باستثناء نافذة عنصر معين إذا تم تحديده."""
        for item in self.downloads.values():
            if item != except_item and item.details_window and item.details_window.winfo_exists():
                item.details_window.destroy()
                item.details_window = None

    def process_startup_downloads(self):
        """Resumes downloads on startup if the setting is enabled."""
        if True: # Always resume paused downloads on startup
            for item in list(self.downloads.values()): # Use list() to create a copy for safe iteration
                if item.state == DownloadState.PAUSED:
                    self.start_download(item)

    def start_local_server(self):
        """Starts a local HTTP server in a background thread to listen for download requests."""
        try:
            # Pass a reference of the app instance to the handler
            def handler(*args, **kwargs):
                BrowserRequestHandler(self, *args, **kwargs)

            self.http_server = HTTPServer(('127.0.0.1', self.server_port), handler)
            server_thread = threading.Thread(target=self.http_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            print(f"Local server started on port {self.server_port}.")
        except Exception as e:
            # Set server to None so we don't try to shut it down later
            self.http_server = None
            if isinstance(e, socket.error) and e.errno == 10048: # Address already in use
                message = f"المنفذ {self.server_port} مستخدم بالفعل. لن يعمل التكامل مع المتصفح."
                print(f"Warning: {message}")
                # Optionally show a non-blocking warning to the user
                # messagebox.showwarning("فشل بدء الخادم", message)
            else:
                print(f"An unexpected error occurred while starting the local server: {e}")

    def check_for_updates(self, on_startup=True):
        """Checks for a new version of the application in a background thread."""
        # لا تظهر رسالة "جاري التحقق" عند بدء التشغيل لتكون العملية صامتة
        if not on_startup:
            self.status_label.config(text="جاري التحقق من وجود تحديثات...")

        thread = threading.Thread(target=self._update_check_worker, args=(on_startup,), daemon=True)
        thread.start()

    def _update_check_worker(self, on_startup):
        """The actual worker function that performs the update check."""
        try:
            with request.urlopen(UPDATE_URL, timeout=10) as response:
                if response.status == 200:
                    version_info = json.loads(response.read().decode('utf-8'))
                    latest_version = version_info.get("latest_version")

                    # مقارنة بسيطة للإصدارات (يمكن تحسينها إذا كانت الأرقام معقدة)
                    if latest_version and latest_version > APP_VERSION:
                        self.master.after(0, self.prompt_user_to_update, version_info)
                    elif not on_startup:
                        # أظهر رسالة فقط إذا كان المستخدم قد طلب التحقق يدويًا
                        self.master.after(0, lambda: messagebox.showinfo(self._('no_update_available_title'), self._('no_update_available_message'), parent=self.master))
                elif not on_startup:
                    self.master.after(0, lambda: messagebox.showerror("خطأ", f"فشل التحقق من التحديث. رمز الحالة: {response.status}", parent=self.master))
        except Exception as e:
            print(f"Update check failed: {e}")
            if not on_startup:
                self.master.after(0, lambda: messagebox.showerror("خطأ", f"فشل الاتصال بخادم التحديثات:\n{e}", parent=self.master))
        finally:
            # إعادة نص الحالة إلى الوضع الطبيعي بعد التحقق اليدوي
            if not on_startup:
                self.master.after(1000, lambda: self.status_label.config(text=self._('ready_to_download')))

    def prompt_user_to_update(self, version_info):
        """Shows a dialog asking the user if they want to update."""
        if messagebox.askyesno(
            self._('update_available_title'),
            self._('update_available_message', latest_version=version_info.get('latest_version', 'N/A'), release_notes=version_info.get('release_notes', '')),
            parent=self.master
        ):
            webbrowser.open_new(version_info.get("download_url"))
            messagebox.showinfo("بدء التحديث", "سيتم الآن فتح رابط التحميل في متصفحك. بعد اكتمال التحميل، يرجى تشغيل المثبت الجديد. سيتم إغلاق البرنامج الآن.", parent=self.master)
            self.shutdown_application(force=True) # إغلاق البرنامج للسماح بالتحديث

class BrowserRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests from the browser extension."""
    def __init__(self, app_instance, *args, **kwargs):
        self.app = app_instance
        super().__init__(*args, **kwargs)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = json.loads(post_data)
        self.app.add_download_from_browser(params.get('url'), params.get('cookies'))
        self.send_response(200)
        self.end_headers()

class DetailsWindow(tk.Toplevel):
    """نافذة منبثقة لعرض تفاصيل تقدم أجزاء التحميل."""
    def __init__(self, master, item):
        super().__init__(master)
        self.item = item
        self.app = item.app
        self._offset_x = 0
        self._offset_y = 0

        self.overrideredirect(True)
        self.geometry("550x380")
        self.transient(master)
        self.attributes("-topmost", True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        main_container = ttk.Frame(self, style='Card.TFrame', padding=1)
        main_container.pack(expand=True, fill=tk.BOTH)

        # --- Custom Title Bar ---
        title_bar = ttk.Frame(main_container) # No style, will be configured manually
        title_bar.pack(fill=tk.X)
        title_label = ttk.Label(title_bar, text=f"{self.app._('show_part_details')} - {os.path.basename(item.save_location)}", anchor=tk.W)
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        close_button = ttk.Button(title_bar, text='X', style='Close.TButton', command=self.on_close)
        close_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # --- تطبيق لون الإطار المميز على شريط العنوان ---
        accent_color = self.app.settings.get('title_bar_bg_color', '#4a4a4a')
        try:
            r, g, b = self.winfo_rgb(accent_color)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            fg_color = 'white' if brightness < 128000 else 'black'
        except (tk.TclError, ValueError):
            fg_color = 'black'

        # إنشاء نمط فريد لهذه النافذة لتجنب التضارب
        style = ttk.Style()
        style_id = f'AccentTitle.{self.winfo_id()}'
        style.configure(f'{style_id}.TFrame', background=accent_color)
        style.configure(f'{style_id}.TLabel', background=accent_color, foreground=fg_color, font=("Tahoma", 9, "bold"))

        title_bar.configure(style=f'{style_id}.TFrame')
        title_label.configure(style=f'{style_id}.TLabel')

        # إنشاء نمط مخصص لزر الإغلاق ليتناسب مع لون النص
        close_style_id = f'AccentClose.{self.winfo_id()}.TButton'
        # تعديل: فرض اللون الأسود على حرف X لضمان ظهوره
        style.configure(close_style_id, foreground='black', background=accent_color, borderwidth=0, relief='flat', font=('Arial', 8, 'bold'), padding=(2, 0))
        style.map(
            close_style_id,
            background=[('active', '#c04040'), ('!active', accent_color)],
            foreground=[('active', 'white'), ('!active', 'black')]
        )
        close_button.configure(style=close_style_id)

        # Bind drag events
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<ButtonRelease-1>", self.stop_move)
        title_bar.bind("<B1-Motion>", self.do_move)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<ButtonRelease-1>", self.stop_move)
        title_label.bind("<B1-Motion>", self.do_move)

        main_frame = ttk.Frame(main_container, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 5))

        # --- Scrollable Canvas for real progress bars ---
        canvas = tk.Canvas(main_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Store widgets for updating ---
        self.progress_bars = []
        self.progress_labels = []

        # --- Create UI elements for each segment ---
        for i in range(item.num_segments):
            row_frame = ttk.Frame(scrollable_frame, padding=(0, 5))
            row_frame.pack(fill=tk.X, expand=True)

            part_label = ttk.Label(row_frame, text=f"الجزء {i+1}:", width=10)
            part_label.pack(side=tk.LEFT)

            pb = ttk.Progressbar(row_frame, orient="horizontal", length=100, mode="determinate")
            pb.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.progress_bars.append(pb)

            pl = ttk.Label(row_frame, text="0%", width=25, anchor=tk.W)
            pl.pack(side=tk.LEFT)
            self.progress_labels.append(pl)

        # --- Start the update loop ---
        self.update_loop()

    def start_move(self, event): self._offset_x = event.x; self._offset_y = event.y
    def stop_move(self, event): self._offset_x = None; self._offset_y = None
    def do_move(self, event):
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def on_close(self):
        """يتم استدعاؤها عند إغلاق نافذة التفاصيل."""
        self.item.details_window = None
        self.destroy()

    def update_loop(self):
        """Updates the progress bars and labels periodically."""
        if not self.winfo_exists():
            return

        for i in range(self.item.num_segments):
            if i < len(self.item.segments):
                segment = self.item.segments[i]
                downloaded = segment.downloaded_size
                total = segment.total_size
                
                if total > 0:
                    percentage = (downloaded / total) * 100
                    self.progress_bars[i]['value'] = percentage
                    self.progress_labels[i].config(text=f"{self.app.format_size(downloaded)} / {self.app.format_size(total)} ({percentage:.1f}%)")
                else:
                    self.progress_bars[i]['value'] = 0
                    self.progress_labels[i].config(text=f"{self.app.format_size(downloaded)} / N/A")

        self.after(500, self.update_loop)

class SettingsWindow(tk.Toplevel):
    """نافذة منبثقة لتغيير إعدادات التطبيق."""
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self._ = app._
        self.title(self._('settings'))
        self.geometry("450x540") # زيادة ارتفاع النافذة لضمان ظهور الأزرار
        self.transient(master)
        self.grab_set()

        # نسخة مؤقتة من الإعدادات للتعديل عليها
        self.temp_colors = self.app.color_settings.copy()
        self.temp_language = tk.StringVar(value=self.app.lang_manager.language)
        self.temp_auto_resume = tk.BooleanVar(value=self.app.settings.get('auto_resume_on_startup', True))
        self.temp_default_unknown_category = tk.StringVar(value=self.app.settings.get('default_unknown_category', 'uncategorized'))
        self.temp_default_download_folder = tk.StringVar(value=self.app.get_default_download_folder())
        self.temp_port = tk.IntVar(value=self.app.server_port)
        self.temp_limit_enabled = tk.BooleanVar(value=self.app.settings.get('speed_limit_enabled', False))
        self.temp_limit_value = tk.IntVar(value=self.app.settings.get('speed_limit_value', 1024))
        self.temp_limit_unit = tk.StringVar(value=self.app.settings.get('speed_limit_unit', 'kb_s'))
        self.temp_instant_search = tk.BooleanVar(value=self.app.settings.get('instant_search_enabled', True))
        self.temp_max_concurrent_downloads = tk.IntVar(value=self.app.max_concurrent_downloads)
        self.temp_title_bar_bg = tk.StringVar(value=self.app.settings.get('title_bar_bg_color', '#4a4a4a'))
        self.color_previews = {}

        # --- الإطار الرئيسي وأزرار التحكم السفلية ---
        main_frame = ttk.Frame(self, padding=(10, 10, 10, 0))
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        buttons_frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # --- إنشاء واجهة التبويبات ---
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill=tk.BOTH)

        # --- التبويب الأول: عام ---
        general_tab = ttk.Frame(notebook, padding="10")
        notebook.add(general_tab, text=self._('general_tab'))

        lang_frame = ttk.LabelFrame(general_tab, text=self._('language'), padding="10")
        lang_frame.pack(fill=tk.X, pady=(0, 10), expand=True)
        
        self.lang_map = {'ar': self._('arabic'), 'en': self._('english'), 'fr': self._('french'), 'es': self._('spanish')}
        self.temp_lang_display = tk.StringVar(value=self.lang_map.get(self.temp_language.get()))
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.temp_lang_display, state="readonly", values=list(self.lang_map.values()))
        lang_combo.pack(fill=tk.X)
        lang_combo.bind('<<ComboboxSelected>>', self.on_lang_select)

        startup_frame = ttk.LabelFrame(general_tab, text=self._('startup_options'), padding="10")
        startup_frame.pack(fill=tk.X, pady=(0, 10), expand=True)

        # --- قسم مجلد الحفظ الافتراضي ---
        save_folder_frame = ttk.LabelFrame(general_tab, text=self._('default_save_folder'), padding="10")
        save_folder_frame.pack(fill=tk.X, pady=(0, 10), expand=True)

        path_label = ttk.Label(save_folder_frame, textvariable=self.temp_default_download_folder, wraplength=300, anchor=tk.W)
        path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = ttk.Button(save_folder_frame, text=self._('change_folder'), command=self.browse_default_folder)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        # --- قسم تكامل المتصفح ---
        browser_frame = ttk.LabelFrame(general_tab, text=self._('browser_integration_settings'), padding="10")
        browser_frame.pack(fill=tk.X, pady=(0, 10), expand=True)
        ttk.Label(browser_frame, text=self._('browser_integration_desc'), wraplength=350).pack(anchor=tk.W, pady=(0, 5))
        open_ext_settings_button = ttk.Button(browser_frame, text=self._('open_browser_settings_btn'), command=self.open_extension_settings)
        open_ext_settings_button.pack(anchor=tk.W)

        # --- التبويب الثاني: التحميلات ---
        downloads_tab = ttk.Frame(notebook, padding="10")
        notebook.add(downloads_tab, text=self._('downloads_tab'))

        # --- قسم الفئة الافتراضية (منقول) ---
        default_cat_frame = ttk.LabelFrame(downloads_tab, text=self._('default_category_for_unknown'), padding="10")
        default_cat_frame.pack(fill=tk.X, pady=(0, 10), expand=True)
        ttk.Label(default_cat_frame, text=self._('default_category_desc'), wraplength=350).pack(anchor=tk.W, pady=(0, 5))
        category_keys = [key for key in self.app.categories.keys() if key != 'all']
        self.key_to_display_map = {key: self.app.categories[key] for key in category_keys}
        default_cat_combo = ttk.Combobox(default_cat_frame, textvariable=self.temp_default_unknown_category, state="readonly", values=category_keys)
        default_cat_combo.pack(fill=tk.X)

        # --- قسم التحميلات المتزامنة ---
        concurrent_frame = ttk.LabelFrame(downloads_tab, text=self._('max_concurrent_downloads'), padding="10")
        concurrent_frame.pack(fill=tk.X, expand=True, pady=(0, 10))
        concurrent_spinbox = ttk.Spinbox(
            concurrent_frame, from_=1, to=16, 
            textvariable=self.temp_max_concurrent_downloads, width=5
        )
        concurrent_spinbox.pack(anchor=tk.W)

        # --- قسم تحديد السرعة (منقول) ---
        limit_frame = ttk.LabelFrame(downloads_tab, text=self._('speed_limit_tab'), padding="10")
        limit_frame.pack(fill=tk.X, expand=True, pady=(0, 10))

        def toggle_limit_controls():
            state = tk.NORMAL if self.temp_limit_enabled.get() else tk.DISABLED
            limit_value_spinbox.config(state=state)
            limit_unit_combo.config(state=state)

        limit_check = ttk.Checkbutton(limit_frame, text=self._('enable_speed_limit'), variable=self.temp_limit_enabled, command=toggle_limit_controls)
        limit_check.pack(anchor=tk.W, pady=(0, 10))

        controls_frame = ttk.Frame(limit_frame)
        controls_frame.pack(fill=tk.X)

        ttk.Label(controls_frame, text=self._('max_speed')).pack(side=tk.LEFT)
        limit_value_spinbox = ttk.Spinbox(controls_frame, from_=1, to=100000, textvariable=self.temp_limit_value, width=8)
        limit_value_spinbox.pack(side=tk.LEFT, padx=5)

        unit_map = {'kb_s': self._('kb_s'), 'mb_s': self._('mb_s')}
        limit_unit_combo = ttk.Combobox(controls_frame, textvariable=self.temp_limit_unit, state="readonly", values=list(unit_map.keys()), width=8)
        limit_unit_combo.pack(side=tk.LEFT)
        toggle_limit_controls() # Set initial state

        # --- قسم البحث الفوري ---
        search_options_frame = ttk.LabelFrame(downloads_tab, text=self._('search'), padding="10")
        search_options_frame.pack(fill=tk.X, expand=True, pady=(0, 10))
        ttk.Checkbutton(search_options_frame, text=self._('enable_instant_search'), variable=self.temp_instant_search).pack(anchor=tk.W)

        # --- التبويب الثاني: الاتصال ---
        connection_tab = ttk.Frame(notebook, padding="10")
        notebook.add(connection_tab, text=self._('connection_tab'))

        server_frame = ttk.LabelFrame(connection_tab, text=self._('server_settings'), padding="10")
        server_frame.pack(fill=tk.X, pady=(0, 10), expand=True)
        port_row = ttk.Frame(server_frame)
        port_row.pack(fill=tk.X)
        ttk.Label(port_row, text=self._('server_port')).pack(side=tk.LEFT, padx=(0, 10)) # Corrected line
        port_spinbox = ttk.Spinbox(port_row, from_=1024, to=65535, textvariable=self.temp_port, width=8) # Corrected line
        port_spinbox.pack(in_=port_row, side=tk.LEFT) # Corrected line

        # --- التبويب الثالث: المظهر ---
        appearance_tab = ttk.Frame(notebook, padding="10")
        notebook.add(appearance_tab, text=self._('appearance_tab'))

        colors_frame = ttk.LabelFrame(appearance_tab, text=self._('status_colors'), padding="10")
        colors_frame.pack(fill=tk.X, expand=True)

        status_map = {
            'downloading': self._('downloading'),
            'complete': self._('complete'),
            'paused': self._('paused_status'),
            'error': self._('error_title')
        }
        
        # --- إعداد Grid وتتبع الصفوف ---
        self.color_row_index = 0
        colors_frame.columnconfigure(0, weight=1) # السماح للعمود الأول بالتمدد
        colors_frame.columnconfigure(1, minsize=40) # تحديد عرض أدنى لمربع اللون
        colors_frame.columnconfigure(1, minsize=80) # تحديد عرض أدنى لمربع اللون

        for tag, name in status_map.items():
            self.create_color_picker_row(colors_frame, tag, name)

        # --- قسم ألوان الواجهة العامة ---
        general_colors_frame = ttk.LabelFrame(appearance_tab, text=self._('general_ui_colors'), padding="10")
        general_colors_frame.pack(fill=tk.X, expand=True, pady=(10, 0))
        # --- إعادة تعيين عداد الصفوف للإطار الجديد ---
        self.color_row_index = 0
        general_colors_frame.columnconfigure(0, weight=1)
        general_colors_frame.columnconfigure(1, minsize=40) # تحديد عرض أدنى لمربع اللون
        general_colors_frame.columnconfigure(1, minsize=80)
        general_colors_frame.columnconfigure(2, weight=0) # Button column

        # Add color pickers for general UI elements
        self.create_color_picker_row(general_colors_frame, 'title_bar_bg', self._('title_bar_bg'))

        # Add a reset button
        reset_button = ttk.Button(general_colors_frame, text=self._('reset_colors_to_default'), command=self.reset_colors_to_default)
        reset_button.grid(row=self.color_row_index, column=0, columnspan=3, pady=(10, 0), sticky=tk.W)

        # --- أزرار التحكم ---

        cancel_button = ttk.Button(buttons_frame, text=self._('cancel'), command=self.destroy)
        cancel_button.pack(side=tk.RIGHT)

        apply_button = ttk.Button(buttons_frame, text=self._('apply'), command=self.apply_changes)
        apply_button.pack(side=tk.RIGHT, padx=5)

        ok_button = ttk.Button(buttons_frame, text=self._('ok'), command=self.on_ok)
        ok_button.pack(side=tk.RIGHT, padx=5)

        # --- تطبيق لون شريط العنوان المخصص (مثل النافذة الرئيسية) ---
        try:
            if sys.platform == "win32" and sys.getwindowsversion().major >= 10:
                self.update_idletasks()
                HWND = windll.user32.GetParent(self.winfo_id())
                if HWND:
                    def hex_to_bgr(hex_color):
                        hex_color = hex_color.lstrip('#')
                        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                        return (b << 16) | (g << 8) | r
                    
                    bg_color_hex = self.app.settings.get('title_bar_bg_color', '#4a4a4a')
                    bg_color_bgr = hex_to_bgr(bg_color_hex)
                    windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(bg_color_bgr)), sizeof(c_int))
                    # تعديل: حساب لون نص متباين (أسود أو أبيض) لضمان ظهوره
                    try:
                        bg_hex = bg_color_hex.lstrip('#')
                        r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
                        brightness = (r * 299 + g * 587 + b * 114) / 1000
                        fg_hex = '#000000' if brightness > 128 else '#FFFFFF'
                    except Exception:
                        fg_hex = '#000000' # الافتراضي هو الأسود

                    text_color_bgr = hex_to_bgr(fg_hex)
                    windll.dwmapi.DwmSetWindowAttribute(HWND, 36, byref(c_int(text_color_bgr)), sizeof(c_int))
        except Exception:
            pass # تجاهل الخطأ بصمت إذا فشل التخصيص

    def on_lang_select(self, event):
        """Updates the language code when a display name is selected."""
        selected_display_name = self.temp_lang_display.get()
        for code, display in self.lang_map.items():
            if display == selected_display_name:
                self.temp_language.set(code)
                break

    def browse_default_folder(self):
        """Opens a dialog to choose a new default download folder."""
        new_folder = filedialog.askdirectory(
            initialdir=self.temp_default_download_folder.get(),
            title=self._('default_save_folder'),
            parent=self
        )
        if new_folder:
            self.temp_default_download_folder.set(new_folder)

    def open_extension_settings(self):
        """يفتح صفحة إعدادات إضافة المتصفح."""
        # هذا المعرف ثابت ويتم الحصول عليه من ملف manifest.json بعد أول تحميل للإضافة
        extension_id = "ejdidpckilmpbjigoejiplkddddnmklp"
        url = f"chrome-extension://{extension_id}/options.html"
        try:
            webbrowser.open_new(url)
        except Exception as e:
            messagebox.showerror("خطأ", f"لم يتمكن من فتح صفحة الإعدادات:\n{url}\n\n{e}", parent=self)


    def create_color_picker_row(self, parent, tag, name):
        """ينشئ صفًا لاختيار لون لحالة معينة باستخدام grid لمحاذاة أفضل."""
        label = ttk.Label(parent, text=f"{name}:")
        label.grid(row=self.color_row_index, column=0, sticky=tk.W, pady=4)

        # Get the correct initial color
        if tag in self.temp_colors:
            initial_bg = self.temp_colors.get(tag, 'white')
        else: # Assumes it's a general UI color like title_bar_bg
            initial_bg = self.temp_title_bar_bg.get()

        color_preview = tk.Label(parent, text="", background=initial_bg, relief="sunken", borderwidth=1)
        color_preview.grid(row=self.color_row_index, column=1, padx=10, pady=4, sticky="ew")
        self.color_previews[tag] = color_preview

        button = ttk.Button(parent, text=self._('browse'), command=lambda t=tag: self.choose_color(t))
        button.grid(row=self.color_row_index, column=2, pady=4)

        self.color_row_index += 1

    def choose_color(self, tag):
        """يفتح مربع حوار اختيار اللون ويحدث اللون المؤقت."""
        # Determine which dictionary to get the initial color from
        if tag in self.temp_colors:
            initial_color = self.temp_colors.get(tag)
        else:
            initial_color = self.temp_title_bar_bg.get()

        color_code = colorchooser.askcolor(initialcolor=initial_color, title=f"اختر لونًا لـ {tag}")
        if color_code and color_code[1]:
            new_color = color_code[1]
            self.update_temp_color(tag, new_color)

    def apply_changes(self):
        """يطبق الإعدادات المؤقتة على التطبيق ويحفظها."""
        self.app.color_settings.update(self.temp_colors)
        self.app.apply_color_settings()

        new_lang = self.temp_language.get()
        self.app.lang_manager.set_language(new_lang)
        self.app.retranslate_ui()

        new_port = self.temp_port.get()
        if new_port != self.app.server_port:
            self.app.server_port = new_port
            messagebox.showinfo("إعادة تشغيل مطلوبة", self._('port_restart_warning'), parent=self)

        self.app.settings['default_unknown_category'] = self.temp_default_unknown_category.get()
        self.app.settings['default_download_folder'] = self.temp_default_download_folder.get()

        # Save speed limit settings
        self.app.settings['speed_limit_enabled'] = self.temp_limit_enabled.get()
        self.app.settings['speed_limit_value'] = self.temp_limit_value.get()
        self.app.settings['speed_limit_unit'] = self.temp_limit_unit.get()
        self.app.settings['instant_search_enabled'] = self.temp_instant_search.get()
        new_max_downloads = self.temp_max_concurrent_downloads.get()
        if self.app.max_concurrent_downloads != new_max_downloads:
            self.app.max_concurrent_downloads = new_max_downloads
            self.app.process_download_queue() # Process queue in case limit was increased
        self.app.update_speed_limit_from_settings() # Apply immediately
        
        # Save new appearance settings
        appearance_changed = (self.app.settings.get('title_bar_bg_color') != self.temp_title_bar_bg.get())
        self.app.settings['title_bar_bg_color'] = self.temp_title_bar_bg.get()

        # --- تطبيق لون الإطارات فورًا ---
        theme_bg_color = ttk.Style().lookup('TFrame', 'background')
        self.app.apply_frame_color(self.temp_title_bar_bg.get(), theme_bg_color)

        self.app.save_settings()
        
        if appearance_changed:
            messagebox.showinfo("إعادة تشغيل مطلوبة", "بعض تغييرات المظهر تتطلب إعادة تشغيل البرنامج لتظهر بشكل كامل.", parent=self)

    def reset_colors_to_default(self):
        """Resets color settings to their default values in the UI."""
        default_status_colors = {
            'downloading': '#d9edf7',
            'complete': '#dff0d8',
            'paused': '#fcf8e3',
            'error': '#f2dede'
        }
        default_frame_color = '#4a4a4a'

        # Reset the temporary variables
        self.temp_colors = default_status_colors.copy()
        self.temp_title_bar_bg.set(default_frame_color)

        # Update the UI preview widgets
        for tag, color in self.temp_colors.items():
            if tag in self.color_previews:
                self.color_previews[tag].config(background=color)
        
        if 'title_bar_bg' in self.color_previews:
            self.color_previews['title_bar_bg'].config(background=default_frame_color)

    def on_ok(self):
        self.apply_changes()
        self.destroy()

    def update_temp_color(self, tag, color):
        """Updates the correct temporary variable and the color preview."""
        if tag in self.temp_colors:
            self.temp_colors[tag] = color
        else: # This will now handle 'title_bar_bg'
            self.temp_title_bar_bg.set(color)
        
        if tag in self.color_previews:
            self.color_previews[tag].config(background=color)

class MiniProgressWindow(tk.Toplevel):
    """نافذة منبثقة صغيرة لعرض تقدم التحميل والتحكم فيه."""
    def __init__(self, master, item):
        super().__init__(master)
        self.item = item
        self.app = item.app
        self._offset_x = 0
        self._offset_y = 0

        self.overrideredirect(True)
        self.geometry("380x220")
        self.transient(master)
        self.attributes("-topmost", True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Main container with a border ---
        main_container = ttk.Frame(self, style='Card.TFrame', padding=1)
        main_container.pack(expand=True, fill=tk.BOTH)

        # --- Custom Title Bar ---
        title_bar = ttk.Frame(main_container) # No style, will be configured manually
        title_bar.pack(fill=tk.X)
        title_label = ttk.Label(title_bar, text=self.app._('window_title'), anchor=tk.W)
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        close_button = ttk.Button(title_bar, text='X', style='Close.TButton', command=self.on_close)
        close_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # --- تطبيق لون الإطار المميز على شريط العنوان ---
        accent_color = self.app.settings.get('title_bar_bg_color', '#4a4a4a')
        try:
            r, g, b = self.winfo_rgb(accent_color)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            fg_color = 'white' if brightness < 128000 else 'black'
        except (tk.TclError, ValueError):
            fg_color = 'black'

        # إنشاء نمط فريد لهذه النافذة
        style = ttk.Style()
        style_id = f'AccentTitle.{self.winfo_id()}'
        style.configure(f'{style_id}.TFrame', background=accent_color)
        style.configure(f'{style_id}.TLabel', background=accent_color, foreground=fg_color, font=("Tahoma", 9, "bold"))

        title_bar.configure(style=f'{style_id}.TFrame')
        title_label.configure(style=f'{style_id}.TLabel')

        # إنشاء نمط مخصص لزر الإغلاق لهذه النافذة
        close_style_id = f'AccentClose.{self.winfo_id()}.TButton'
        # تعديل: فرض اللون الأسود على حرف X لضمان ظهوره
        style.configure(close_style_id, foreground='black', background=accent_color, borderwidth=0, relief='flat', font=('Arial', 8, 'bold'), padding=(2, 0))
        style.map(
            close_style_id,
            background=[('active', '#c04040'), ('!active', accent_color)],
            foreground=[('active', 'white'), ('!active', 'black')]
        )
        close_button.configure(style=close_style_id)

        # Bind drag events to the title bar and its label
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<ButtonRelease-1>", self.stop_move)
        title_bar.bind("<B1-Motion>", self.do_move)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<ButtonRelease-1>", self.stop_move)
        title_label.bind("<B1-Motion>", self.do_move)

        # --- Content Frame ---
        main_frame = ttk.Frame(main_container, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

        self.filename_label = ttk.Label(main_frame, text=os.path.basename(item.save_location), anchor=tk.W, font=("Tahoma", 9, "bold"))
        self.filename_label.pack(fill=tk.X, pady=(0, 5))
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=2)
        self.progress_label = ttk.Label(main_frame, text="...", anchor=tk.W)
        self.progress_label.pack(fill=tk.X, pady=2)
        self.speed_label = ttk.Label(main_frame, text="...", anchor=tk.W)
        self.speed_label.pack(fill=tk.X, pady=2)
        self.status_label = ttk.Label(main_frame, text="...", anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(2, 8))

        # --- تخزين مراجع الأيقونات بشكل دائم داخل النافذة لمنع اختفائها ---
        self.icon_pause_color = self.app.icons.get('pause', {}).get('color')
        self.icon_pause_disabled = self.app.icons.get('pause', {}).get('disabled')
        self.icon_start_color = self.app.icons.get('start', {}).get('color')
        self.icon_start_disabled = self.app.icons.get('start', {}).get('disabled')
        self.icon_resume_color = self.app.icons.get('resume_file', {}).get('color')
        self.icon_cancel_color = self.app.icons.get('cancel', {}).get('color')
        self.icon_cancel_disabled = self.app.icons.get('cancel', {}).get('disabled')


        # --- Buttons are now part of the content frame ---
        self.action_button = ttk.Button(main_frame, text="إيقاف مؤقت", compound=tk.LEFT, command=self.toggle_download)
        self.action_button.pack(side=tk.LEFT)
        self.cancel_button = ttk.Button(main_frame, text="إلغاء", compound=tk.LEFT, command=self.cancel_download)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        self.update_loop()

    def start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def stop_move(self, event):
        self._offset_x = None
        self._offset_y = None

    def do_move(self, event):
        x = self.winfo_pointerx() - self._offset_x
        y = self.winfo_pointery() - self._offset_y
        self.geometry(f"+{x}+{y}")

    def toggle_download(self):
        if self.item.state in [DownloadState.IDLE, DownloadState.PAUSED, DownloadState.SCHEDULED, DownloadState.ERROR_RETRYING, DownloadState.CANCELLED, DownloadState.PERMANENT_ERROR]:
            self.app.start_download(self.item)
        elif self.item.state == DownloadState.DOWNLOADING:
            self.app.pause_download(self.item)

    def cancel_download(self):
        self.app.cancel_download(self.item)

    def on_close(self):
        self.item.mini_progress_window = None
        self.destroy()

    def update_loop(self):
        if not self.winfo_exists(): return

        item = self.item
        progress_str = f"{(item.downloaded_size / item.total_size * 100):.1f}%" if item.total_size > 0 else "0.0%"
        self.progress_bar['value'] = (item.downloaded_size / item.total_size * 100) if item.total_size > 0 else 0
        self.progress_label.config(text=f"{self.app.format_size(item.downloaded_size)} / {self.app.format_size(item.total_size)} ({progress_str})")
        self.speed_label.config(text=f"{self.app._('speed')}: {self.app.format_size(item.speed)}/s | {self.app._('time_left')}: {self.app.format_time(item.time_left)}")
        self.status_label.config(text=f"{self.app._('status')}: {self.app._(item.status_text)}")

        # --- منطق تحديث الأزرار المحسن ---
        action_text, action_icon_key, action_cmd, action_state, cancel_state = self.app.get_button_states(item)

        # تحديد الأيقونة الصحيحة لزر الإجراء بناءً على المراجع المحفوظة
        if action_icon_key == 'pause':
            action_icon = self.icon_pause_color if action_state == tk.NORMAL else self.icon_pause_disabled
        elif action_icon_key == 'resume_file':
            action_icon = self.icon_resume_color
        else: # 'start'
            action_icon = self.icon_start_color if action_state == tk.NORMAL else self.icon_start_disabled

        # تطبيق الحالة المحسوبة على الأزرار
        self.action_button.config(
            text=action_text,
            command=action_cmd,
            state=action_state,
            image=action_icon
        )
        self.cancel_button.config(
            state=cancel_state,
            image=self.icon_cancel_color if cancel_state == tk.NORMAL else self.icon_cancel_disabled
        )

        self.after(500, self.update_loop)

    def refresh_link(self):
        """A wrapper to call the app's refresh link logic for this specific item."""
        self.app.refresh_download_link(self.item)
        self.on_close() # Close the mini window as the main dialog will appear

def register_native_host():
    """
    Registers the native messaging host by creating a manifest and
    adding keys to the Windows Registry.
    """
    if sys.platform != "win32":
        return False
    
    try:
        HOST_NAME = "com.engmohamed.advanced_downloader"
        
        # The executable path is the most reliable way to launch the app
        if getattr(sys, 'frozen', False):
            # When running as a packaged app (PyInstaller)
            base_dir = os.path.dirname(sys.executable)
            executable_path = sys.executable
        else:
            # When running as a script for development
            base_dir = os.path.abspath(".")
            # For dev, we point to the run.bat which sets up the python env
            executable_path = os.path.join(base_dir, "run.bat")

        manifest_path = os.path.join(base_dir, "native-host-manifest.json")

        # Update the manifest to point to the correct executable path
        with open(manifest_path, 'r+', encoding='utf-8') as f:
            manifest = json.load(f)
            manifest['path'] = executable_path
            f.seek(0)
            json.dump(manifest, f, indent=4)
            f.truncate()

        for reg_path in [r"Software\Google\Chrome\NativeMessagingHosts", r"Software\Microsoft\Edge\NativeMessagingHosts"]:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, os.path.join(reg_path, HOST_NAME))
            winreg.SetValue(key, None, winreg.REG_SZ, manifest_path)
            winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Failed to register native host: {e}")
        return False

def unregister_native_host():
    """Removes the native messaging host keys from the Windows Registry."""
    if sys.platform != "win32":
        return
    
    HOST_NAME = "com.engmohamed.advanced_downloader"
    for reg_path in [r"Software\Google\Chrome\NativeMessagingHosts", r"Software\Microsoft\Edge\NativeMessagingHosts"]:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
            winreg.DeleteKey(key, HOST_NAME)
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass # Key or subkey doesn't exist, which is fine.
        except Exception:
            pass # Ignore other errors during uninstallation.

def check_dependencies():
    """
    Checks for required packages. If any are missing, it shows a clear,
    blocking error message and instructs the user on how to fix it.
    Returns False if dependencies are missing, True otherwise.
    """
    required_packages = [
        ("cloudscraper", "cloudscraper"),
        ("PIL", "Pillow"),
        ("win10toast_persist", "win10toast-persist"),
        ("pystray", "pystray"),
        ("tkinterdnd2", "tkinterdnd2"),
        ("ttkthemes", "ttkthemes"),
    ]

    missing_modules = []
    for module_name, install_name in required_packages:
        if importlib.util.find_spec(module_name) is None:
            missing_modules.append(install_name)

    if not missing_modules:
        return True # All good

    # If we are here, modules are missing. Show a robust error message.
    error_message = (
        "البرنامج لا يمكنه العمل بسبب عدم وجود المكتبات التالية:\n"
        f"• {', '.join(missing_modules)}\n\n"
        "الحل:\n"
        "1. أغلق هذه الرسالة.\n"
        "2. اذهب إلى مجلد البرنامج.\n"
        "3. انقر نقرًا مزدوجًا على ملف `install_requirements.py` لتثبيت كل ما هو مطلوب.\n"
        "4. حاول تشغيل البرنامج مرة أخرى."
    )
    # Use a dedicated Tk instance to show the error, ensuring it's visible.
    root_err = tk.Tk()
    root_err.withdraw()
    messagebox.showerror("مكتبات أساسية ناقصة", error_message, parent=root_err)
    return False
def install_browser_extension_registry():
    """
    Attempts to register the browser extension for Chrome-based browsers
    by adding keys to the Windows Registry. This is a Windows-specific feature.
    """
    if sys.platform != "win32":
        return False

    # This ID is derived from the public key in manifest.json
    EXTENSION_ID = "ejdidpckilmpbjigoejiplkddddnmklp" 
    EXTENSION_VERSION = "1.2" # Must match manifest.json

    try:
        # Use resource_path to find the folder correctly in both dev and packaged app
        # When running as a script, it's in the current dir.
        # When packaged, PyInstaller extracts it to a temp dir.
        # The registry needs an absolute path to where the extension files will be
        # *after installation*. We assume they are in a 'browser-extension' subfolder.
        if getattr(sys, 'frozen', False):
            extension_path = os.path.join(os.path.dirname(sys.executable), "browser-extension")
        else:
            extension_path = os.path.abspath("browser-extension")

        if not os.path.isdir(extension_path):
            print(f"Browser extension path not found at: {extension_path}")
            return False

        # Registry paths for different browsers (user-level installation)
        registry_paths = [
            r"Software\Google\Chrome\Extensions",
            r"Software\Microsoft\Edge\Extensions",
            # You can add other Chromium browsers here, e.g., Brave
            # r"Software\BraveSoftware\Brave-Browser\Extensions",
        ]

        for reg_path in registry_paths:
            try:
                # Create the main extension key for the browser
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                
                # Create a subkey with our extension's ID
                extension_key = winreg.CreateKey(key, EXTENSION_ID)
                
                # Set the path and version values
                winreg.SetValueEx(extension_key, "path", 0, winreg.REG_SZ, extension_path)
                winreg.SetValueEx(extension_key, "version", 0, winreg.REG_SZ, EXTENSION_VERSION)
                winreg.CloseKey(extension_key)
                winreg.CloseKey(key)
            except Exception:
                continue # Ignore errors for browsers that are not installed
        return True
    except Exception as e:
        print(f"Failed to write to registry: {e}")
        return False

def main():
    # --- التعامل مع أوامر التثبيت والإزالة ---
    if len(sys.argv) > 1:
        if sys.argv[1] == '--register':
            register_native_host()
            install_browser_extension_registry()
            sys.exit(0)
        elif sys.argv[1] == '--unregister':
            unregister_native_host()
            # Note: We don't uninstall the browser extension registry keys
            # as they don't harm anything if left behind.
            sys.exit(0)

    # --- التحقق من المكتبات (مهم لمرحلة التطوير) ---
    # عند تحويله لـ exe، سيتم تضمين المكتبات ولن يفشل هذا التحقق
    if not getattr(sys, 'frozen', False):
        if not check_dependencies():
            sys.exit(1)

    settings = {}
    if os.path.exists(SETTINGS_FILE):
        try: # Try to load settings, but don't crash if the file is corrupt
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            pass # Ignore corrupt settings file, use defaults

    first_run = not os.path.exists(SETTINGS_FILE)

    saved_theme = settings.get('theme', 'arc')

    # --- الحل النهائي لمشكلة الأيقونات: إنشاء النافذة بالترتيب الصحيح ---
    # 1. أنشئ النافذة باستخدام ThemedTk أولاً لتطبيق السمة بشكل صحيح.
    try:
        root = ThemedTk(theme=saved_theme)
    except Exception:
        root = tk.Tk()

    # 2. إذا كانت tkinterdnd2 متاحة، قم بتغليف النافذة الموجودة لإضافة وظيفة السحب والإفلات.
    #    هذا هو الأسلوب الصحيح للجمع بين ttkthemes و tkinterdnd2.
    if TkinterDnD:
        root = TkinterDnDWrapper(root)

    # --- START: Splash Screen Logic ---
    root.withdraw() # إخفاء النافذة الرئيسية مؤقتًا
    splash = SplashScreen(root)
    # --- END: Splash Screen Logic ---

    # Pass loaded settings to the app
    app = FileDownloaderApp(root, initial_settings=settings.copy())

    # --- Logic to handle being launched by the browser ---
    # The browser passes two arguments: the origin and the native host ID. We don't need them,
    # but their presence tells us we were launched for native messaging.
    # This logic will run while the splash screen is visible.
    if len(sys.argv) > 1:
        try:
            # Read the message from stdin (standard native messaging protocol)
            raw_length = sys.stdin.buffer.read(4)
            if not raw_length:
                sys.exit(0) # Exit if no message
            message_length = struct.unpack('@I', raw_length)[0]
            message = sys.stdin.buffer.read(message_length).decode('utf-8')
            download_data = json.loads(message)

            # Try to send the data to an already running instance of the app
            port = settings.get('server_port', 9614)
            req = request.Request(f"http://127.0.0.1:{port}", data=json.dumps(download_data).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
            
            try:
                request.urlopen(req, timeout=1)
                sys.exit(0) # Success means another instance is running, so this one can exit.
            except (error.URLError, socket.timeout):
                # Failure means this is the first instance. Continue running and add the download.
                app.add_download_from_browser(download_data.get('url'), download_data.get('cookies'))
        except Exception as e:
            with open("native_host_error.log", "a") as f: f.write(f"{datetime.datetime.now()}: {str(e)}\n")
    
    # --- Attempt to set custom title bar color (Windows specific) ---
    # Note: This uses Windows API and might not work on all Windows versions or configurations.
    # الحصول على لون الخلفية الافتراضي للسمة الحالية
    theme_bg_color = ttk.Style().lookup('TFrame', 'background')
    app.apply_frame_color(settings.get('title_bar_bg_color', '#4a4a4a'), theme_bg_color)

    title_bar_bg_color = settings.get('title_bar_bg_color', '#4a4a4a') # Default dark gray
    try:
        if sys.platform == "win32" and sys.getwindowsversion().major >= 10:
            root.update_idletasks()
            HWND = windll.user32.GetParent(root.winfo_id())

            if HWND:
                # Colors are in BGR format (0x00BBGGRR).
                def hex_to_bgr(hex_color):
                    hex_color = hex_color.lstrip('#')
                    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    return (b << 16) | (g << 8) | r

                # Title bar background from settings
                bg_color_bgr = hex_to_bgr(title_bar_bg_color)
                windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(bg_color_bgr)), sizeof(c_int))

                # Title bar text (less reliable, but we can try)
                # تعديل: حساب لون نص متباين (أسود أو أبيض) لضمان ظهوره
                try:
                    bg_hex = title_bar_bg_color.lstrip('#')
                    r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
                    brightness = (r * 299 + g * 587 + b * 114) / 1000
                    fg_hex = '#000000' if brightness > 128 else '#FFFFFF'
                except Exception:
                    fg_hex = '#000000' # الافتراضي هو الأسود

                text_color_bgr = hex_to_bgr(fg_hex)
                windll.dwmapi.DwmSetWindowAttribute(HWND, 36, byref(c_int(text_color_bgr)), sizeof(c_int))
    except Exception as e:
        # print(f"Debug: Failed to customize title bar: {e}") # Optional debug
        pass # Silently ignore if customization fails

    # --- First Run Setup ---
    if first_run:
        register_native_host() # تسجيل المشغل الأصلي
        if install_browser_extension_registry():
            messagebox.showinfo(
                "تثبيت إضافة المتصفح",
                "تم تسجيل إضافة المتصفح بنجاح.\n\n"
                "الرجاء إعادة تشغيل متصفحك (Chrome/Edge). قد تحتاج إلى تفعيل الإضافة يدويًا من صفحة الإضافات إذا ظهرت رسالة تحذير.",
                parent=root
            )
        app.save_settings() # Save settings to mark that first run is complete

    # --- START: Splash Screen Logic ---
    splash.destroy() # إغلاق شاشة البداية
    root.deiconify() # إظهار النافذة الرئيسية
    # --- END: Splash Screen Logic ---

    root.mainloop()

if __name__ == "__main__":
    # --- تعديل آلية التشغيل ---
    # إذا تم تشغيل البرنامج من المتصفح، فسيتم تمرير وسيط خاص.
    # إذا لم يتم العثور على نسخة أخرى من البرنامج، فستستمر هذه النسخة في العمل.
    # إذا تم تشغيله يدويًا، فإنه يعمل كالمعتاد.
    try:
        main()
    except Exception as e:
        # إنشاء سجل بسيط للأخطاء الفادحة
        with open("fatal_error.log", "a") as f:
            f.write(f"{datetime.datetime.now()}: {str(e)}\n")
