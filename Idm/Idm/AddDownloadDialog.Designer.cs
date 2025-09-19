namespace Idm
{
    partial class AddDownloadDialog
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
            this.urlLabel = new System.Windows.Forms.Label();
            this.urlTextBox = new System.Windows.Forms.TextBox();
            this.savePathLabel = new System.Windows.Forms.Label();
            this.savePathTextBox = new System.Windows.Forms.TextBox();
            this.browseButton = new System.Windows.Forms.Button();
            this.scheduleCheckBox = new System.Windows.Forms.CheckBox();
            this.scheduleDateTimePicker = new System.Windows.Forms.DateTimePicker();
            this.okButton = new System.Windows.Forms.Button();
            this.cancelButton = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // urlLabel
            // 
            this.urlLabel.AutoSize = true;
            this.urlLabel.Location = new System.Drawing.Point(13, 13);
            this.urlLabel.Name = "urlLabel";
            this.urlLabel.Size = new System.Drawing.Size(82, 20);
            this.urlLabel.TabIndex = 0;
            this.urlLabel.Text = "رابط الملف:";
            // 
            // urlTextBox
            // 
            this.urlTextBox.Location = new System.Drawing.Point(17, 37);
            this.urlTextBox.Name = "urlTextBox";
            this.urlTextBox.Size = new System.Drawing.Size(455, 26);
            this.urlTextBox.TabIndex = 1;
            // 
            // savePathLabel
            // 
            this.savePathLabel.AutoSize = true;
            this.savePathLabel.Location = new System.Drawing.Point(13, 79);
            this.savePathLabel.Name = "savePathLabel";
            this.savePathLabel.Size = new System.Drawing.Size(80, 20);
            this.savePathLabel.TabIndex = 2;
            this.savePathLabel.Text = "حفظ في:";
            // 
            // savePathTextBox
            // 
            this.savePathTextBox.Location = new System.Drawing.Point(17, 103);
            this.savePathTextBox.Name = "savePathTextBox";
            this.savePathTextBox.Size = new System.Drawing.Size(354, 26);
            this.savePathTextBox.TabIndex = 3;
            // 
            // browseButton
            // 
            this.browseButton.Location = new System.Drawing.Point(377, 101);
            this.browseButton.Name = "browseButton";
            this.browseButton.Size = new System.Drawing.Size(95, 31);
            this.browseButton.TabIndex = 4;
            this.browseButton.Text = "تصفح...";
            this.browseButton.UseVisualStyleBackColor = true;
            this.browseButton.Click += new System.EventHandler(this.browseButton_Click);
            // 
            // scheduleCheckBox
            // 
            this.scheduleCheckBox.AutoSize = true;
            this.scheduleCheckBox.Location = new System.Drawing.Point(17, 150);
            this.scheduleCheckBox.Name = "scheduleCheckBox";
            this.scheduleCheckBox.Size = new System.Drawing.Size(117, 24);
            this.scheduleCheckBox.TabIndex = 5;
            this.scheduleCheckBox.Text = "جدولة التحميل";
            this.scheduleCheckBox.UseVisualStyleBackColor = true;
            this.scheduleCheckBox.CheckedChanged += new System.EventHandler(this.scheduleCheckBox_CheckedChanged);
            // 
            // scheduleDateTimePicker
            // 
            this.scheduleDateTimePicker.CustomFormat = "yyyy/MM/dd   hh:mm tt";
            this.scheduleDateTimePicker.Format = System.Windows.Forms.DateTimePickerFormat.Custom;
            this.scheduleDateTimePicker.Location = new System.Drawing.Point(140, 148);
            this.scheduleDateTimePicker.Name = "scheduleDateTimePicker";
            this.scheduleDateTimePicker.Size = new System.Drawing.Size(332, 26);
            this.scheduleDateTimePicker.TabIndex = 6;
            // 
            // okButton
            // 
            this.okButton.Location = new System.Drawing.Point(266, 198);
            this.okButton.Name = "okButton";
            this.okButton.Size = new System.Drawing.Size(100, 35);
            this.okButton.TabIndex = 7;
            this.okButton.Text = "موافق";
            this.okButton.UseVisualStyleBackColor = true;
            this.okButton.Click += new System.EventHandler(this.okButton_Click);
            // 
            // cancelButton
            // 
            this.cancelButton.DialogResult = System.Windows.Forms.DialogResult.Cancel;
            this.cancelButton.Location = new System.Drawing.Point(372, 198);
            this.cancelButton.Name = "cancelButton";
            this.cancelButton.Size = new System.Drawing.Size(100, 35);
            this.cancelButton.TabIndex = 8;
            this.cancelButton.Text = "إلغاء";
            this.cancelButton.UseVisualStyleBackColor = true;
            // 
            // AddDownloadDialog
            // 
            this.AcceptButton = this.okButton;
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 20F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.CancelButton = this.cancelButton;
            this.ClientSize = new System.Drawing.Size(484, 245);
            this.Controls.Add(this.cancelButton);
            this.Controls.Add(this.okButton);
            this.Controls.Add(this.scheduleDateTimePicker);
            this.Controls.Add(this.scheduleCheckBox);
            this.Controls.Add(this.browseButton);
            this.Controls.Add(this.savePathTextBox);
            this.Controls.Add(this.savePathLabel);
            this.Controls.Add(this.urlTextBox);
            this.Controls.Add(this.urlLabel);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "AddDownloadDialog";
            this.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.RightToLeftLayout = true;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "إضافة تحميل جديد";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label urlLabel;
        private System.Windows.Forms.TextBox urlTextBox;
        private System.Windows.Forms.Label savePathLabel;
        private System.Windows.Forms.TextBox savePathTextBox;
        private System.Windows.Forms.Button browseButton;
        private System.Windows.Forms.CheckBox scheduleCheckBox;
        private System.Windows.Forms.DateTimePicker scheduleDateTimePicker;
        private System.Windows.Forms.Button okButton;
        private System.Windows.Forms.Button cancelButton;
    }
}