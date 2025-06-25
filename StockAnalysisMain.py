from StockAnalysisFunction import show_BT, predict,predict2,predict_all,predict_all2,show_all
import streamlit as st

st.set_page_config(layout="wide")
sidebar_options = st.sidebar.selectbox(
    "Options",
    ["Main Menu", "View Present Stock Data", "Compare Stocks"]
)

if sidebar_options == "Main Menu":
    st.header("Explore Malaysia’s Stock Options in One Place")
    st.write("Stay informed, compare options, and make smarter investment decisions.")

    st.write("")
    st.subheader("What You Can Do Here")
    st.subheader("1. View the Latest Stock Options")
    st.write("Stay ahead of the curve with up-to-date listings from Bursa Malaysia. Easily browse current stock options with key metrics like volume, strike price, expiry date, and implied volatility.")

    st.subheader("2. Predict & Compare Upcoming Stock Options")
    st.write("Use data-driven insights to anticipate trends and opportunities. Compare future options side-by-side with built-in analytics—perfect for identifying promising contracts before they hit peak demand.")


elif sidebar_options == "Compare Stocks":
    col6, col7 = st.columns([0.8, 0.2])

    if "range" not in st.session_state:
        st.session_state.range = 0.000 

    with col7:
        num_input = st.text_input("Enter unit price", value=st.session_state.range)
    

    if num_input.isdigit():
        st.session_state.range = float(num_input)

    with col6:
        invest_amount = st.slider("Please select an amount range you want for invest.",min_value=0.000,max_value=80.000,step=0.001,key="range")

    col1, col2 = st.columns(2)
    with col1:
        options = st.selectbox(
            'Select first sector you interested',
            ('All','Business Trust', 'Closed-End Funds', 'Construction', 'Consumer Products & Services', 'Energy', 'Financial Services', 'Health Care', 'Industrial Products & Services', 'Plantation', 'Property', 'Real Estate Investment Trusts', 'SPAC', 'Technology', 'Telecommunications & Media', 'Transportation & Logistics', 'Utilities'),
            key="sector_1"
        )
        
        


        

    with col2:
        col2_options = st.selectbox(
            'Select second sector you interested',
            ('All','Business Trust', 'Closed-End Funds', 'Construction', 'Consumer Products & Services', 'Energy', 'Financial Services', 'Health Care', 'Industrial Products & Services', 'Plantation', 'Property', 'Real Estate Investment Trusts', 'SPAC', 'Technology', 'Telecommunications & Media', 'Transportation & Logistics', 'Utilities'),
            key="sector_2"


        )

    col_left, col_button, col_right = st.columns([1, 0.2, 1])
    with col_button:
        confirm = st.button("Confirm")
    
    if confirm:
        col4, col5 = st.columns(2)

        with col4:

            st.subheader('Sector: ' + options)

            if options == 'Business Trust':
                predict(options,invest_amount)
            elif options == 'Closed-End Funds':
                predict(options,invest_amount)
            elif options == 'Construction':
                predict(options,invest_amount)
            elif options == 'Consumer Products & Services':
                predict(options,invest_amount)
            elif options == 'Energy':
                predict(options,invest_amount)
            elif options == 'Financial Services':
                predict(options,invest_amount)
            elif options == 'Health Care':
                predict(options,invest_amount)
            elif options == 'Industrial Products & Services':
                predict(options,invest_amount)
            elif options == 'Plantation':
                predict(options,invest_amount)
            elif options == 'Property':
                predict(options,invest_amount)
            elif options == 'Real Estate Investment Trusts':
                predict(options,invest_amount)
            elif options == 'SPAC':
                predict(options,invest_amount)
            elif options == 'Technology':
                predict(options,invest_amount)
            elif options == 'Telecommunications & Media':
                predict(options,invest_amount)
            elif options == 'Transportation & Logistics':
                predict(options,invest_amount)
            elif options == 'Utilities':
                predict(options,invest_amount) 
            elif options == 'All':
                predict_all()

        with col5:
            
            st.subheader('Sector: ' + col2_options)

            if col2_options == 'Business Trust':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Closed-End Funds':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Construction':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Consumer Products & Services':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Energy':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Financial Services':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Health Care':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Industrial Products & Services':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Plantation':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Property':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Real Estate Investment Trusts':
                predict2(col2_options,invest_amount)
            elif col2_options == 'SPAC':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Technology':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Telecommunications & Media':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Transportation & Logistics':
                predict2(col2_options,invest_amount)
            elif col2_options == 'Utilities':
                predict2(col2_options,invest_amount)
            elif col2_options == 'All':
                predict_all()


elif sidebar_options == "View Present Stock Data":
    options = st.selectbox(
        'Select Your Sector Option',
        (
            'All','Business Trust', 'Closed-End Funds', 'Construction', 'Consumer Products & Services',
            'Energy', 'Financial Services', 'Health Care', 'Industrial Products & Services',
            'Plantation', 'Property', 'Real Estate Investment Trusts', 'SPAC',
            'Technology', 'Telecommunications & Media', 'Transportation & Logistics', 'Utilities'
        )
    )

    if options == 'Business Trust':
        show_BT(options)
    elif options == 'Closed-End Funds':
        show_BT(options)
    elif options == 'Construction':
        show_BT(options)
    elif options == 'Consumer Products & Services':
        show_BT(options)
    elif options == 'Energy':
        show_BT(options)
    elif options == 'Financial Services':
        show_BT(options)
    elif options == 'Health Care':
        show_BT(options)
    elif options == 'Industrial Products & Services':
        show_BT(options)
    elif options == 'Plantation':
        show_BT(options)
    elif options == 'Property':
        show_BT(options)
    elif options == 'Real Estate Investment Trusts':
        show_BT(options)
    elif options == 'SPAC':
        show_BT(options)
    elif options == 'Technology':
        show_BT(options)
    elif options == 'Telecommunications & Media':
        show_BT(options)
    elif options == 'Transportation & Logistics':
        show_BT(options)
    elif options == 'Utilities':
        show_BT(options)
    elif options =='All':
        show_all()

