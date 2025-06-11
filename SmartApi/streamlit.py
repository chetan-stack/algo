import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import crete_update_table as table
# Set the title of the app
import base64

def show_dialog(id,script, token,exc, lotsize, ltp, close, target, stoploss, profit, createddate, button_text, key):
    print('opendqailog')
    with st.expander("Are You Sure ?", expanded=True):
        st.write(f"Place Order for symbol {script}")
        # Editable fields
        print('enter dailog')
        if st.button("Submit",key="submit_button_{key}"):
            print('delete')
            # table.inserttokenns(script, exc, token, lotsize, ltp, 0)
            # table.delete_place_order(id)
            # st.success("Value submitted!")
# Dummy function to simulate placing an order
def place_order(title):
    # Simulate order logic here
    return f"Order placed for {title}"
st.title('Trade Manager')

# Dummy function to simulate sending an alert
def send_alert(message):
    # In a real implementation, you might send an email, push notification, etc.
    st.info(f"Alert sent: {message}")

# Function to display the Base64 image
def show_image(base64_str):
    # Decode the Base64 string and create a Streamlit-compatible image
    image_data = base64.b64decode(base64_str)
    st.image(image_data, caption='Image from Base64', use_column_width=True)

# Sidebar for tab selection
st.sidebar.header('Navigation')
tab = st.sidebar.radio("Choose a Tab:", ["Options Order", "Order Book"])

# Tab 1: User Input and Data Generation
if tab == "Options Order":
    st.header("User Input and Data")

    # Input for text
    user_name = st.text_input('Enter your name:', 'Guest')

    # Input for slider to select a range
    selected_range = st.slider('Select a number range:', 0, 100, (25, 75))

    # Display the user name and range
    st.write(f'Hello, {user_name}!')
    st.write(f'You selected the range: {selected_range}')

    # Generate sample data based on user input


     # place  order table
    data = table.fetch_all_orders()
    # df = pd.DataFrame(data, columns=['id', 'script', 'token','lotsize', 'ltp','close','target','stoploss', 'profit','createddate'])
    # Function to create a card with a button
    def create_editable_card(id,script, token,exc, lotsize, ltp, close, target, stoploss, profit, createddate, button_text, key):
        # Creating a card-like container with editable fields
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:#f8f9fa; padding:15px; border-radius:10px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 10px;">
                    <h3>{script} (Token: {token}) {createddate}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Editable fields
            edited_ltp = st.number_input(f'LTP for {script}', value=ltp, key=f"ltp_{key}")
            edited_target = st.number_input(f'Target for {script}', value=target, key=f"target_{key}")
            edited_stoploss = st.number_input(f'Stop Loss for {script}', value=stoploss, key=f"stoploss_{key}")
            edited_lotsize = st.number_input(f'lot for {lotsize}', value=lotsize, key=f"lotsize_{key}")

            st.markdown(f"Lot Size: {lotsize} | Close: {close} | Profit: {profit} | Created Date: {createddate}")

            # Adding the button in the card
            if st.button(button_text, key=key):
                # Call the function to place an order with the edited values
                # order_message = place_order(script, edited_ltp, edited_target, edited_stoploss,edited_lotsize)
                show_dialog(id,script, token,exc, lotsize, ltp, close, target, stoploss, profit, createddate, button_text, key)
                # Send an alert after placing the order
                # st.success(f'Action triggered: {order_message}')
                # Here you can add code to send an alert
                # send_alert(order_message)    # Example usage

            # Button to open the image

    st.subheader('Order Prediction')
    for idx, row in enumerate(data):
        create_editable_card(
            id=row['id'],
            script=row['symbol'],
            token=row['token'],
            exc=row['exchange'],
            lotsize=row['lotsize'],
            ltp=row['ltp'],
            close=row['closeprice'],
            target=row['target'],
            stoploss=row['stoploss'],
            profit=row['profit'],
            createddate=row['createddate'],
            button_text="Place Order",
            key=f"card_{idx}"
        )




# Tab 2: Data Visualization
elif tab == "Order Book":
    st.header("Data Visualization")

    data = table.fetchsupportforweb()
    df = pd.DataFrame(data, columns=['id', 'script', 'token','lotsize', 'ltp', 'profit','createddate'])
    # Show the dataframe
    st.subheader('Order Book')
    st.write(df)


