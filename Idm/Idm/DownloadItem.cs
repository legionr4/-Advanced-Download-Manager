using System;
using System.ComponentModel;
using System.Threading;
using System.Windows.Forms;
using Newtonsoft.Json;  

namespace Idm
{
    public enum DownloadStatus
    {
        [Description("في الانتظار")]
        Queued,
        [Description("مجدول")]
        Scheduled,
        [Description("جاري التحميل")]
        Downloading,
        [Description("متوقف مؤقتاً")]
        Paused,
        [Description("خطأ، إعادة محاولة...")]
        ErrorRetrying,
        [Description("مكتمل")]
        Completed,
        [Description("خطأ")]
        Error,
        [Description("تم الإلغاء")]
        Cancelled,
        [Description("جاري التجميع")]
        Combining
    }

    public class DownloadItem
    {
        public string Id { get; } = System.Guid.NewGuid().ToString();
        public string Url { get; set; }
        public string FilePath { get; set; }
        public DownloadStatus Status { get; set; } = DownloadStatus.Queued;
        public DateTime? ScheduledTime { get; set; }
        public long TotalBytes { get; set; }
        public int NumParts { get; set; } = 8; // Default to 8 parts
        public long DownloadedBytes { get; set; }

        [JsonIgnore]
        public double Speed { get; set; } // Bytes per second
        public string ErrorMessage { get; set; }

        // Objects for controlling the download task
        [JsonIgnore]
        public CancellationTokenSource Cts { get; set; }
        [JsonIgnore]
        public ManualResetEventSlim PauseEvent { get; } = new ManualResetEventSlim(true);
        [JsonIgnore]
        public ListViewItem ListViewItem { get; set; }
    }
}