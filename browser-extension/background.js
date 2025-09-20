// Function to create the context menu
function createContextMenu() {
  // Remove any existing menu item to avoid duplicates during development
  chrome.contextMenus.remove("send-to-idm", () => {
    chrome.contextMenus.create({
      id: "send-to-idm",
      title: "تحميل بواسطة مدير التحميل",
      contexts: ["link"] // Show only when right-clicking a link
    });
  });
}

// Create the menu when the extension is installed or the browser starts
chrome.runtime.onInstalled.addListener(createContextMenu);
chrome.runtime.onStartup.addListener(createContextMenu);

// --- Helper Function to send download to Python App ---
async function sendToDownloader(downloadUrl) {
  try {
    // 1. Get cookies for the URL
    const cookies = await chrome.cookies.getAll({ url: downloadUrl });
    const cookieString = cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');

    // 2. Get the port from storage
    const settings = await chrome.storage.sync.get({ port: 9614 });
    const port = settings.port;

    // 3. Send the request
    await fetch(`http://127.0.0.1:${port}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: downloadUrl, cookies: cookieString }),
    });
  } catch (error) {    
    // التحقق من أن الخطأ هو خطأ في الشبكة، مما يعني أن البرنامج غير قيد التشغيل
    if (error instanceof TypeError) {
        console.log("App not running or connection refused. Attempting to launch via native host.");
        chrome.runtime.sendNativeMessage(
          'com.engmohamed.advanced_downloader',
          { url: downloadUrl, cookies: cookieString },
          (response) => { 
            if (chrome.runtime.lastError) {
              console.error(`Native host error: ${chrome.runtime.lastError.message}`);
            }
          } 
        );
    } else {
        console.error("An unexpected error occurred in sendToDownloader:", error);
    }
  }
}

// Handle the context menu click
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "send-to-idm" && info.linkUrl) {
    sendToDownloader(info.linkUrl);
  }
});

// --- Automatic Download Interception ---

// List of file extensions to automatically intercept.
const INTERCEPT_EXTENSIONS = [
    'zip', 'rar', '7z', 'tar', 'gz', 'bz2',
    'exe', 'msi', 'dmg', 'deb', 'rpm',
    'iso', 'img', 'vhd',
    'mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv',
    'mp3', 'flac', 'wav', 'ogg',
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'
];

chrome.downloads.onCreated.addListener(async (downloadItem) => {
  // 1. Check if the feature is enabled in settings
  const settings = await chrome.storage.sync.get({ intercept: true });
  if (!settings.intercept) {
    return; // Do nothing if interception is disabled
  }

  // 1.5. Add an exclusion for GitHub repositories to avoid intercepting code downloads
  if (downloadItem.url.includes("github.com")) {
    console.log(`Ignoring GitHub download: ${downloadItem.url}`);
    return;
  }

  // 2. Extract file extension from the URL
  const url = new URL(downloadItem.url);
  const filename = url.pathname.split('/').pop();
  const extension = filename.split('.').pop().toLowerCase();

  // 3. Check if the extension is in our list
  if (INTERCEPT_EXTENSIONS.includes(extension)) {
    console.log(`Intercepting download for: ${filename}`);

    // 4. Cancel the browser's download and send it to our app
    chrome.downloads.cancel(downloadItem.id);
    sendToDownloader(downloadItem.url);
  }
});