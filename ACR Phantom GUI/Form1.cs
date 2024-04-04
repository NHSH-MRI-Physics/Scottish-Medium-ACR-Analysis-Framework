using EvilDICOM.Core;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml.Linq;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;
using EvilDICOM;
using EvilDICOM.Core.Helpers;
using System.IO;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using FellowOakDicom;
using FellowOakDicom.Imaging;
using static System.Net.Mime.MediaTypeNames;
using FellowOakDicom.Imaging.Codec;
using FellowOakDicom.Network;
using System.Text.RegularExpressions;
using System.Runtime.CompilerServices;
using static System.Net.WebRequestMethods;
using System.Collections;
using EvilDICOM.Core.Element;
using static System.Windows.Forms.LinkLabel;

namespace ACR_Phantom_GUI
{
    public partial class Form1 : Form
    {

        private BackgroundWorker Worker;
        private BackgroundWorker Updater;
        private BackgroundWorker Loader;
        private string Arguments = "";
        private Dictionary<string, List<FileInfo>> FileDict;
        private string UpdaterString = "";
        private List<string> ImageChecker = new List<string>();
        public Form1()
        {
            try
            {
                InitializeComponent();
                Worker = new BackgroundWorker();
                Worker.DoWork += Worker_DoWork;
                Worker.ProgressChanged += Worker_ProgressChanged;
                Worker.RunWorkerCompleted += Worker_RunWorkerCompleted;
                Worker.WorkerReportsProgress = true;
                Worker.WorkerSupportsCancellation = true;

                Updater = new BackgroundWorker();
                Updater.DoWork += Updater_DoWork;
                Updater.RunWorkerCompleted += Updater_RunWorkerCompleted;

                Loader = new BackgroundWorker();
                Loader.DoWork += Loader_DoWork;
                Loader.RunWorkerCompleted += Loader_RunWorkerCompleted;

                var processInfo = new ProcessStartInfo("docker", $"images doctorspacemanphd/dockeracrphantom");
                RunProcess(processInfo, new DataReceivedEventHandler(OutputImageCheck), new DataReceivedEventHandler(OutputImageCheck));
                ImageChecker.RemoveAt(0);
                bool ImageFound = false;
                foreach(string Image in ImageChecker)
                {
                    ImageFound= Image.Contains("doctorspacemanphd/dockeracrphantom");
                }

               if (ImageFound==false)
                    LogBoxField.AppendText("No docker image found, update backend or set offline mode" + Environment.NewLine);
                else
                    LogBoxField.AppendText("Docker image found" + Environment.NewLine);

                UpdateSequences();
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        void OutputImageCheck(object sendingProcess, DataReceivedEventArgs outLine)
        {
            if (outLine.Data != null)
                ImageChecker.Add(outLine.Data);
        }

        void ErrorImageCheck(object sendingProcess, DataReceivedEventArgs outLine)
        {
            LogBoxField.AppendText(outLine.Data+Environment.NewLine);
        }

        private void UpdateSequences()
        {
            try
            {
                if (DCMPath.Text.Length > 0)
                {
                    SeqSelector.Items.Clear();
                    List<string> filePaths = Directory.GetFiles(DCMPath.Text, "*", SearchOption.TopDirectoryOnly).ToList();
                    List<string> seq = new List<string>();
                    foreach (string DCMPath in filePaths)
                    {
                        bool isDicom = DicomFile.HasValidHeader(DCMPath);
                        if (isDicom == true)
                        {
                            DICOMObject DCM = DICOMObject.Read(DCMPath);
                            string Sequence = DCM.FindFirst(TagHelper.SeriesDescription).DData.ToString();
                            seq.Add(Sequence);
                        }
                    }
                    SeqSelector.Items.AddRange(seq.Distinct().ToArray());
                    if (SeqSelector.Items.Count > 0) { SeqSelector.SelectedIndex = 0; }
                }
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        private void SeqSelector_SelectedIndexChanged(object sender, EventArgs e)
        {
            UpdateResultList();
        }

        private void StartButton_Click(object sender, EventArgs e)
        {
            try
            {
                LogBoxField.AppendText("Starting Analysis" + Environment.NewLine);
                if (RunAllCheck.Checked == true)
                {
                    Arguments = "-RunAll";
                }
                else
                {
                    if (RunUniformity.Checked == true) { Arguments += "-RunUniformity "; }
                    if (RunSlicePosition.Checked == true) { Arguments += "-RunSlicePos "; }
                    if (RunGhosting.Checked == true) { Arguments += "-RunGhosting "; }
                    if (RunGeometricAccuracy.Checked == true) { Arguments += "-RunGeoAcc "; }
                    if (RunSNRCheck.Checked == true) { Arguments += "-RunSNR "; }
                    if (RunSliceThickness.Checked == true) { Arguments += "-RunSliceThickness "; }
                    if (RunSpatialRes.Checked == true) { Arguments += "-RunSpatialRes "; }
                }
                ResultComboBox.Enabled = false;
                ResultComboBox.Items.Clear();
                ViewResult.Enabled = false;
                Results.Clear();
                StartButton.Enabled = false;
                SeqSelector.Enabled = false;
                SeqSelector.Enabled = false;
                DCMPath.Enabled = false;
                OutputPath.Enabled = false;
                Worker.RunWorkerAsync();
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        private void RunProcess(ProcessStartInfo processInfo, DataReceivedEventHandler Output, DataReceivedEventHandler ErrorOut)
        {
            processInfo.CreateNoWindow = true;
            processInfo.UseShellExecute = false;
            processInfo.RedirectStandardOutput = true;
            processInfo.RedirectStandardError = true;
            int exitCode;
            using (var process = new Process())
            {
                process.StartInfo = processInfo;
                //process.OutputDataReceived += new DataReceivedEventHandler(OutputHandler);
                process.OutputDataReceived += Output;
                process.ErrorDataReceived += ErrorOut;

                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();
                process.WaitForExit(1200000);
                if (!process.HasExited)
                {
                    process.Kill();
                }

                exitCode = process.ExitCode;
                process.Close();
            }
        }

        private void Worker_DoWork(object sender, System.ComponentModel.DoWorkEventArgs e)
        {
            try
            {
                //Run the docker image
                string DCMFolder = null;
                DCMPath.Invoke(new MethodInvoker(delegate { DCMFolder = DCMPath.Text; }));
                string OutputFolder = null;
                OutputPath.Invoke(new MethodInvoker(delegate { OutputFolder = OutputPath.Text; }));
                string Sequence = null;
                SeqSelector.Invoke(new MethodInvoker(delegate { Sequence = SeqSelector.Text; }));

                var processInfo = new ProcessStartInfo("docker", $"run --pull=never -v " + DCMFolder + ":/app/DataTransfer -v" + OutputFolder + ":/app/OutputFolder -v C:/Users/John/Desktop/DockerLocalTest/ToleranceTable:/app/ToleranceTable doctorspacemanphd/dockeracrphantom -seq \"" + Sequence + "\" " + Arguments);
                RunProcess(processInfo, new DataReceivedEventHandler(OutputHandler), new DataReceivedEventHandler(OutputErrorHandler));

                //Prune the container we just made
                processInfo = new ProcessStartInfo("docker", $"container prune -f");
                RunProcess(processInfo, new DataReceivedEventHandler(OutputHandler), new DataReceivedEventHandler(OutputErrorHandler));

            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }
        
        void OutputErrorHandler(object sendingProcess, DataReceivedEventArgs outLine)
        {
            try
            {
                LogBoxField.Invoke(new MethodInvoker(delegate { LogBoxField.Text += outLine.Data + Environment.NewLine; ; LogBoxField.SelectionStart = LogBoxField.Text.Length; LogBoxField.ScrollToCaret(); }));
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }


        void OutputHandler(object sendingProcess, DataReceivedEventArgs outLine)
        {
            try
            {
                bool OutputAll = false;
                string Line = "";
                LogBoxField.Invoke(new MethodInvoker(delegate { OutputAll = ShowAllOutput.Checked; }));
                Line = outLine.Data + Environment.NewLine;

                if (OutputAll == true)
                {
                    LogBoxField.Invoke(new MethodInvoker(delegate { LogBoxField.Text += Line; LogBoxField.SelectionStart = LogBoxField.Text.Length; LogBoxField.ScrollToCaret(); }));
                }
                else
                {
                    //Report Progress
                    if (Line.Contains("Progress"))
                    {
                        LogBoxField.Invoke(new MethodInvoker(delegate { LogBoxField.AppendText("Tests Completed: " + Line.Split(' ')[1]); LogBoxField.SelectionStart = LogBoxField.Text.Length; LogBoxField.ScrollToCaret(); }));
                    }
                    else if (Line.Contains("Running"))
                    {
                        LogBoxField.Invoke(new MethodInvoker(delegate { LogBoxField.AppendText(Line); LogBoxField.SelectionStart = LogBoxField.Text.Length; LogBoxField.ScrollToCaret(); }));
                    }
                    else //Check for warnings/errros probably want to improve this at a later date.
                    {
                        if (Line.Split(' ').Length > 3)
                        {
                            string PossibleWarningOrError = Line.Split(' ')[2];

                            if (PossibleWarningOrError == "W" || PossibleWarningOrError == "E")
                            {
                                LogBoxField.Invoke(new MethodInvoker(delegate { LogBoxField.AppendText(Line); LogBoxField.SelectionStart = LogBoxField.Text.Length; LogBoxField.ScrollToCaret(); }));
                            }
                        }
                    }
                }
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        void OutputAllHandler(object sendingProcess, DataReceivedEventArgs outLine)
        {
            LogBoxField.Invoke(new MethodInvoker(delegate { LogBoxField.Text += outLine.Data+Environment.NewLine; LogBoxField.SelectionStart = LogBoxField.Text.Length; LogBoxField.ScrollToCaret(); }));
        }

        private void Worker_ProgressChanged(object sender, System.ComponentModel.ProgressChangedEventArgs e)
        {
            try
            {
                //will leave this here incase somepoint i want a progress bar or something
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }
        private void Worker_RunWorkerCompleted(object sender, System.ComponentModel.RunWorkerCompletedEventArgs e)
        {
            try
            {
                //Fill out the results table
                DirectoryInfo dinfo = new DirectoryInfo(OutputPath.Text);
                FileInfo[] Files = dinfo.GetFiles("*.txt");
                List<FileInfo> FilteredFiles = new List<FileInfo>();
                foreach (FileInfo file in Files)
                {
                    if (file.Name.Contains(SeqSelector.Text))
                    {
                        FilteredFiles.Add(file);
                    }
                }
                var directory = new DirectoryInfo(OutputPath.Text);
                var MostRecentFile = (from f in FilteredFiles orderby f.LastWriteTime descending select f).First();
                List<string> lines = System.IO.File.ReadAllLines(MostRecentFile.FullName).ToList();

                foreach (string line in lines)
                {
                    Results.AppendText(line + Environment.NewLine);
                }
                HighlightText(Results, "Pass", Color.Green);
                HighlightText(Results, "Fail", Color.Red);
                HighlightText(Results, "No Tolerance Set", Color.Orange);
                HighlightText(Results, "Not Run", Color.Blue);


                LogBoxField.Text += "Finished" + Environment.NewLine;
                StartButton.Enabled = true;
                SeqSelector.Enabled = true;
                LogBoxField.SelectionStart = LogBoxField.Text.Length;
                LogBoxField.ScrollToCaret();

                Arguments = "";

                ResultComboBox.Enabled = true;
                ViewResult.Enabled = true;
                SeqSelector.Enabled = true;
                DCMPath.Enabled = true;
                OutputPath.Enabled = true;

                UpdateResultList();
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        private void UpdateResultList()
        {

            FileDict = new Dictionary<string, List<FileInfo>>();

            List<string> PathsExtension = new List<string>();
            List<string> Keys = new List<string>();


            PathsExtension.Add("ACRGeometricAccuracy");
            Keys.Add("Geometric Acccuracy");

            PathsExtension.Add("ACRGhosting");
            Keys.Add("Ghosting");

            PathsExtension.Add("ACRSlicePosition");
            Keys.Add("Slice Position");

            PathsExtension.Add("ACRSliceThickness");
            Keys.Add("Slice Thickness");

            PathsExtension.Add("ACRSNR");
            Keys.Add("SNR");

            PathsExtension.Add("ACRSpatialResolution");
            Keys.Add("Spatial Resolution");

            PathsExtension.Add("ACRUniformity");
            Keys.Add("Uniformity");

            ResultComboBox.Items.Clear();

            for (int i = 0; i < Keys.Count; i++)
            {
                ResultComboBox.Items.Add(Keys[i]);
                FileDict.Add(Keys[i], new List<FileInfo>());
                string[] paths = { OutputPath.Text, PathsExtension[i] };
                string fullpath = Path.Combine(paths);
                if (Directory.Exists(fullpath))
                {
                    DirectoryInfo info = new DirectoryInfo(fullpath);
                    FileInfo[] Files = info.GetFiles("*.png");
                    foreach (FileInfo file in Files)
                    {
                        string underlinedSeq = SeqSelector.Text.Replace(' ', '_');

                        if (file.Name.StartsWith(underlinedSeq) == true)
                        {
                            FileDict[Keys[i]].Add(file);
                        }
                    }
                }
            }
            ResultComboBox.SelectedIndex = 0;
        }

        public static void HighlightText(RichTextBox myRtb, string word, Color color)
        {
            if (word == string.Empty)
                return;
            var reg = new Regex(@"\b" + word + @"(\b|s\b)", RegexOptions.IgnoreCase);

            foreach (Match match in reg.Matches(myRtb.Text))
            {
                myRtb.Select(match.Index, match.Length);
                myRtb.SelectionColor = color;
            }

            myRtb.SelectionLength = 0;
            myRtb.SelectionColor = Color.Black;
        }

        private void DCMPath_click(object sender, MouseEventArgs e)
        {
            try
            {
                using (var fbd = new FolderBrowserDialog())
                {
                    DialogResult result = fbd.ShowDialog();
                    if (result == DialogResult.OK)
                    {
                        UpdateSequences();
                        DCMPath.Text = fbd.SelectedPath;
                    }
                }
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        private void OutputPath_click(object sender, MouseEventArgs e)
        {
            try
            {
                using (var fbd = new FolderBrowserDialog())
                {
                    DialogResult result = fbd.ShowDialog();
                    if (result == DialogResult.OK)
                    {
                        OutputPath.Text = fbd.SelectedPath;
                    }
                }
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        private void RunAllCheck_CheckedChanged(object sender, EventArgs e)
        {
            try
            {
                if (RunAllCheck.Checked)
                {
                    RunUniformity.Enabled = false;
                    RunSlicePosition.Enabled = false;
                    RunGhosting.Enabled = false;
                    RunGeometricAccuracy.Enabled = false;
                    RunSNRCheck.Enabled = false;
                    RunSliceThickness.Enabled = false;
                    RunSpatialRes.Enabled = false;
                }
                else
                {
                    RunUniformity.Enabled = true;
                    RunSlicePosition.Enabled = true;
                    RunGhosting.Enabled = true;
                    RunGeometricAccuracy.Enabled = true;
                    RunSNRCheck.Enabled = true;
                    RunSliceThickness.Enabled = true;
                    RunSpatialRes.Enabled = true;
                }
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }

        }

        private void ViewResult_Click(object sender, EventArgs e)
        {try
            {
                List<FileInfo> Files = FileDict[ResultComboBox.Text];

                if(Files.Count == 0)
                    {
                        throw new Exception("No result image found for " + ResultComboBox.Text);
                    }

                foreach (FileInfo file in Files)
                {
                    System.Diagnostics.Process.Start(file.FullName);
                }
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        private void Updater_DoWork(object sender, System.ComponentModel.DoWorkEventArgs e)
        {
            var processInfo = new ProcessStartInfo("docker", "pull doctorspacemanphd/dockeracrphantom:latest");
            RunProcess(processInfo, new DataReceivedEventHandler(OutputAllHandler), new DataReceivedEventHandler(OutputAllHandler));
        }

        private void Updater_RunWorkerCompleted(object sender, System.ComponentModel.RunWorkerCompletedEventArgs e)
        {
            StartButton.Enabled = true;
            UpdateDocker.Enabled = true;
            OfflineMode.Enabled = true;
            LogBoxField.AppendText(UpdaterString);
        }

        private void UpdateDocker_Click(object sender, EventArgs e)
        {
            StartButton.Enabled = false;
            UpdateDocker.Enabled = false;
            OfflineMode.Enabled = false ;
            Updater.RunWorkerAsync();
        }

        private void OfflineMode_CheckedChanged(object sender, EventArgs e)
        {
            if (OfflineMode.Checked == true) 
            {
                UpdateDocker.Enabled = false;
                OfflineMode.Enabled = false;
                StartButton.Enabled = false;
                LogBoxField.AppendText("Loading local docker image." +Environment.NewLine);
                LogBoxField.SelectionStart = LogBoxField.Text.Length; 
                LogBoxField.ScrollToCaret();
                Loader.RunWorkerAsync();
            }
            else
            {
                UpdateDocker.Enabled = true;
            }
        }

        private void Loader_DoWork(object sender, System.ComponentModel.DoWorkEventArgs e)
        {
            var processInfo = new ProcessStartInfo("docker", "load -i DockerImage/ACRPhantomImage.tar");
            RunProcess(processInfo, new DataReceivedEventHandler(OutputAllHandler), new DataReceivedEventHandler(OutputAllHandler));
        }

        private void Loader_RunWorkerCompleted(object sender, System.ComponentModel.RunWorkerCompletedEventArgs e)
        {
            OfflineMode.Enabled = true;
            StartButton.Enabled = true;
        }
    }
}

