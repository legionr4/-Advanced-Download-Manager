﻿using System;
using System.IO;
using System.Windows.Forms;

namespace Idm
{
    public partial class AddDownloadDialog : Form
    {
        public string DownloadUrl => urlTextBox.Text;
        public string SavePath => savePathTextBox.Text;
        public DateTime? ScheduledTime => scheduleCheckBox.Checked ? scheduleDateTimePicker.Value : (DateTime?)null;
        
        public AddDownloadDialog(string initialUrl = "", bool isRefreshMode = false)
        {
            InitializeComponent();

            if (isRefreshMode)
            {
                this.Text = "تحديث رابط التحميل";
                urlLabel.Text = "بعد تحديث الصفحة في متصفحك، الصق رابط التحميل الجديد هنا:";
                savePathLabel.Visible = false;
                savePathTextBox.Visible = false;
                browseButton.Visible = false;
                scheduleCheckBox.Visible = false;
                scheduleDateTimePicker.Visible = false;
                this.Height -= 120; // تقليص ارتفاع النافذة
            }
            else
            {
                scheduleDateTimePicker.Value = DateTime.Now.AddMinutes(5);
                scheduleDateTimePicker.Enabled = false;
            }

            // إذا لم يتم تمرير رابط، حاول لصق المحتوى من الحافظة
            if (string.IsNullOrWhiteSpace(initialUrl) && Clipboard.ContainsText())
            {
                string clipboardText = Clipboard.GetText();
                if (clipboardText.StartsWith("http", StringComparison.OrdinalIgnoreCase))
                {
                    urlTextBox.Text = clipboardText;
                }
            }
            else
            {
                urlTextBox.Text = initialUrl;
            }
        }

        private void browseButton_Click(object sender, EventArgs e)
        {
            using (var sfd = new SaveFileDialog())
            {
                try
                {
                    if (!string.IsNullOrWhiteSpace(urlTextBox.Text))
                    {
                        sfd.FileName = Path.GetFileName(new Uri(urlTextBox.Text).AbsolutePath);
                    }
                }
                catch { /* Ignore invalid URLs for now */ }

                sfd.Filter = "All files (*.*)|*.*";
                if (sfd.ShowDialog(this) == DialogResult.OK)
                {
                    savePathTextBox.Text = sfd.FileName;
                }
            }
        }

        private void scheduleCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            scheduleDateTimePicker.Enabled = scheduleCheckBox.Checked;
        }

        private void okButton_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(DownloadUrl) || (!savePathTextBox.Visible && string.IsNullOrWhiteSpace(SavePath)))
            {
                MessageBox.Show("الرجاء إدخال رابط الملف ومسار الحفظ.", "بيانات ناقصة", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            this.DialogResult = DialogResult.OK;
            this.Close();
        }
    }
}