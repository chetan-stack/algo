import xlwings as xw

# Open the workbook
wb = xw.Book("angel_excel.xlsx")

# Check if the sheet 'nifty' exists
try:
    st = wb.sheets['nifty']
except KeyError:
    print("Sheet 'nifty' does not exist in the workbook.")
    # Handle the error, such as by creating the sheet
    st = wb.sheets.add('nifty')

# Assign the value to cell A1
st.range('A1').value = ['storedata']
