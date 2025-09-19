﻿using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using System.Reflection;
using Newtonsoft.Json;
using System.Windows.Forms;

namespace Idm
{
    public partial class Form1 : Form
    {
        // استخدام نسخة واحدة من HttpClient لتحسين الأداء
        private static readonly HttpClient httpClient = new HttpClient { Timeout = TimeSpan.FromDays(1) };
        private readonly List<DownloadItem> _downloads = new List<DownloadItem>();
        private const string SessionFile = "downloads.json";
        private int _maxConcurrentDownloads = 3; // القيمة الافتراضية للتحميلات المتزامنة

        public Form1()
        {
            InitializeComponent();
            // إضافة ترويسة User-Agent لتقليد متصفح وتجنب الحظر من الخوادم
            if (httpClient.DefaultRequestHeaders.UserAgent.Count == 0)
            {
                httpClient.DefaultRequestHeaders.UserAgent.ParseAdd("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36");
            }
            LoadSession();
            _maxConcurrentDownloads = (int)concurrentDownloadsNumeric.Value;
            InitializeContextMenu();
            UpdateButtons();

            // تفعيل ميزة السحب والإفلات على قائمة التحميلات
            this.downloadsListView.AllowDrop = true;
            this.downloadsListView.DragEnter += new DragEventHandler(downloadsListView_DragEnter);
            this.downloadsListView.DragDrop += new DragEventHandler(downloadsListView_DragDrop);
        }

        private void addButton_Click(object sender, EventArgs e)
        {
            // استدعاء الدالة المساعدة بدون رابط مبدئي (ستستخدم الحافظة)
            HandleNewDownloadRequest(null);
        }

        private void actionButton_Click(object sender, EventArgs e)
        {
            if (downloadsListView.SelectedItems.Count == 0) return;

            var selectedDownload = (DownloadItem)downloadsListView.SelectedItems[0].Tag;

            if (selectedDownload.Status == DownloadStatus.Downloading) // Pause
            {
                selectedDownload.PauseEvent.Reset();
                selectedDownload.Status = DownloadStatus.Paused;
            }
            else if (selectedDownload.Status == DownloadStatus.Paused || selectedDownload.Status == DownloadStatus.Error || selectedDownload.Status == DownloadStatus.ErrorRetrying || selectedDownload.Status == DownloadStatus.Scheduled) // Resume
            {
                selectedDownload.PauseEvent.Set();
                selectedDownload.Status = DownloadStatus.Queued;
                ProcessQueue();
            }
            else if (selectedDownload.Status == DownloadStatus.Queued) // De-queue (pause)
            {
                selectedDownload.Status = DownloadStatus.Paused;
            }

            UpdateButtons();
        }

        private void removeButton_Click(object sender, EventArgs e)
        {
            if (downloadsListView.SelectedItems.Count == 0) return;

            var selectedDownload = (DownloadItem)downloadsListView.SelectedItems[0].Tag;

            if (MessageBox.Show("هل أنت متأكد من أنك تريد إزالة هذا التحميل؟", "تأكيد الإزالة", MessageBoxButtons.YesNo, MessageBoxIcon.Warning) == DialogResult.Yes)
            {
                selectedDownload.Cts?.Cancel();
                _downloads.Remove(selectedDownload);
                downloadsListView.Items.Remove(selectedDownload.ListViewItem);
                // يمكنك هنا إضافة خيار لحذف الملفات المؤقتة
            }
        }

        private void removeCompletedButton_Click(object sender, EventArgs e)
        {
            var completed = _downloads.Where(d => d.Status == DownloadStatus.Completed).ToList();
            foreach (var item in completed)
            {
                _downloads.Remove(item);
                downloadsListView.Items.Remove(item.ListViewItem);
            }
        }

        private async void ProcessQueue()
        {
            if (this.IsDisposed) return;
            var activeDownloads = _downloads.Count(d => d.Status == DownloadStatus.Downloading);
            if (activeDownloads >= _maxConcurrentDownloads)
            {
                return; // وصلنا للحد الأقصى
            }

            var nextDownload = _downloads.FirstOrDefault(d => d.Status == DownloadStatus.Queued);
            if (nextDownload == null)
            {
                return; // لا يوجد شيء في قائمة الانتظار
            }

            await StartDownload(nextDownload);
        }

        private async Task StartDownload(DownloadItem item)
        {
            item.Cts = new CancellationTokenSource();
            item.PauseEvent.Set();
            item.Status = DownloadStatus.Downloading;

            try
            {
                await DownloadFileAsync(item);
                if (item.Status != DownloadStatus.Cancelled)
                {
                    item.Status = DownloadStatus.Completed;
                }
            }
            catch (OperationCanceledException)
            {
                item.Status = DownloadStatus.Cancelled;
            }
            catch (HttpRequestException httpEx)
            {
                // التمييز بين الأخطاء الدائمة (4xx) والأخطاء المؤقتة (5xx)
                string msg = httpEx.Message.ToLower();
                if (msg.Contains("401") || msg.Contains("403") || msg.Contains("404")) // Unauthorized, Forbidden, Not Found
                {
                    item.Status = DownloadStatus.Error;
                    item.ErrorMessage = $"خطأ دائم ({httpEx.Message}). قد يكون الرابط منتهي الصلاحية أو تم حذفه.";
                }
                else // الأخطاء الأخرى قابلة لإعادة المحاولة
                {
                    await HandleRetryableError(item, httpEx);
                }
            }
            catch (Exception ex)
            {
                await HandleRetryableError(item, ex);
            }
            finally
            {
                item.Cts?.Dispose();
                item.Cts = null;
                item.Speed = 0;
                ProcessQueue(); // محاولة بدء التحميل التالي
            }
        }

        private async Task HandleRetryableError(DownloadItem item, Exception ex)
        {
            item.Status = DownloadStatus.ErrorRetrying;
            item.ErrorMessage = ex.Message;

            // Wait for 30 seconds before requeueing, but allow cancellation or pause
            try
            {
                await Task.Delay(TimeSpan.FromSeconds(30), item.Cts.Token);

                // If status is still ErrorRetrying (user hasn't paused/cancelled), requeue it
                if (item.Status == DownloadStatus.ErrorRetrying)
                {
                    item.Status = DownloadStatus.Queued;
                }
            }
            catch (OperationCanceledException)
            {
                // This is expected if the user cancels the download during the retry wait
                item.Status = DownloadStatus.Cancelled;
            }
        }

        private async Task DownloadFileAsync(DownloadItem item)
        {
            var response = await httpClient.GetAsync(item.Url, HttpCompletionOption.ResponseHeadersRead, item.Cts.Token);
            response.EnsureSuccessStatusCode();

            var totalBytes = response.Content.Headers.ContentLength;
            item.TotalBytes = totalBytes ?? 0;
            var canResume = response.Headers.AcceptRanges.Contains("bytes");

            if (totalBytes.HasValue && canResume && totalBytes > 5 * 1024 * 1024) // تحميل متعدد الأجزاء للملفات الأكبر من 5 ميجا
            {
                await DownloadMultiPartAsync(item);
            }
            else // تحميل عادي
            {
                await DownloadSinglePartAsync(response, item);
            }
        }

        private async Task DownloadSinglePartAsync(HttpResponseMessage response, DownloadItem item)
        {
            long existingBytes = 0;
            if (File.Exists(item.FilePath))
            {
                existingBytes = new FileInfo(item.FilePath).Length;
            }

            // If the server didn't provide total size, we can't reliably resume. Start over.
            if (item.TotalBytes == 0)
            {
                existingBytes = 0;
            }

            if (existingBytes > 0)
            {
                var request = new HttpRequestMessage(HttpMethod.Get, item.Url);
                request.Headers.Range = new System.Net.Http.Headers.RangeHeaderValue(existingBytes, null);
                response = await httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, item.Cts.Token);
            }

            item.PauseEvent.Wait(item.Cts.Token);
            using (var contentStream = await response.Content.ReadAsStreamAsync())
            using (var fileStream = new FileStream(item.FilePath, existingBytes > 0 ? FileMode.Append : FileMode.Create, FileAccess.Write, FileShare.None, 8192, true))
            {
                await CopyStreamWithProgressAsync(contentStream, fileStream, item, item.TotalBytes);
            }
        }

        private async Task DownloadMultiPartAsync(DownloadItem item)
        {
            int parts = item.NumParts;
            long partSize = item.TotalBytes / parts;
            var tempFiles = new List<string>();
            var tasks = new List<Task>();

            for (int i = 0; i < parts; i++)
            {
                long start = i * partSize;
                long end = (i == parts - 1) ? item.TotalBytes - 1 : start + partSize - 1;

                string tempFile = $"{item.FilePath}.part{i}";
                tempFiles.Add(tempFile);

                long existingBytes = 0;
                if (File.Exists(tempFile))
                {
                    existingBytes = new FileInfo(tempFile).Length;
                }

                if (existingBytes >= (end - start + 1))
                {
                    continue;
                }

                tasks.Add(Task.Run(async () =>
                {
                    var request = new HttpRequestMessage(HttpMethod.Get, item.Url);
                    request.Headers.Range = new System.Net.Http.Headers.RangeHeaderValue(start + existingBytes, end);
                    var response = await httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, item.Cts.Token);
                    response.EnsureSuccessStatusCode();

                    using (var contentStream = await response.Content.ReadAsStreamAsync())
                    using (var fileStream = new FileStream(tempFile, FileMode.Append, FileAccess.Write, FileShare.None, 8192, true))
                    {
                        await CopyStreamWithProgressAsync(contentStream, fileStream, item, null);
                    }
                }, item.Cts.Token));
            }

            var progressTask = Task.Run(async () =>
            {
                var stopwatch = Stopwatch.StartNew();
                while (tasks.Any(t => !t.IsCompleted && !t.IsCanceled && !t.IsFaulted))
                {
                    item.Cts.Token.ThrowIfCancellationRequested();
                    item.PauseEvent.Wait(item.Cts.Token);

                    long currentBytes = tempFiles.Sum(f => File.Exists(f) ? new FileInfo(f).Length : 0);
                    UpdateItemProgress(item, currentBytes, stopwatch.Elapsed);
                    await Task.Delay(500, item.Cts.Token);
                }
            }, item.Cts.Token);

            await Task.WhenAll(tasks.Concat(new[] { progressTask }));

            item.Cts.Token.ThrowIfCancellationRequested();

            item.Status = DownloadStatus.Combining;
            using (var finalStream = new FileStream(item.FilePath, FileMode.Create, FileAccess.Write, FileShare.None))
            {
                foreach (var tempFile in tempFiles)
                {
                    using (var tempStream = new FileStream(tempFile, FileMode.Open, FileAccess.Read))
                    {
                        await tempStream.CopyToAsync(finalStream);
                    }
                    File.Delete(tempFile);
                }
            }
        }

        private async Task CopyStreamWithProgressAsync(Stream source, Stream destination, DownloadItem item, long? partTotalBytes)
        {
            var buffer = new byte[8192];
            long totalBytesRead = 0;
            int bytesRead;
            var stopwatch = Stopwatch.StartNew();

            while ((bytesRead = await source.ReadAsync(buffer, 0, buffer.Length, item.Cts.Token)) > 0)
            {
                item.PauseEvent.Wait(item.Cts.Token);

                await destination.WriteAsync(buffer, 0, bytesRead, item.Cts.Token);
                totalBytesRead += bytesRead;
                if (partTotalBytes.HasValue)
                {
                    UpdateItemProgress(item, totalBytesRead, stopwatch.Elapsed);
                }
            }
        }

        private void UpdateItemProgress(DownloadItem item, long currentBytes, TimeSpan timeElapsed)
        {
            double speed = 0;
            if (timeElapsed.TotalSeconds > 0)
            {
                speed = (currentBytes - item.DownloadedBytes) / timeElapsed.TotalSeconds;
            }
            item.DownloadedBytes = currentBytes;
            item.Speed = speed;
        }

        private void uiUpdateTimer_Tick(object sender, EventArgs e)
        {
            foreach (var item in _downloads)
            {
                var lvi = item.ListViewItem;
                if (lvi == null) continue;

                lvi.SubItems[1].Text = $"{FormatBytes(item.DownloadedBytes)} / {FormatBytes(item.TotalBytes)}";
                double percentage = item.TotalBytes > 0 ? (double)item.DownloadedBytes * 100 / item.TotalBytes : 0;
                lvi.SubItems[2].Text = $"{percentage:F1}%";
                lvi.SubItems[3].Text = item.Status == DownloadStatus.Downloading ? $"{FormatBytes(item.Speed)}/s" : "---";

                if (item.Status == DownloadStatus.Scheduled && item.ScheduledTime.HasValue)
                {
                    lvi.SubItems[4].Text = $"مجدول لـ {item.ScheduledTime:g}";
                }
                else
                {
                    lvi.SubItems[4].Text = GetEnumDescription(item.Status);
                }
            }

            CheckScheduledDownloads();
        }

        private void downloadsListView_SelectedIndexChanged(object sender, EventArgs e)
        {
            UpdateButtons();
        }

        private void UpdateButtons()
        {
            if (downloadsListView.SelectedItems.Count > 0)
            {
                var item = (DownloadItem)downloadsListView.SelectedItems[0].Tag;
                actionButton.Enabled = true;
                removeButton.Enabled = true;

                if (item.Status == DownloadStatus.Downloading)
                {
                    actionButton.Text = "إيقاف مؤقت";
                }
                else if (item.Status == DownloadStatus.Paused || item.Status == DownloadStatus.Error || item.Status == DownloadStatus.Queued || item.Status == DownloadStatus.ErrorRetrying || item.Status == DownloadStatus.Scheduled)
                {
                    actionButton.Text = "بدء / استئناف";
                }
                else
                {
                    actionButton.Enabled = false;
                }
            }
            else
            {
                actionButton.Enabled = false;
                removeButton.Enabled = false;
            }
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            SaveSession();
            foreach (var item in _downloads.Where(d => d.Status == DownloadStatus.Downloading))
            {
                item.Cts?.Cancel();
            }
        }

        private void SaveSession()
        {
            // Prepare items for saving
            foreach (var item in _downloads)
            {
                // Mark active downloads as paused so they can be resumed on next launch
                if (item.Status == DownloadStatus.Downloading || item.Status == DownloadStatus.Queued || item.Status == DownloadStatus.Combining || item.Status == DownloadStatus.Scheduled)
                {
                    item.Status = DownloadStatus.Paused;
                }
            }

            // Filter out completed downloads from being saved
            var downloadsToSave = _downloads.Where(d => d.Status != DownloadStatus.Completed && d.Status != DownloadStatus.Cancelled).ToList();

            try
            {
                string json = JsonConvert.SerializeObject(downloadsToSave, Formatting.Indented);
                File.WriteAllText(SessionFile, json);
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error saving session: {ex.Message}");
            }
        }

        private void LoadSession()
        {
            if (!File.Exists(SessionFile)) return;

            try
            {
                string json = File.ReadAllText(SessionFile);
                var loadedDownloads = JsonConvert.DeserializeObject<List<DownloadItem>>(json);

                if (loadedDownloads == null) return;

                foreach (var item in loadedDownloads)
                {
                    // Recalculate downloaded bytes from part files for accuracy
                    long existingBytes = 0;
                    for (int i = 0; i < item.NumParts; i++)
                    {
                        string tempFile = $"{item.FilePath}.part{i}";
                        if (File.Exists(tempFile))
                        {
                            existingBytes += new FileInfo(tempFile).Length;
                        }
                    }
                    item.DownloadedBytes = existingBytes;

                    // Add to UI
                    var listViewItem = new ListViewItem(new[] {
                        Path.GetFileName(item.FilePath),
                        $"{FormatBytes(item.DownloadedBytes)} / {FormatBytes(item.TotalBytes)}",
                        item.TotalBytes > 0 ? $"{(double)item.DownloadedBytes * 100 / item.TotalBytes:F1}%" : "0.0%",
                        "---",
                        GetEnumDescription(item.Status)
                    }) { Tag = item };
                    item.ListViewItem = listViewItem;
                    _downloads.Add(item);
                    downloadsListView.Items.Add(listViewItem);
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Error loading session: {ex.Message}");
            }
        }

        private void concurrentDownloadsNumeric_ValueChanged(object sender, EventArgs e)
        {
            _maxConcurrentDownloads = (int)concurrentDownloadsNumeric.Value;
            ProcessQueue(); // محاولة بدء تحميلات إضافية إذا توفرت أماكن
        }

        private void CheckScheduledDownloads()
        {
            var dueDownloads = _downloads
                .Where(d => d.Status == DownloadStatus.Scheduled && d.ScheduledTime.HasValue && d.ScheduledTime.Value <= DateTime.Now)
                .ToList();

            if (dueDownloads.Any())
            {
                foreach (var item in dueDownloads) { item.Status = DownloadStatus.Queued; }
                ProcessQueue();
            }
        }

        private void setDefaultSaveFolderToolStripMenuItem_Click(object sender, EventArgs e)
        {
            using (var fbd = new FolderBrowserDialog())
            {
                fbd.Description = "اختر مجلد الحفظ الافتراضي";
                string currentPath = GetDefaultSavePath();
                fbd.SelectedPath = currentPath;

                if (fbd.ShowDialog() == DialogResult.OK && !string.IsNullOrWhiteSpace(fbd.SelectedPath))
                {
                    Properties.Settings.Default.DefaultSavePath = fbd.SelectedPath;
                    Properties.Settings.Default.Save();
                    MessageBox.Show($"تم تعيين مجلد الحفظ الافتراضي إلى:\n{fbd.SelectedPath}", "تم الحفظ", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
            }
        }

        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private string GetDefaultSavePath()
        {
            string defaultPath = Properties.Settings.Default.DefaultSavePath;
            if (!string.IsNullOrEmpty(defaultPath) && Directory.Exists(defaultPath))
            {
                return defaultPath;
            }

            // Fallback to user's Downloads folder
            return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Downloads");
        }

        private void aboutToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string aboutText = "برنامج مدير التحميل\n\n" +
                               "الوصف: مدير تحميل متقدم يدعم التحميل متعدد الأجزاء، قائمة الانتظار، وجدولة التحميلات.\n\n" +
                               "المطور: Eng.Mohamed\n" +
                               "الإصدار: 1.5 (تحديثات 2025)\n\n" +
                               "للتواصل أو الإبلاغ عن مشاكل، يرجى زيارة موقعنا.";
            MessageBox.Show(aboutText, "حول البرنامج", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        #region Context Menu

        private ContextMenuStrip _contextMenu;
        private ToolStripMenuItem _startResumeMenuItem;
        private ToolStripMenuItem _pauseMenuItem;
        private ToolStripMenuItem _refreshLinkMenuItem;
        private ToolStripMenuItem _removeMenuItem;

        private void InitializeContextMenu()
        {
            _contextMenu = new ContextMenuStrip();

            _startResumeMenuItem = new ToolStripMenuItem("بدء / استئناف");
            _startResumeMenuItem.Click += (s, e) => actionButton_Click(s, e);

            _pauseMenuItem = new ToolStripMenuItem("إيقاف مؤقت");
            _pauseMenuItem.Click += (s, e) => actionButton_Click(s, e);

            _refreshLinkMenuItem = new ToolStripMenuItem("تحديث رابط التحميل");
            _refreshLinkMenuItem.Click += RefreshLinkMenuItem_Click;

            _removeMenuItem = new ToolStripMenuItem("إزالة");
            _removeMenuItem.Click += (s, e) => removeButton_Click(s, e);

            _contextMenu.Items.Add(_startResumeMenuItem);
            _contextMenu.Items.Add(_pauseMenuItem);
            _contextMenu.Items.Add(new ToolStripSeparator());
            _contextMenu.Items.Add(_refreshLinkMenuItem);
            _contextMenu.Items.Add(new ToolStripSeparator());
            _contextMenu.Items.Add(_removeMenuItem);

            _contextMenu.Opening += ContextMenu_Opening;
            downloadsListView.ContextMenuStrip = _contextMenu;
        }

        private void ContextMenu_Opening(object sender, CancelEventArgs e)
        {
            if (downloadsListView.SelectedItems.Count == 0)
            {
                e.Cancel = true;
                return;
            }

            var item = (DownloadItem)downloadsListView.SelectedItems[0].Tag;

            _startResumeMenuItem.Visible = (item.Status == DownloadStatus.Paused || item.Status == DownloadStatus.ErrorRetrying || item.Status == DownloadStatus.Queued || item.Status == DownloadStatus.Scheduled);
            _pauseMenuItem.Visible = (item.Status == DownloadStatus.Downloading);
            _refreshLinkMenuItem.Visible = (item.Status == DownloadStatus.Error);
        }

        private void RefreshLinkMenuItem_Click(object sender, EventArgs e)
        {
            if (downloadsListView.SelectedItems.Count == 0) return;
            var item = (DownloadItem)downloadsListView.SelectedItems[0].Tag;

            try
            {
                Process.Start(item.Url);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"لم نتمكن من فتح المتصفح: {ex.Message}", "خطأ", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }

            using (var dialog = new AddDownloadDialog(item.Url, isRefreshMode: true))
            {
                if (dialog.ShowDialog(this) == DialogResult.OK)
                {
                    item.Url = dialog.DownloadUrl;
                    item.Status = DownloadStatus.Queued;
                    item.ErrorMessage = null;
                    ProcessQueue();
                }
            }
        }
        #endregion

        #region Drag and Drop

        private void downloadsListView_DragEnter(object sender, DragEventArgs e)
        {
            // التحقق مما إذا كانت البيانات المسحوبة نصية
            if (e.Data.GetDataPresent(DataFormats.Text))
            {
                // إظهار أيقونة النسخ للمستخدم
                e.Effect = DragDropEffects.Copy;
            }
            else
            {
                e.Effect = DragDropEffects.None;
            }
        }

        private void downloadsListView_DragDrop(object sender, DragEventArgs e)
        {
            // الحصول على النص (الرابط) الذي تم إفلاته
            string url = (string)e.Data.GetData(DataFormats.Text);
            if (!string.IsNullOrEmpty(url) && url.StartsWith("http", StringComparison.OrdinalIgnoreCase))
            {
                // استدعاء الدالة المساعدة مع الرابط الذي تم إفلاته
                HandleNewDownloadRequest(url);
            }
        }

        #endregion

        #region Helpers
        /// <summary>
        /// يعالج طلب إضافة تحميل جديد، سواء من زر أو من السحب والإفلات.
        /// </summary>
        /// <param name="initialUrl">الرابط المبدئي لعرضه في مربع الحوار.</param>
        private void HandleNewDownloadRequest(string initialUrl)
        {
            using (var dialog = new AddDownloadDialog(initialUrl))
            {
                if (dialog.ShowDialog(this) == DialogResult.OK)
                {
                    if (_downloads.Any(d => d.FilePath.Equals(dialog.SavePath, StringComparison.OrdinalIgnoreCase)))
                    {
                        MessageBox.Show("هذا الملف موجود بالفعل في القائمة.", "ملف مكرر", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        return;
                    }

                    var newItem = new DownloadItem
                    {
                        Url = dialog.DownloadUrl,
                        FilePath = dialog.SavePath,
                        NumParts = (int)partsPerDownloadNumeric.Value,
                        ScheduledTime = dialog.ScheduledTime,
                        Status = dialog.ScheduledTime.HasValue ? DownloadStatus.Scheduled : DownloadStatus.Queued
                    };

                    var listViewItem = new ListViewItem(new[] { Path.GetFileName(newItem.FilePath), "N/A", "0%", "N/A", newItem.Status == DownloadStatus.Scheduled ? $"مجدول لـ {newItem.ScheduledTime:g}" : GetEnumDescription(newItem.Status) }) { Tag = newItem };
                    newItem.ListViewItem = listViewItem;

                    _downloads.Add(newItem);
                    downloadsListView.Items.Add(listViewItem);

                    ProcessQueue();
                }
            }
        }

        private string FormatBytes(double bytes)
        {
            string[] suffix = { "B", "KB", "MB", "GB", "TB" };
            int i = 0;
            while (bytes >= 1024 && i < suffix.Length - 1)
            {
                bytes /= 1024;
                i++;
            }
            return $"{bytes:F1} {suffix[i]}";
        }

        public static string GetEnumDescription(Enum value)
        {
            FieldInfo fi = value.GetType().GetField(value.ToString());
            DescriptionAttribute[] attributes = (DescriptionAttribute[])fi.GetCustomAttributes(typeof(DescriptionAttribute), false);
            return attributes.Length > 0 ? attributes[0].Description : value.ToString();
        }
        #endregion
    }
}
