import * as XLSX from 'xlsx';
import * as path from 'path';

const excelPath = path.join(__dirname, '../../../149635_NB_raw_counts(24-360047-149635 VCC Day 2).xlsx');

export function analyzeExcelStructure() {
  try {
    // Read the Excel file
    const workbook = XLSX.readFile(excelPath);
    
    console.log('Excel File Analysis:');
    console.log('==================');
    console.log('Sheet Names:', workbook.SheetNames);
    
    // Analyze each sheet
    workbook.SheetNames.forEach(sheetName => {
      console.log(`\nAnalyzing sheet: ${sheetName}`);
      console.log('-------------------');
      
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as unknown[][];
      
      if (jsonData.length > 0) {
        console.log('Number of rows:', jsonData.length);
        console.log('Number of columns:', jsonData[0].length);
        
        // Show first few rows to understand structure
        console.log('\nFirst 5 rows:');
        jsonData.slice(0, 5).forEach((row, index) => {
          console.log(`Row ${index}:`, row);
        });
        
        // Try to identify headers
        if (jsonData.length > 0) {
          console.log('\nPossible headers:', jsonData[0]);
        }
      }
    });
    
    return workbook;
  } catch (error) {
    console.error('Error reading Excel file:', error);
    throw error;
  }
}

// Run the analysis if this file is executed directly
if (require.main === module) {
  analyzeExcelStructure();
}