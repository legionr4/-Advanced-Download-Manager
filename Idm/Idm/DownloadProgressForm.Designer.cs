namespace Idm
{
    partial class DownloadProgressForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            this.fileNameLabel = new System.Windows.Forms.Label();
            this.progressBar = new System.Windows.Forms.ProgressBar();
            this.progressLabel = new System.Windows.Forms.Label();
            this.speedLabel = new System.Windows.Forms.Label();
            this.statusLabel = new System.Windows.Forms.Label();
            this.statusValueLabel = new System.Windows.Forms.Label();
            this.SuspendLayout();
            // 
            // fileNameLabel
            // 
            this.fileNameLabel.AutoEllipsis = true;
            this.fileNameLabel.Font = new System.Drawing.Font("Microsoft Sans Serif", 8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.fileNameLabel.Location = new System.Drawing.Point(12, 9);
            this.fileNameLabel.Name = "fileNameLabel";
            this.fileNameLabel.Size = new System.Drawing.Size(460, 20);
            this.fileNameLabel.TabIndex = 0;
            this.fileNameLabel.Text = "اسم الملف";
            // 
            // progressBar
            // 
            this.progressBar.Location = new System.Drawing.Point(12, 42);
            this.progressBar.Name = "progressBar";
            this.progressBar.Size = new System.Drawing.Size(460, 23);
            this.progressBar.TabIndex = 1;
            // 
            // progressLabel
            // 
            this.progressLabel.AutoSize = true;
            this.progressLabel.Location = new System.Drawing.Point(12, 78);
            this.progressLabel.Name = "progressLabel";
            this.progressLabel.Size = new System.Drawing.Size(111, 20);
            this.progressLabel.TabIndex = 2;
            this.progressLabel.Text = "0 MB / 0 MB";
            // 
            // speedLabel
            // 
            this.speedLabel.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.speedLabel.Location = new System.Drawing.Point(322, 78);
            this.speedLabel.Name = "speedLabel";
            this.speedLabel.Size = new System.Drawing.Size(150, 20);
            this.speedLabel.TabIndex = 3;
            this.speedLabel.Text = "0 KB/s";
            this.speedLabel.TextAlign = System.Drawing.ContentAlignment.TopRight;
            // 
            // statusLabel
            // 
            this.statusLabel.AutoSize = true;
            this.statusLabel.Location = new System.Drawing.Point(12, 111);
            this.statusLabel.Name = "statusLabel";
            this.statusLabel.Size = new System.Drawing.Size(47, 20);
            this.statusLabel.TabIndex = 4;
            this.statusLabel.Text = "الحالة:";
            // 
            // statusValueLabel
            // 
            this.statusValueLabel.AutoSize = true;
            this.statusValueLabel.Location = new System.Drawing.Point(65, 111);
            this.statusValueLabel.Name = "statusValueLabel";
            this.statusValueLabel.Size = new System.Drawing.Size(73, 20);
            this.statusValueLabel.TabIndex = 5;
            this.statusValueLabel.Text = "جاري البدء...";
            // 
            // DownloadProgressForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 20F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(484, 149);
            this.Controls.Add(this.statusValueLabel);
            this.Controls.Add(this.statusLabel);
            this.Controls.Add(this.speedLabel);
            this.Controls.Add(this.progressLabel);
            this.Controls.Add(this.progressBar);
            this.Controls.Add(this.fileNameLabel);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.Name = "DownloadProgressForm";
            this.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.RightToLeftLayout = true;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "تقدم التحميل";
            this.TopMost = true;
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        #endregion

        private System.Windows.Forms.Label fileNameLabel;
        private System.Windows.Forms.ProgressBar progressBar;
        private System.Windows.Forms.Label progressLabel;
        private System.Windows.Forms.Label speedLabel;
        private System.Windows.Forms.Label statusLabel;
        private System.Windows.Forms.Label statusValueLabel;
    }
}
