import streamlit as st
import yfinance as yf
import pandas as pd
import time
from yff import get_stock_data,forecast,main_ticker,ace_tickers,etf_tickers,leap_tickers,main_ticker_compare,ace_tickers_compare,etf_tickers_compare,leap_tickers_compare,main_ticker_compare2,leap_tickers_compare2,ace_tickers_compare2,etf_tickers_compare2


st.set_page_config(page_title="Explore Malaysia’s Stock Options in One Place", layout="wide")
tickers = []

refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 10, 300, 60)

sidebar_options = st.sidebar.selectbox(
    "Options",
    ("Main Menu", "View Present Stock Data","Compare Stock Data", "Forecasting")
)

if sidebar_options == "Main Menu":
    st.title("Explore Malaysia’s Stock Options in One Place")
    st.markdown(
        """
        Welcome to your one-stop platform for navigating the Malaysian stock market.  
        Stay **informed**, **compare opportunities**, and make **smarter investment decisions** backed by real-time data and predictive insights.
        """
    )

elif sidebar_options == "Compare Stock Data":
    col6, col7 = st.columns([0.8, 0.2])

    if "max_range" not in st.session_state:
        st.session_state.max_range = 80.000

    if "min_range" not in st.session_state:
        st.session_state.min_range = 0.000

    with col7:
        num_input = st.text_input(
            "Enter max unit price", value=st.session_state.max_range
        )
        if num_input.replace('.', '', 1).isdigit():
            st.session_state.max_range = float(num_input)

    with col6:
        invest_amount = st.slider(
            "Please select an **amount range** you want to invest in (Open price).",
            min_value=0.000,
            max_value=80.000,
            value=st.session_state.max_range,
            step=0.001,
            key="max_range_slider"
        )

    col1, col2 = st.columns(2)
    with col1:
        col_market, col_sector = st.columns(2)
        with col_market:
            market_options = st.selectbox(
                'Market',
                ('Main Market','Ace Market','Leap Market',"ETF")
            )

        if market_options == 'Main Market':
            with col_sector:
                options = st.selectbox(
                            'Select the sector you interested',
                            ('Agricultural Products','Auto Parts','Automotive','Banking','Building Materials','Business Trust','Chemicals','Closed End Fund','Construction','Consumer Services','Digital Services','Diversified Industrials','Electricity','Energy, Infrastructure, Equipment & Services','Energy','Food & Beverages','Gas, Water & Multi-Utilities','Health Care Equipment & Services','Health Care Providers','Household Goods','Industrial Engineering','Industrial Materials, Components & Equipment','Industrial Services','Insurance','Media','Metals','Oil & Gas Producers','Other Energy Resources','Other Financials','Packaging Materials','Personal Goods','Pharmaceuticals','Plantation','Property','Real Estate Investment Trusts','Renewable Energy','Retailers','Semiconductors','Software','Special Purpose Acquisition Company','Technology Equipment','Telecommunications Equipment','Telecommunications Service Providers','Transportation & Logistics Services','Transportation Equipment','Travel, Leisure & Hospitality','Wood & Wood Products'),
                            key="sector_1"
                )
                


        if market_options == 'Ace Market':
            with col_sector:
                options = st.selectbox(
                            'Select the sector you interested',
                            ('Agricultural Products','Auto Parts','Building Materials','Chemicals','Construction','Consumer Services','Digital Services','Energy Infrastructure Equipment & Services','Food & Beverages','Gas, Water & Multi-Utilities','Health Care Equipment & Services','Health Care Providers','Household Goods','Industrial Engineering','Industrial Materials, Components & Equipment','Industrial Services','Media','Metals','Other Financials','Packaging Materials','Personal Goods','Plantation','Property','Renewable Energy','Retailers','Semiconductors','Software','Technology Equipment','Telecommunications Equipment','Telecom Service Providers','Transportation & Logistics','Travel, Leisure & Hospitality'),
                            key="sector_2"
                )
                

        elif market_options == "ETF":
            with col_sector:
                options = st.selectbox(
                    'Select the sector you are intrested',
                    ('Bond Fund','Commodity Fund',"Equity Fund"),
                    key="sector_3",

                )


        elif market_options == "Leap Market":
            with col_sector:
                options = st.selectbox(
                    'Select the sector you are interested',
                    (
                        'Agricultural Products','Building Materials','Construction','Consumer Services',
                        'Digital Services','Food & Beverages','Health Care Providers','Household Goods',
                        'Industrial Materials, Components & Equipment','Industrial Services','Metals',
                        'Other Financials','Packaging Materials','Personal Goods','Pharmaceuticals',
                        'Plantation','Semiconductors','Software'
                    ),
                    key="sector_4"
                )


    with col2:
        col_market2, col_sector2 = st.columns(2)
        with col_market2:
            market_options2 = st.selectbox(
                'Market',
                ('Main Market','Ace Market','Leap Market',"ETF"),key="market2"
            )

        if market_options2 == 'Main Market':
            with col_sector2:
                options2 = st.selectbox(
                            'Select the sector you interested',
                            ('Agricultural Products','Auto Parts','Automotive','Banking','Building Materials','Business Trust','Chemicals','Closed End Fund','Construction','Consumer Services','Digital Services','Diversified Industrials','Electricity','Energy, Infrastructure, Equipment & Services','Energy','Food & Beverages','Gas, Water & Multi-Utilities','Health Care Equipment & Services','Health Care Providers','Household Goods','Industrial Engineering','Industrial Materials, Components & Equipment','Industrial Services','Insurance','Media','Metals','Oil & Gas Producers','Other Energy Resources','Other Financials','Packaging Materials','Personal Goods','Pharmaceuticals','Plantation','Property','Real Estate Investment Trusts','Renewable Energy','Retailers','Semiconductors','Software','Special Purpose Acquisition Company','Technology Equipment','Telecommunications Equipment','Telecommunications Service Providers','Transportation & Logistics Services','Transportation Equipment','Travel, Leisure & Hospitality','Wood & Wood Products'),
                            key="sector_69"
                )
                        


        elif market_options2 == 'Ace Market':
            with col_sector:
                options2 = st.selectbox(
                            'Select the sector you interested',
                            ('Agricultural Products','Auto Parts','Building Materials','Chemicals','Construction','Consumer Services','Digital Services','Energy Infrastructure Equipment & Services','Food & Beverages','Gas, Water & Multi-Utilities','Health Care Equipment & Services','Health Care Providers','Household Goods','Industrial Engineering','Industrial Materials, Components & Equipment','Industrial Services','Media','Metals','Other Financials','Packaging Materials','Personal Goods','Plantation','Property','Renewable Energy','Retailers','Semiconductors','Software','Technology Equipment','Telecommunications Equipment','Telecom Service Providers','Transportation & Logistics','Travel, Leisure & Hospitality'),
                            key="sector_70"
                )
                

        elif market_options2 == "ETF":
            with col_sector:
                options2 = st.selectbox(
                    'Select the sector you are intrested',
                    ('Bond Fund','Commodity Fund',"Equity Fund"),
                    key="sector_71",

                )

        elif market_options2 == "Leap Market":
            with col_sector:
                options2 = st.selectbox(
                    'Select the sector you are interested',
                    (
                        'Agricultural Products','Building Materials','Construction','Consumer Services',
                        'Digital Services','Food & Beverages','Health Care Providers','Household Goods',
                        'Industrial Materials, Components & Equipment','Industrial Services','Metals',
                        'Other Financials','Packaging Materials','Personal Goods','Pharmaceuticals',
                        'Plantation','Semiconductors','Software'
                    ),
                    key="sector_72"
                )



        
    col_left, col_button, col_right = st.columns([1, 0.2, 1])
    with col_button:
        confirm = st.button("Confirm")       

    if confirm:
        col4, col5 = st.columns(2)

        with col4:
            if market_options == "Main Market":
                main_ticker_compare(invest_amount,options)
            elif market_options == "Ace Market":
                ace_tickers_compare(invest_amount,options)
            elif market_options == "ETF":
                etf_tickers_compare(invest_amount,options)
            elif market_options == "Leap Market":
                leap_tickers_compare(invest_amount,options)

        with col5:
            if market_options2 == "Main Market":
                main_ticker_compare2(invest_amount,options2)
            elif market_options2 == "Ace Market":
                ace_tickers_compare2(invest_amount,options2)
            elif market_options2 == "ETF":
                etf_tickers_compare2(invest_amount,options2)
            elif market_options2 == "Leap Market":
                leap_tickers_compare2(invest_amount,options2)
        

elif sidebar_options == "View Present Stock Data":

    
    col_market, col_sector = st.columns(2)
    with col_market:
        market_options = st.selectbox(
            'Market',
            ('Main Market','Ace Market','Leap Market',"ETF")
        )

    if market_options == 'Main Market':
        with col_sector:
                options = st.selectbox(
                        'Select the sector you interested',
                        ('Agricultural Products','Auto Parts','Automotive','Banking','Building Materials','Business Trust','Chemicals','Closed End Fund','Construction','Consumer Services','Digital Services','Diversified Industrials','Electricity','Energy, Infrastructure, Equipment & Services','Energy','Food & Beverages','Gas, Water & Multi-Utilities','Health Care Equipment & Services','Health Care Providers','Household Goods','Industrial Engineering','Industrial Materials, Components & Equipment','Industrial Services','Insurance','Media','Metals','Oil & Gas Producers','Other Energy Resources','Other Financials','Packaging Materials','Personal Goods','Pharmaceuticals','Plantation','Property','Real Estate Investment Trusts','Renewable Energy','Retailers','Semiconductors','Software','Special Purpose Acquisition Company','Technology Equipment','Telecommunications Equipment','Telecommunications Service Providers','Transportation & Logistics Services','Transportation Equipment','Travel, Leisure & Hospitality','Wood & Wood Products'),
                        key="sector_displaymain"
            )
                
        main_ticker(refresh_rate,options)

    elif market_options == 'Ace Market':
        with col_sector:
            options = st.selectbox(
                        'Select the sector you interested',
                        ('Agricultural Products','Auto Parts','Building Materials','Chemicals','Construction','Consumer Services','Digital Services','Energy Infrastructure Equipment & Services','Food & Beverages','Gas, Water & Multi-Utilities','Health Care Equipment & Services','Health Care Providers','Household Goods','Industrial Engineering','Industrial Materials, Components & Equipment','Industrial Services','Media','Metals','Other Financials','Packaging Materials','Personal Goods','Plantation','Property','Renewable Energy','Retailers','Semiconductors','Software','Technology Equipment','Telecommunications Equipment','Telecom Service Providers','Transportation & Logistics','Travel, Leisure & Hospitality'),
                        key="sector_displayace"
            )

        ace_tickers(refresh_rate,options)



    elif market_options == "ETF":
        with col_sector:
            options = st.selectbox(
                'Select the sector you are intrested',
                ('Bond Fund','Commodity Fund',"Equity Fund"),
                key="sector_displayetf",

            )

        etf_tickers(refresh_rate,options)

    elif market_options == "Leap Market":
        with col_sector:
            options = st.selectbox(
                'Select the sector you are interested',
                (
                    'Agricultural Products','Building Materials','Construction','Consumer Services',
                    'Digital Services','Food & Beverages','Health Care Providers','Household Goods',
                    'Industrial Materials, Components & Equipment','Industrial Services','Metals',
                    'Other Financials','Packaging Materials','Personal Goods','Pharmaceuticals',
                    'Plantation','Semiconductors','Software'
                ),
                key="sector_displayleap"
            )

        leap_tickers(refresh_rate,options)


elif sidebar_options == "Forecasting":
    forecast()

