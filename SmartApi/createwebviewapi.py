import json
import re
import datetime
from flask import Flask, render_template,request
import crete_update_table
import store_auto_condition
import datetime
import re
from collections import defaultdict
app = Flask(__name__)
app.secret_key = "secret"  # Required for flash messages
DATA_FILE = "auto_trade.json"  # File to store form data


# Function to load stored data
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)  # Read existing data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty if file not found or corrupted


# Function to save data
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# def sum_profit_or_loss(formatted_data):
#     total_profit_or_loss = 0.0
#     for item in formatted_data:
#         try:
#             profit_or_loss = item.get('profit', 'N/A')
#             if profit_or_loss != 'N/A':
#                 total_profit_or_loss += float(profit_or_loss)
#         except ValueError:
#             print(f"Error converting profit_or_loss to float for item: {item}")
#     return total_profit_or_loss

def sum_profit_or_loss(formatted_data):
    total_profit_or_loss = 0.0
    today = datetime.date.today()
    pushdata = []
    order = 0
    stoplossorder = 0
    for item in formatted_data:
        try:
            created_date = item.get('createddate')

            # Check if created_date exists and is not None
            if created_date and created_date != 'None':
                # Parse the datetime string to a datetime object
                item_datetime = item['createddate'].split(" ")
                item_date = item_datetime[0]  # Extract just the date part

                # Compare item_date with today's date
                if item_date == str(today):
                    order += 1

                    profit_or_loss = item.get('profit', 'N/A')
                    if profit_or_loss != 'N/A':
                        pattern = r"Profit/Loss:\s*(-?\d+\.\d+)"
                        match = re.search(pattern, item['profit'])
                        profit_loss = pushdata.append(match.group(1))
                        floatvalue = float(match.group(1))
                        total_profit_or_loss += float(match.group(1))
                        stoplossorder += 1 if floatvalue < 0 else 0

        except (ValueError, TypeError) as e:
            print(f"Error processing item {item.get('id')}: {e}")
    brokage = order * 50
    return str(total_profit_or_loss) + " - no. of order: " + str(order) + " - brokreg: " + str(brokage) + "- stoploss: " + str(stoplossorder)



def month_order_data(formatted_data):
    today = datetime.date.today()
    formatted_data = crete_update_table.fetchsupportforweb()

    totalprofit = 0.0
    total_order = 0
    total_stoploss_order = 0
    daily_summary = defaultdict(lambda: {'orders': 0, 'stoplosses': 0, 'profit': 0.0})

    for item in formatted_data:
        try:
            created_date = item.get('createddate')
            if created_date and created_date != 'None':
                # Convert to datetime object
                item_datetime = datetime.datetime.strptime(created_date, "%Y-%m-%d %H:%M:%S.%f")

                if item_datetime.month == today.month and item_datetime.year == today.year:
                    day_key = item_datetime.date().isoformat()  # Format: 'YYYY-MM-DD'
                    total_order += 1
                    daily_summary[day_key]['orders'] += 1

                    profit_or_loss = item.get('profit', 'N/A')
                    if profit_or_loss != 'N/A':
                        pattern = r"Profit/Loss:\s*(-?\d+\.\d+)"
                        match = re.search(pattern, profit_or_loss)
                        if match:
                            floatvalue = float(match.group(1))
                            totalprofit += floatvalue
                            daily_summary[day_key]['profit'] += floatvalue
                            if floatvalue < 0:
                                total_stoploss_order += 1
                                daily_summary[day_key]['stoplosses'] += 1

        except (ValueError, TypeError):
            continue

    returndata = {
        'totalOrder': total_order,
        'stoplossOrder': total_stoploss_order,
        'totalProfit': round(totalprofit, 2),
        'dailyBreakdown': {
            date: {
                'orders': data['orders'],
                'stoplosses': data['stoplosses'],
                'profit': round(data['profit'], 2)
            }
            for date, data in sorted(daily_summary.items())
        }
    }
    print("---------------",returndata)
    return returndata

@app.route("/", methods=["GET", "POST"])  # Ensure POST is allowed

def home():
    try:
        form_data = load_data()  # Load stored data

        if request.method == "POST":
            form_data = {
                "auto_place_order": request.form.get("auto_place_order") == "on",  # Convert checkbox value to True/False
                "stop_loss": request.form.get("stop_loss"),
                "lotsize": request.form.get("lotsize"),
                "target_points": request.form.get("target_points"),
                "loss_points": request.form.get("loss_points"),
                "trade_range_min": request.form.get("trade_range_min"),
                "trade_range_max": request.form.get("trade_range_max"),
                "NIFTY": request.form.get("trade_nifty") == "on",
                "BANKNIFTY": request.form.get("trade_banknifty") == "on",
                "SENSEX": request.form.get("trade_SENSEX") == "on",
                "buy_or_sell": request.form.get("buy_or_sell"),  # Add this line
                'store': form_data['store']

            }
            save_data(form_data)  # Save to JSON file

        fetchdata = crete_update_table.fetchsupportforweb()
        date = datetime.date.today()
        # print(date)
        formatted_data = []
        for item in fetchdata:
            if item['createddate']:
                datetime_obj = item['createddate'].split(" ")
            if item['createddate'] and datetime_obj[0] == str(date):
                try:

                    profit_str = item.get('profit')
                    print(profit_str)
                        # Define the updated regex patt
                    # ern to extract data
                    # pattern = r'Time: (?P<date>.*?) - Symbol: (?P<symbol>.*?) - Exit Price: (?P<ltp>.*?) - Buy Price: (?P<buyprice>.*?) - Trailing Stoploss Price: (?P<trailing_stoploss_price>.*?) - Target Price: (?P<target_price>.*?) - Profit/Loss: (?P<profit_or_loss>.*?)$'
                    #
                    # match = re.match(pattern, profit_str)
                    # if match:
                    #     data = match.groupdict()
                    # else:
                    #     data = {
                    #         'date': 'N/A',
                    #         'symbol': 'N/A',
                    #         'lt                     p': 'N/A',
                    #         'buyprice': 'N/A',
                    #         'trailing_stoploss_price': 'N/A',
                    #         'target_price': 'N/A',
                    #         'profit_or_loss': 'N/A'
                    #     }

                    # Split the string into key-value pairs
                    pairs = re.split(r' - ', profit_str)
                    print('resplit',pair)
                    # Initialize an empty dictionary
                    result = {}

                    # Parse each pair
                    for pair in pairs:
                        key, value = pair.split(': ', 1)  # Split only on the first ': '

                        # Handle specific types
                        if "Time" in key:
                            result[key] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
                        elif "Symbol" in key:
                            result[key] = value
                        else:
                            result[key] = float(value)

                    # Print the result as a Python dictionary
                    print(result)
                    # Extract and process the 'profit' field safely
                    parts = item['profit'].split(' - ')

                    # Check if the parts list is not empty and get the last item
                    if parts:
                        # Get the last part and clean up the value
                        last_part = parts[-1].split(' ')[-1]  # Last item in the last part

                        # Extract values from the last part if needed
                        ltp = parts[0].split(' ')[1] if len(parts[0].split(' ')) > 1 else 'N/A'
                        buyPrice = parts[1].split(' ')[1] if len(parts[1].split(' ')) > 1 else 'N/A'
                        profitValue = last_part if last_part else 'N/A'
                    else:
                        ltp = buyPrice = profitValue = 'N/A'

                    formatted_item = {
                        'id': item.get('id'),
                        'script': item.get('script'),
                        'token': item.get('token'),
                        'lotsize': item.get('lotsize'),
                        'buyPrice': item.get('ltp'),
                        'nltp':result['Exit Price'],
                        'trailing_stoploss_price': result['Trailing Stoploss Price'],
                        'target_price': result['Target Price'],
                        'max_price_achieved': result['Target Price'],
                        'profit': result['Profit/Loss'],
                        'profittext': item.get('profit'),
                        'createddate': item.get('createddate')
                    }
                    formatted_data.append(formatted_item)
                except Exception as e:
                    print(e)
                    formatted_data.append({
                        'id': item.get('id'),
                        'script': item.get('script'),
                        'token': item.get('token'),
                        'lotsize': item.get('lotsize'),
                        'date': 'Error',
                        'symbol': 'Error',
                        'nltp':item.get('ltp'),
                        'ltp': item.get('ltp'),
                        'buyPrice': item.get('ltp'),
                        'trailing_stoploss_price': 'Error',
                        'target_price': 'Error',
                        'max_price_achieved': 'Error',
                        'profit': item.get('profit'),
                        'createddate': item.get('createddate')
                    })
                    print(f"Error processing item {item.get('id')}: {e}")

    except Exception as e:
        return f"An error occurred: {e}"
    print(formatted_data)
    allprofit = sum_profit_or_loss(formatted_data)
    monthwisedata = month_order_data(formatted_data)
    return render_template('index.html', fetchdata=formatted_data,allprofit=allprofit,form_data=form_data,monthwisedata=monthwisedata,store=form_data['store'] )


if __name__ == '__main__':
    app.run(debug=True, port=4000)
