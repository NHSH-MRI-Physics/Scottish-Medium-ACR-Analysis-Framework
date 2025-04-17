import pandas as pd
def DumpToExcel(ReportFile,Filename):
    # Split the report into lines
    lines = ReportFile.split("\n")
    
    # Prepare data for Excel
    data = []
    for line in lines:
        # Split each line into columns based on tab or whitespace
        columns = line.split("\t")
        data.append(columns)
    
    # Create a DataFrame
    df = pd.DataFrame(data)
    
    # Write to Excel
    output_file = Filename.split(".")[0] + ".xlsx"
    df.to_excel(output_file, index=False, header=False)
    print(f"Report has been written to {output_file}")