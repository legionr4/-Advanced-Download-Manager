using System;
using System.Windows.Forms;

namespace Idm
{
    public partial class DownloadProgressForm : Form
    {
        public DownloadProgressForm()
        {
            InitializeComponent();
        }

        public void UpdateProgress(string fileName, long downloadedBytes, long totalBytes, double speed)
        {
            // هذا يضمن أن التحديثات تحدث بأمان على خيط واجهة المستخدم
            if (this.InvokeRequired)
            {
                this.Invoke((Action)(() => UpdateProgress(fileName, downloadedBytes, totalBytes, speed)));
                return;
            }

            fileNameLabel.Text = System.IO.Path.GetFileName(fileName);

            if (totalBytes > 0)
            {
                progressBar.Style = ProgressBarStyle.Blocks;
                double percentage = (double)downloadedBytes * 100 / totalBytes;
                progressBar.Value = (int)percentage;
                progressLabel.Text = $"{FormatBytes(downloadedBytes)} / {FormatBytes(totalBytes)} ({percentage:F2}%)";
            }
            else
            {
                // إذا كان حجم الملف غير معروف، استخدم شريط تقدم متحرك
                progressBar.Style = ProgressBarStyle.Marquee;
                progressLabel.Text = $"{FormatBytes(downloadedBytes)} / ???";
            }

            speedLabel.Text = $"{FormatBytes(speed)}/s";
        }

        public void UpdateStatus(string status)
        {
            if (this.InvokeRequired)
            {
                this.Invoke((Action)(() => UpdateStatus(status)));
                return;
            }
            statusValueLabel.Text = status;
        }

        // دالة مساعدة لتنسيق حجم الملفات
        private string FormatBytes(double bytes)
        {
            string[] suffix = { "B", "KB", "MB", "GB", "TB" };
            int i = 0;
            while (bytes >= 1024 && i < suffix.Length - 1)
            {
                bytes /= 1024;
                i++;
            }
            return $"{bytes:F2} {suffix[i]}";
        }
    }
}
