namespace Idm
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.addButton = new System.Windows.Forms.Button();
            this.removeButton = new System.Windows.Forms.Button();
            this.downloadsListView = new System.Windows.Forms.ListView();
            this.columnHeader1 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader2 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader3 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader4 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.columnHeader5 = ((System.Windows.Forms.ColumnHeader)(new System.Windows.Forms.ColumnHeader()));
            this.actionButton = new System.Windows.Forms.Button();
            this.uiUpdateTimer = new System.Windows.Forms.Timer(this.components);
            this.removeCompletedButton = new System.Windows.Forms.Button();
            this.concurrentDownloadsLabel = new System.Windows.Forms.Label();
            this.concurrentDownloadsNumeric = new System.Windows.Forms.NumericUpDown();
            this.partsPerDownloadLabel = new System.Windows.Forms.Label();
            this.partsPerDownloadNumeric = new System.Windows.Forms.NumericUpDown();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.fileToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.exitToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.optionsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.setDefaultSaveFolderToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.helpToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.aboutToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            ((System.ComponentModel.ISupportInitialize)(this.concurrentDownloadsNumeric)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.partsPerDownloadNumeric)).BeginInit();
            this.menuStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // addButton
            // 
            this.addButton.Location = new System.Drawing.Point(12, 45);
            this.addButton.Name = "addButton";
            this.addButton.Size = new System.Drawing.Size(120, 38);
            this.addButton.TabIndex = 0;
            this.addButton.Text = "إضافة تحميل";
            this.addButton.UseVisualStyleBackColor = true;
            this.addButton.Click += new System.EventHandler(this.addButton_Click);
            // 
            // removeButton
            // 
            this.removeButton.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.removeButton.Location = new System.Drawing.Point(792, 45);
            this.removeButton.Name = "removeButton";
            this.removeButton.Size = new System.Drawing.Size(80, 38);
            this.removeButton.TabIndex = 1;
            this.removeButton.Text = "إزالة";
            this.removeButton.UseVisualStyleBackColor = true;
            this.removeButton.Click += new System.EventHandler(this.removeButton_Click);
            // 
            // downloadsListView
            // 
            this.downloadsListView.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.downloadsListView.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.columnHeader1,
            this.columnHeader2,
            this.columnHeader3,
            this.columnHeader4,
            this.columnHeader5});
            this.downloadsListView.FullRowSelect = true;
            this.downloadsListView.HideSelection = false;
            this.downloadsListView.Location = new System.Drawing.Point(12, 89);
            this.downloadsListView.MultiSelect = false;
            this.downloadsListView.Name = "downloadsListView";
            this.downloadsListView.Size = new System.Drawing.Size(860, 382);
            this.downloadsListView.TabIndex = 2;
            this.downloadsListView.UseCompatibleStateImageBehavior = false;
            this.downloadsListView.View = System.Windows.Forms.View.Details;
            this.downloadsListView.SelectedIndexChanged += new System.EventHandler(this.downloadsListView_SelectedIndexChanged);
            // 
            // columnHeader1
            // 
            this.columnHeader1.Text = "اسم الملف";
            this.columnHeader1.Width = 300;
            // 
            // columnHeader2
            // 
            this.columnHeader2.Text = "الحجم";
            this.columnHeader2.Width = 120;
            // 
            // columnHeader3
            // 
            this.columnHeader3.Text = "التقدم";
            this.columnHeader3.Width = 120;
            // 
            // columnHeader4
            // 
            this.columnHeader4.Text = "السرعة";
            this.columnHeader4.Width = 120;
            // 
            // columnHeader5
            // 
            this.columnHeader5.Text = "الحالة";
            this.columnHeader5.Width = 150;
            // 
            // actionButton
            // 
            this.actionButton.Location = new System.Drawing.Point(138, 45);
            this.actionButton.Name = "actionButton";
            this.actionButton.Size = new System.Drawing.Size(135, 38);
            this.actionButton.TabIndex = 3;
            this.actionButton.Text = "بدء / إيقاف مؤقت";
            this.actionButton.UseVisualStyleBackColor = true;
            this.actionButton.Click += new System.EventHandler(this.actionButton_Click);
            // 
            // uiUpdateTimer
            // 
            this.uiUpdateTimer.Enabled = true;
            this.uiUpdateTimer.Interval = 1000;
            this.uiUpdateTimer.Tick += new System.EventHandler(this.uiUpdateTimer_Tick);
            // 
            // removeCompletedButton
            // 
            this.removeCompletedButton.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.removeCompletedButton.Location = new System.Drawing.Point(641, 45);
            this.removeCompletedButton.Name = "removeCompletedButton";
            this.removeCompletedButton.Size = new System.Drawing.Size(145, 38);
            this.removeCompletedButton.TabIndex = 4;
            this.removeCompletedButton.Text = "إزالة المكتمل";
            this.removeCompletedButton.UseVisualStyleBackColor = true;
            this.removeCompletedButton.Click += new System.EventHandler(this.removeCompletedButton_Click);
            // 
            // concurrentDownloadsLabel
            // 
            this.concurrentDownloadsLabel.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.concurrentDownloadsLabel.AutoSize = true;
            this.concurrentDownloadsLabel.Location = new System.Drawing.Point(489, 54);
            this.concurrentDownloadsLabel.Name = "concurrentDownloadsLabel";
            this.concurrentDownloadsLabel.Size = new System.Drawing.Size(120, 20);
            this.concurrentDownloadsLabel.TabIndex = 5;
            this.concurrentDownloadsLabel.Text = "تحميلات متزامنة:";
            // 
            // concurrentDownloadsNumeric
            // 
            this.concurrentDownloadsNumeric.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.concurrentDownloadsNumeric.Location = new System.Drawing.Point(615, 52);
            this.concurrentDownloadsNumeric.Maximum = new decimal(new int[] {
            10,
            0,
            0,
            0});
            this.concurrentDownloadsNumeric.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.concurrentDownloadsNumeric.Name = "concurrentDownloadsNumeric";
            this.concurrentDownloadsNumeric.Size = new System.Drawing.Size(51, 26);
            this.concurrentDownloadsNumeric.TabIndex = 6;
            this.concurrentDownloadsNumeric.Value = new decimal(new int[] {
            3,
            0,
            0,
            0});
            this.concurrentDownloadsNumeric.ValueChanged += new System.EventHandler(this.concurrentDownloadsNumeric_ValueChanged);
            // 
            // partsPerDownloadLabel
            // 
            this.partsPerDownloadLabel.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.partsPerDownloadLabel.AutoSize = true;
            this.partsPerDownloadLabel.Location = new System.Drawing.Point(322, 54);
            this.partsPerDownloadLabel.Name = "partsPerDownloadLabel";
            this.partsPerDownloadLabel.Size = new System.Drawing.Size(49, 20);
            this.partsPerDownloadLabel.TabIndex = 7;
            this.partsPerDownloadLabel.Text = "الأجزاء:";
            // 
            // partsPerDownloadNumeric
            // 
            this.partsPerDownloadNumeric.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.partsPerDownloadNumeric.Location = new System.Drawing.Point(377, 52);
            this.partsPerDownloadNumeric.Maximum = new decimal(new int[] {
            16,
            0,
            0,
            0});
            this.partsPerDownloadNumeric.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.partsPerDownloadNumeric.Name = "partsPerDownloadNumeric";
            this.partsPerDownloadNumeric.Size = new System.Drawing.Size(51, 26);
            this.partsPerDownloadNumeric.TabIndex = 8;
            this.partsPerDownloadNumeric.Value = new decimal(new int[] {
            8,
            0,
            0,
            0});
            // 
            // menuStrip1
            // 
            this.menuStrip1.GripMargin = new System.Windows.Forms.Padding(2, 2, 0, 2);
            this.menuStrip1.ImageScalingSize = new System.Drawing.Size(24, 24);
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.fileToolStripMenuItem,
            this.optionsToolStripMenuItem,
            this.helpToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(884, 33);
            this.menuStrip1.TabIndex = 9;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // fileToolStripMenuItem
            // 
            this.fileToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.exitToolStripMenuItem});
            this.fileToolStripMenuItem.Name = "fileToolStripMenuItem";
            this.fileToolStripMenuItem.Size = new System.Drawing.Size(54, 29);
            this.fileToolStripMenuItem.Text = "ملف";
            // 
            // exitToolStripMenuItem
            // 
            this.exitToolStripMenuItem.Name = "exitToolStripMenuItem";
            this.exitToolStripMenuItem.Size = new System.Drawing.Size(148, 34);
            this.exitToolStripMenuItem.Text = "خروج";
            this.exitToolStripMenuItem.Click += new System.EventHandler(this.exitToolStripMenuItem_Click);
            // 
            // optionsToolStripMenuItem
            // 
            this.optionsToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.setDefaultSaveFolderToolStripMenuItem});
            this.optionsToolStripMenuItem.Name = "optionsToolStripMenuItem";
            this.optionsToolStripMenuItem.Size = new System.Drawing.Size(78, 29);
            this.optionsToolStripMenuItem.Text = "خيارات";
            // 
            // setDefaultSaveFolderToolStripMenuItem
            // 
            this.setDefaultSaveFolderToolStripMenuItem.Name = "setDefaultSaveFolderToolStripMenuItem";
            this.setDefaultSaveFolderToolStripMenuItem.Size = new System.Drawing.Size(341, 34);
            this.setDefaultSaveFolderToolStripMenuItem.Text = "تحديد مجلد الحفظ الافتراضي...";
            this.setDefaultSaveFolderToolStripMenuItem.Click += new System.EventHandler(this.setDefaultSaveFolderToolStripMenuItem_Click);
            // 
            // helpToolStripMenuItem
            // 
            this.helpToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.aboutToolStripMenuItem});
            this.helpToolStripMenuItem.Name = "helpToolStripMenuItem";
            this.helpToolStripMenuItem.Size = new System.Drawing.Size(79, 29);
            this.helpToolStripMenuItem.Text = "مساعدة";
            // 
            // aboutToolStripMenuItem
            // 
            this.aboutToolStripMenuItem.Name = "aboutToolStripMenuItem";
            this.aboutToolStripMenuItem.Size = new System.Drawing.Size(270, 34);
            this.aboutToolStripMenuItem.Text = "حول البرنامج";
            this.aboutToolStripMenuItem.Click += new System.EventHandler(this.aboutToolStripMenuItem_Click);
            // 
            // Form1
            // 
            this.ClientSize = new System.Drawing.Size(884, 474);
            this.Controls.Add(this.partsPerDownloadNumeric);
            this.Controls.Add(this.partsPerDownloadLabel);
            this.Controls.Add(this.concurrentDownloadsNumeric);
            this.Controls.Add(this.concurrentDownloadsLabel);
            this.Controls.Add(this.removeCompletedButton);
            this.Controls.Add(this.actionButton);
            this.Controls.Add(this.downloadsListView);
            this.Controls.Add(this.removeButton);
            this.Controls.Add(this.addButton);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "Form1";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "مدير التحميل";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.Form1_FormClosing);
            ((System.ComponentModel.ISupportInitialize)(this.concurrentDownloadsNumeric)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.partsPerDownloadNumeric)).EndInit();
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button addButton;
        private System.Windows.Forms.Button removeButton;
        private System.Windows.Forms.ListView downloadsListView;
        private System.Windows.Forms.ColumnHeader columnHeader1;
        private System.Windows.Forms.ColumnHeader columnHeader2;
        private System.Windows.Forms.ColumnHeader columnHeader3;
        private System.Windows.Forms.ColumnHeader columnHeader4;
        private System.Windows.Forms.ColumnHeader columnHeader5;
        private System.Windows.Forms.Button actionButton;
        private System.Windows.Forms.Timer uiUpdateTimer;
        private System.Windows.Forms.Button removeCompletedButton;
        private System.Windows.Forms.Label concurrentDownloadsLabel;
        private System.Windows.Forms.NumericUpDown concurrentDownloadsNumeric;
        private System.Windows.Forms.Label partsPerDownloadLabel;
        private System.Windows.Forms.NumericUpDown partsPerDownloadNumeric;
        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.ToolStripMenuItem fileToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem exitToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem optionsToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem setDefaultSaveFolderToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem helpToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem aboutToolStripMenuItem;
    }
}
