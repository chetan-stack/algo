import json
import re

from flask import Flask, render_template, request
import datetime
import crete_update_table

app = Flask(__name__)

def sum_profit_or_loss(formatted_data, filter_date=None):
    total_profit_or_loss = 0.0
    order_count = 0
    stoplossorder=0
    for item in formatted_data:
        try:
            created_date = item.get('createddate')
            profit = item.get('profit', 'N/A')

            # Check if the created_date exists and matches the filter_date
            if created_date and created_date != 'None':
                item_date = created_date.split(" ")[0]  # Extract date part
                if filter_date is None or item_date == filter_date:
                    order_count += 1

                    # Validate and extract the profit/loss value
                    if isinstance(profit, str):
                        # Look for numeric profit values
                        match = re.search(r"[-+]?\d*\.\d+|\d+", profit)  # Match floats or integers
                        if match:
                            total_profit_or_loss += float(match.group())
                            floatvalue = float(match.group(1))

                        else:
                            print(f"Profit value not found for item: {item}")
                    elif isinstance(profit, (int, float)):
                        total_profit_or_loss += float(profit)
                        stoplossorder += 1 if profit < 0 else 0



                    else:
                        print(f"Unexpected profit format for item: {item}")

        except Exception as e:
            print(f"Error processing item {item.get('id', 'unknown')}: {e}")

    # Calculate brokerage
    brokerage = order_count * 50

    # Return calculated results
    return {
        "total_profit_or_loss": total_profit_or_loss,
        "order_count": order_count,
        "brokerage": brokerage,
        'stoplossorder':stoplossorder
    }
DATA_FILE = "auto_trade_crypto.json"  # File to store form data

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)  # Read existing data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty if file not found or corrupted

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        fetchdata = crete_update_table.fetchtcryptoorderbookweb()
        filter_date = request.args.get('date', datetime.date.today().strftime('%Y-%m-%d'))  # Default to today
        result = sum_profit_or_loss(fetchdata, filter_date)
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
                # 'store': form_data['store']

            }
            save_data(form_data)
    except Exception as e:
        return f"An error occurred: {e}"

    return render_template('index.html', fetchdata=fetchdata, filter_date=filter_date,form_data=form_data, **result)


if __name__ == '__main__':
    app.run(debug=True, port=4000)
