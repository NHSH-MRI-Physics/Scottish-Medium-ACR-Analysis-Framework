namespace ACR_Phantom_GUI
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
            this.label3 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.OutputPath = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.StartButton = new System.Windows.Forms.Button();
            this.DCMPath = new System.Windows.Forms.TextBox();
            this.ShowAllOutput = new System.Windows.Forms.CheckBox();
            this.SeqSelector = new System.Windows.Forms.ComboBox();
            this.label4 = new System.Windows.Forms.Label();
            this.RunAllCheck = new System.Windows.Forms.CheckBox();
            this.RunSNRCheck = new System.Windows.Forms.CheckBox();
            this.RunGeometricAccuracy = new System.Windows.Forms.CheckBox();
            this.RunGhosting = new System.Windows.Forms.CheckBox();
            this.RunSlicePosition = new System.Windows.Forms.CheckBox();
            this.RunUniformity = new System.Windows.Forms.CheckBox();
            this.RunSliceThickness = new System.Windows.Forms.CheckBox();
            this.label5 = new System.Windows.Forms.Label();
            this.ResultComboBox = new System.Windows.Forms.ComboBox();
            this.ViewResult = new System.Windows.Forms.Button();
            this.label6 = new System.Windows.Forms.Label();
            this.LogBoxField = new System.Windows.Forms.RichTextBox();
            this.RunSpatialRes = new System.Windows.Forms.CheckBox();
            this.Results = new System.Windows.Forms.RichTextBox();
            this.label7 = new System.Windows.Forms.Label();
            this.UpdateDocker = new System.Windows.Forms.Button();
            this.OfflineMode = new System.Windows.Forms.CheckBox();
            this.SuspendLayout();
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(282, 349);
            this.label3.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(36, 20);
            this.label3.TabIndex = 6;
            this.label3.Text = "Log";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(3, 58);
            this.label2.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(100, 20);
            this.label2.TabIndex = 4;
            this.label2.Text = "Results Path";
            // 
            // OutputPath
            // 
            this.OutputPath.Location = new System.Drawing.Point(112, 54);
            this.OutputPath.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.OutputPath.Name = "OutputPath";
            this.OutputPath.ReadOnly = true;
            this.OutputPath.Size = new System.Drawing.Size(696, 26);
            this.OutputPath.TabIndex = 3;
            this.OutputPath.MouseClick += new System.Windows.Forms.MouseEventHandler(this.OutputPath_click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(3, 18);
            this.label1.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(99, 20);
            this.label1.TabIndex = 2;
            this.label1.Text = "DICOM Path";
            // 
            // StartButton
            // 
            this.StartButton.Location = new System.Drawing.Point(8, 402);
            this.StartButton.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.StartButton.Name = "StartButton";
            this.StartButton.Size = new System.Drawing.Size(270, 35);
            this.StartButton.TabIndex = 0;
            this.StartButton.Text = "Start Analysis";
            this.StartButton.UseVisualStyleBackColor = true;
            this.StartButton.Click += new System.EventHandler(this.StartButton_Click);
            // 
            // DCMPath
            // 
            this.DCMPath.Location = new System.Drawing.Point(112, 14);
            this.DCMPath.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.DCMPath.Name = "DCMPath";
            this.DCMPath.ReadOnly = true;
            this.DCMPath.Size = new System.Drawing.Size(696, 26);
            this.DCMPath.TabIndex = 1;
            this.DCMPath.MouseClick += new System.Windows.Forms.MouseEventHandler(this.DCMPath_click);
            // 
            // ShowAllOutput
            // 
            this.ShowAllOutput.AutoSize = true;
            this.ShowAllOutput.Location = new System.Drawing.Point(328, 348);
            this.ShowAllOutput.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.ShowAllOutput.Name = "ShowAllOutput";
            this.ShowAllOutput.Size = new System.Drawing.Size(149, 24);
            this.ShowAllOutput.TabIndex = 7;
            this.ShowAllOutput.Text = "Show All Output";
            this.ShowAllOutput.UseVisualStyleBackColor = true;
            // 
            // SeqSelector
            // 
            this.SeqSelector.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.SeqSelector.FormattingEnabled = true;
            this.SeqSelector.Location = new System.Drawing.Point(819, 78);
            this.SeqSelector.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.SeqSelector.Name = "SeqSelector";
            this.SeqSelector.Size = new System.Drawing.Size(328, 28);
            this.SeqSelector.TabIndex = 8;
            this.SeqSelector.SelectedIndexChanged += new System.EventHandler(this.SeqSelector_SelectedIndexChanged);
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(819, 54);
            this.label4.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(152, 20);
            this.label4.TabIndex = 9;
            this.label4.Text = "Sequence Selection";
            // 
            // RunAllCheck
            // 
            this.RunAllCheck.AutoSize = true;
            this.RunAllCheck.Checked = true;
            this.RunAllCheck.CheckState = System.Windows.Forms.CheckState.Checked;
            this.RunAllCheck.Location = new System.Drawing.Point(3, 123);
            this.RunAllCheck.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.RunAllCheck.Name = "RunAllCheck";
            this.RunAllCheck.Size = new System.Drawing.Size(86, 24);
            this.RunAllCheck.TabIndex = 11;
            this.RunAllCheck.Text = "Run All";
            this.RunAllCheck.UseVisualStyleBackColor = true;
            this.RunAllCheck.CheckedChanged += new System.EventHandler(this.RunAllCheck_CheckedChanged);
            // 
            // RunSNRCheck
            // 
            this.RunSNRCheck.AutoSize = true;
            this.RunSNRCheck.Enabled = false;
            this.RunSNRCheck.Location = new System.Drawing.Point(3, 300);
            this.RunSNRCheck.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.RunSNRCheck.Name = "RunSNRCheck";
            this.RunSNRCheck.Size = new System.Drawing.Size(103, 24);
            this.RunSNRCheck.TabIndex = 12;
            this.RunSNRCheck.Text = "Run SNR";
            this.RunSNRCheck.UseVisualStyleBackColor = true;
            // 
            // RunGeometricAccuracy
            // 
            this.RunGeometricAccuracy.AutoSize = true;
            this.RunGeometricAccuracy.Enabled = false;
            this.RunGeometricAccuracy.Location = new System.Drawing.Point(3, 335);
            this.RunGeometricAccuracy.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.RunGeometricAccuracy.Name = "RunGeometricAccuracy";
            this.RunGeometricAccuracy.Size = new System.Drawing.Size(212, 24);
            this.RunGeometricAccuracy.TabIndex = 13;
            this.RunGeometricAccuracy.Text = "Run Geometric Accuracy";
            this.RunGeometricAccuracy.UseVisualStyleBackColor = true;
            // 
            // RunGhosting
            // 
            this.RunGhosting.AutoSize = true;
            this.RunGhosting.Enabled = false;
            this.RunGhosting.Location = new System.Drawing.Point(3, 371);
            this.RunGhosting.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.RunGhosting.Name = "RunGhosting";
            this.RunGhosting.Size = new System.Drawing.Size(134, 24);
            this.RunGhosting.TabIndex = 14;
            this.RunGhosting.Text = "Run Ghosting";
            this.RunGhosting.UseVisualStyleBackColor = true;
            // 
            // RunSlicePosition
            // 
            this.RunSlicePosition.AutoSize = true;
            this.RunSlicePosition.Enabled = false;
            this.RunSlicePosition.Location = new System.Drawing.Point(3, 192);
            this.RunSlicePosition.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.RunSlicePosition.Name = "RunSlicePosition";
            this.RunSlicePosition.Size = new System.Drawing.Size(163, 24);
            this.RunSlicePosition.TabIndex = 16;
            this.RunSlicePosition.Text = "Run Slice Position";
            this.RunSlicePosition.UseVisualStyleBackColor = true;
            // 
            // RunUniformity
            // 
            this.RunUniformity.AutoSize = true;
            this.RunUniformity.Enabled = false;
            this.RunUniformity.Location = new System.Drawing.Point(3, 157);
            this.RunUniformity.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.RunUniformity.Name = "RunUniformity";
            this.RunUniformity.Size = new System.Drawing.Size(140, 24);
            this.RunUniformity.TabIndex = 15;
            this.RunUniformity.Text = "Run Uniformity";
            this.RunUniformity.UseVisualStyleBackColor = true;
            // 
            // RunSliceThickness
            // 
            this.RunSliceThickness.AutoSize = true;
            this.RunSliceThickness.Enabled = false;
            this.RunSliceThickness.Location = new System.Drawing.Point(3, 265);
            this.RunSliceThickness.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.RunSliceThickness.Name = "RunSliceThickness";
            this.RunSliceThickness.Size = new System.Drawing.Size(178, 24);
            this.RunSliceThickness.TabIndex = 18;
            this.RunSliceThickness.Text = "Run Slice Thickness";
            this.RunSliceThickness.UseVisualStyleBackColor = true;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(3, 92);
            this.label5.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(103, 20);
            this.label5.TabIndex = 19;
            this.label5.Text = "Test Selector";
            // 
            // ResultComboBox
            // 
            this.ResultComboBox.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.ResultComboBox.Enabled = false;
            this.ResultComboBox.FormattingEnabled = true;
            this.ResultComboBox.Location = new System.Drawing.Point(8, 466);
            this.ResultComboBox.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.ResultComboBox.Name = "ResultComboBox";
            this.ResultComboBox.Size = new System.Drawing.Size(268, 28);
            this.ResultComboBox.TabIndex = 20;
            // 
            // ViewResult
            // 
            this.ViewResult.Enabled = false;
            this.ViewResult.Location = new System.Drawing.Point(8, 508);
            this.ViewResult.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.ViewResult.Name = "ViewResult";
            this.ViewResult.Size = new System.Drawing.Size(270, 35);
            this.ViewResult.TabIndex = 21;
            this.ViewResult.Text = "View Result";
            this.ViewResult.UseVisualStyleBackColor = true;
            this.ViewResult.Click += new System.EventHandler(this.ViewResult_Click);
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(12, 442);
            this.label6.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(107, 20);
            this.label6.TabIndex = 22;
            this.label6.Text = "Result Viewer";
            // 
            // LogBoxField
            // 
            this.LogBoxField.Location = new System.Drawing.Point(286, 374);
            this.LogBoxField.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.LogBoxField.Name = "LogBoxField";
            this.LogBoxField.ReadOnly = true;
            this.LogBoxField.Size = new System.Drawing.Size(860, 155);
            this.LogBoxField.TabIndex = 23;
            this.LogBoxField.Text = "";
            // 
            // RunSpatialRes
            // 
            this.RunSpatialRes.AutoSize = true;
            this.RunSpatialRes.Enabled = false;
            this.RunSpatialRes.Location = new System.Drawing.Point(3, 228);
            this.RunSpatialRes.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.RunSpatialRes.Name = "RunSpatialRes";
            this.RunSpatialRes.Size = new System.Drawing.Size(207, 24);
            this.RunSpatialRes.TabIndex = 17;
            this.RunSpatialRes.Text = "Run Spatial Resoloution";
            this.RunSpatialRes.UseVisualStyleBackColor = true;
            // 
            // Results
            // 
            this.Results.Location = new System.Drawing.Point(286, 120);
            this.Results.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.Results.Name = "Results";
            this.Results.ReadOnly = true;
            this.Results.Size = new System.Drawing.Size(860, 216);
            this.Results.TabIndex = 24;
            this.Results.Text = "";
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(282, 95);
            this.label7.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(63, 20);
            this.label7.TabIndex = 25;
            this.label7.Text = "Results";
            // 
            // UpdateDocker
            // 
            this.UpdateDocker.Location = new System.Drawing.Point(819, 9);
            this.UpdateDocker.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.UpdateDocker.Name = "UpdateDocker";
            this.UpdateDocker.Size = new System.Drawing.Size(162, 35);
            this.UpdateDocker.TabIndex = 26;
            this.UpdateDocker.Text = "Update Backend";
            this.UpdateDocker.UseVisualStyleBackColor = true;
            this.UpdateDocker.Click += new System.EventHandler(this.UpdateDocker_Click);
            // 
            // OfflineMode
            // 
            this.OfflineMode.AutoSize = true;
            this.OfflineMode.Location = new System.Drawing.Point(1005, 15);
            this.OfflineMode.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.OfflineMode.Name = "OfflineMode";
            this.OfflineMode.Size = new System.Drawing.Size(125, 24);
            this.OfflineMode.TabIndex = 27;
            this.OfflineMode.Text = "Offline Mode";
            this.OfflineMode.UseVisualStyleBackColor = true;
            this.OfflineMode.CheckedChanged += new System.EventHandler(this.OfflineMode_CheckedChanged);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 20F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1167, 549);
            this.Controls.Add(this.OfflineMode);
            this.Controls.Add(this.UpdateDocker);
            this.Controls.Add(this.label7);
            this.Controls.Add(this.Results);
            this.Controls.Add(this.LogBoxField);
            this.Controls.Add(this.label6);
            this.Controls.Add(this.ViewResult);
            this.Controls.Add(this.ResultComboBox);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.RunSliceThickness);
            this.Controls.Add(this.RunSpatialRes);
            this.Controls.Add(this.RunSlicePosition);
            this.Controls.Add(this.RunUniformity);
            this.Controls.Add(this.RunGhosting);
            this.Controls.Add(this.RunGeometricAccuracy);
            this.Controls.Add(this.RunSNRCheck);
            this.Controls.Add(this.RunAllCheck);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.SeqSelector);
            this.Controls.Add(this.ShowAllOutput);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.DCMPath);
            this.Controls.Add(this.StartButton);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.OutputPath);
            this.Controls.Add(this.label1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.MaximizeBox = false;
            this.Name = "Form1";
            this.Text = "Medium ACR Analysis ";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.Button StartButton;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox OutputPath;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox DCMPath;
        private System.Windows.Forms.CheckBox ShowAllOutput;
        private System.Windows.Forms.ComboBox SeqSelector;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.CheckBox RunAllCheck;
        private System.Windows.Forms.CheckBox RunSNRCheck;
        private System.Windows.Forms.CheckBox RunGeometricAccuracy;
        private System.Windows.Forms.CheckBox RunGhosting;
        private System.Windows.Forms.CheckBox RunSlicePosition;
        private System.Windows.Forms.CheckBox RunUniformity;
        private System.Windows.Forms.CheckBox RunSliceThickness;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.ComboBox ResultComboBox;
        private System.Windows.Forms.Button ViewResult;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.RichTextBox LogBoxField;
        private System.Windows.Forms.CheckBox RunSpatialRes;
        private System.Windows.Forms.RichTextBox Results;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.Button UpdateDocker;
        private System.Windows.Forms.CheckBox OfflineMode;
    }
}

