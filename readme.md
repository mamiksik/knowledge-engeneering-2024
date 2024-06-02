# How to use
1. Create a virtual environment
2. Install the required packages `pip install -r requirements.txt`
3. Run the script `python main.py`

- This command will give you options to run different scripts (e.g. script for fetching stock information)
- To run the script for fetching stock information, run `python main.py stock-data-to-ttl`

# How to add new component
1. Create a new python file in the `lib` directory
2. Add all necessary functions in the file
3. Create one function that will be called from the main script (`import_sp_stock_data` in this case). The function most likely should accept some parameters like graph instance
4. Add new function to the main script (`main.py`) and call the function created in step 3, passing necessary parameters and possible saving the result to file. Make sure the function is decorated with `@cli_app.command()`
5. Use click to add optional parameters to the function

