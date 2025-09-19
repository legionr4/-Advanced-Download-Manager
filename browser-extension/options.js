// Saves options to chrome.storage
function save_options() {
    const port = document.getElementById('port').value;
    const intercept = document.getElementById('intercept').checked;
    chrome.storage.sync.set({
        port: port,
        intercept: intercept
    }, function() {
        // Update status to let user know options were saved.
        const status = document.getElementById('status');
        status.textContent = 'تم حفظ الإعدادات.';
        setTimeout(function() {
            status.textContent = '';
        }, 1500);
    });
}

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
function restore_options() {
    chrome.storage.sync.get({
        port: 9614, // Default port
        intercept: true // Default to enabled
    }, function(items) {
        document.getElementById('port').value = items.port;
        document.getElementById('intercept').checked = items.intercept;
    });
}

document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click', save_options);