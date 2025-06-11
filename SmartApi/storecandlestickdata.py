import io
import base64
import numpy as np
import pandas as pd
import mplfinance as mpf

def plot_to_base64(df, level):
    # Create a bytes buffer for the plot
    buffer = io.BytesIO()

    # Plotting the candlestick chart with horizontal lines
    mpf.plot(df, type='candle', hlines=level.to_list(), style='charles', title='Nifty Historical Candlestick Chart', ylabel='Price', savefig=buffer)

    # Seek to the beginning of the buffer
    buffer.seek(0)

    # Convert the buffer to a base64 string
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Close the buffer
    buffer.close()
    return img_base64
    # generate_html(img_base64)


chartbase64 = []

def createchart(script, timeframe, df, level):
    chart = plot_to_base64(df, level)

    resuilt = {
        'chartbase64': chart,
        'script': script,
        'timeframe': timeframe
    }

    # Update chartbase64 with the new result
    for i, item in enumerate(chartbase64):
        if item['script'] == script and item['timeframe'] == timeframe:
            chartbase64[i] = resuilt
            break
    else:
        # If no matching entry is found, add a new one
        chartbase64.append(resuilt)

    generate_html(chartbase64)


def generate_html(chartbase64):
    # Start the HTML document
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Candlestick Charts</title>
    </head>
    <body>
        <h1>Historical Candlestick Charts</h1>
            <div style="display: flex; flex-wrap: wrap;justify-content: flex-start; align-items: flex-start; margin-bottom: 20px;width:100%">

    """

    # Add each chart to the HTML
    for chart in chartbase64:
        html_content += f"""
        <div>
            <h2>{chart['script']} Candlestick Chart ({chart['timeframe']})</h2>
            <img src="data:image/png;base64,{chart['chartbase64']}" alt="{chart['script']} Candlestick Chart" style="display: block;">
        </div>
   
"""


    # End the HTML document
    html_content += """
     </div>
    </body>
    </html>
    """

    # Save the HTML content to a file
    with open('candlestick_charts.html', 'w') as f:
        f.write(html_content)

    print("HTML file has been generated successfully.")
# Example DataFrame (replace with your actual data)
data = {
    'Date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
    'Open': np.random.rand(100) * 100 + 10000,
    'High': np.random.rand(100) * 100 + 10000,
    'Low': np.random.rand(100) * 100 + 10000,
    'Close': np.random.rand(100) * 100 + 10000,
    'Volume': np.random.randint(1000, 5000, size=100)
}
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Example support/resistance levels (replace with your actual levels)
levels = pd.Series([10500, 11000, 11500])

# Generate base64 image string
img_base64 = plot_to_base64(df, levels)

# Generate the HTML file
# generate_html(img_base64)
