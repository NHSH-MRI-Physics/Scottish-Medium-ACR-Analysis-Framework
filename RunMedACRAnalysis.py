#This file serves as both the entry point for Docker or when the user wishes to run it through python.
import argparse
import MedACRAnalysis

parser = argparse.ArgumentParser()
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')

required.add_argument('-seq', type=str, required=True, help='Sequence to be analysed within the DICOM')
optional.add_argument('-RunAll',action="store_true",default=False, help='Run all analysis tests')
optional.add_argument('-RunSNR',action="store_true",default=False, help='Run the signal to noise ratio test')
optional.add_argument('-RunGeoAcc',action="store_true",default=False, help='Run the geometric accuracy test')
optional.add_argument('-RunSpatialRes',action="store_true",default=False, help='Run the spatial resolution test')
optional.add_argument('-RunUniformity',action="store_true",default=False, help='Run the unifomrity test')
optional.add_argument('-RunGhosting',action="store_true",default=False, help='Run all ghosting test')
optional.add_argument('-RunSlicePos',action="store_true",default=False, help='Run the slice position test')
optional.add_argument('-RunSliceThickness',action="store_true",default=False, help='Run the slice thickness test')

optional.add_argument('-InputFolder',type=str,default="DataTransfer", help='Directory containing the DICOM images, expected format is one DICOM file per slice')
optional.add_argument('-ResultsFolder',type=str,default="OutputFolder", help='Directory where the results will be written to')
args = parser.parse_args()
Seq = args.seq

MedACRAnalysis.RunAnalysis(Seq,args.InputFolder,args.ResultsFolder,RunAll=args.RunAll, RunSNR=args.RunSNR, RunGeoAcc=args.RunGeoAcc, RunSpatialRes=args.RunSpatialRes, RunUniformity=args.RunUniformity, RunGhosting=args.RunGhosting, RunSlicePos=args.RunSlicePos, RunSliceThickness=args.RunSliceThickness)