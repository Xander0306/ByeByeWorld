import yfinance as yf
import pandas as pd
import streamlit as st
import numpy as np
import datetime
import plotly.graph_objs as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
import time



def get_stock_data(tickers):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        row = {
            "Ticker": ticker,
            "Name": info.get("shortName", ""),
            "Current Price": info.get("currentPrice", None),
            "Open": info.get("open", None),
            "High": info.get("dayHigh", None),
            "Low": info.get("dayLow", None),
            "Close": info.get("previousClose", None),
            "Volume": info.get("volume", None),
        }
        data.append(row)

    df = pd.DataFrame(data)

    if "Current Price" in df.columns and df["Current Price"].notna().any():
        df_sorted = df.sort_values(by="Current Price", ascending=False)
    else:
        print("Warning: 'Current Price' not found or is entirely missing. Returning unsorted data.")
        df_sorted = df

    return df_sorted


def forecast():
    st.set_page_config(layout="wide")
    st.title("OHLC Recursive Forecast")

    ticker = st.text_input("Enter Stock Ticker (e.g., 1155.KL):", "")

    if ticker:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=5 * 365)
        data = yf.download(ticker, start=start_date, end=end_date)

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if not data.empty:
            actual_ohlc = data[['Open', 'High', 'Low', 'Close']].copy()
            actual_ohlc = actual_ohlc.tail(365).reset_index()
            actual_ohlc['Type'] = 'Actual'
            actual_ohlc = actual_ohlc[['Date', 'Open', 'High', 'Low', 'Close', 'Type']]

            df = data.copy().reset_index()
            df['Date'] = pd.to_datetime(df['Date'])
            df = df[['Date', 'Open', 'High', 'Low', 'Close']].dropna()

            df['Open_Lag1'] = df['Open'].shift(1)
            df['High_Lag1'] = df['High'].shift(1)
            df['Low_Lag1'] = df['Low'].shift(1)
            df['Close_Lag1'] = df['Close'].shift(1)
            df = df.dropna()

            X = df[['Open_Lag1', 'High_Lag1', 'Low_Lag1', 'Close_Lag1']]
            y = df[['Open', 'High', 'Low', 'Close']]

            model = MultiOutputRegressor(RandomForestRegressor(n_estimators=200, random_state=42))
            model.fit(X, y)

            n_days = 30
            last_known = X.iloc[[-1]].values.flatten()
            forecast_list = []
            last_date = df['Date'].iloc[-1]

            for i in range(1, n_days + 1):
                next_day = model.predict(last_known.reshape(1, -1)).flatten()
                forecast_list.append(next_day)
                last_known = next_day

            forecast_df = pd.DataFrame(forecast_list, columns=['Open', 'High', 'Low', 'Close'])
            future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, n_days + 1)]
            forecast_df['Date'] = future_dates
            forecast_df['Type'] = 'Predicted'
            forecast_df = forecast_df[['Date', 'Open', 'High', 'Low', 'Close', 'Type']]

            combined_df = pd.concat([actual_ohlc, forecast_df]).reset_index(drop=True)

            st.subheader("1 Year Actual + 30 Days Predicted OHLC")
            st.dataframe(combined_df.style.format({
                "Open": "{:.2f}",
                "High": "{:.2f}",
                "Low": "{:.2f}",
                "Close": "{:.2f}"
            }))

            st.subheader("Candlestick Chart: Actual + Predicted")

            fig = go.Figure()

            fig.add_trace(go.Candlestick(
                x=combined_df[combined_df['Type'] == 'Actual']['Date'],
                open=combined_df[combined_df['Type'] == 'Actual']['Open'],
                high=combined_df[combined_df['Type'] == 'Actual']['High'],
                low=combined_df[combined_df['Type'] == 'Actual']['Low'],
                close=combined_df[combined_df['Type'] == 'Actual']['Close'],
                increasing_line_color='green',
                decreasing_line_color='red',
                name='Actual OHLC'
            ))

            fig.add_trace(go.Candlestick(
                x=combined_df[combined_df['Type'] == 'Predicted']['Date'],
                open=combined_df[combined_df['Type'] == 'Predicted']['Open'],
                high=combined_df[combined_df['Type'] == 'Predicted']['High'],
                low=combined_df[combined_df['Type'] == 'Predicted']['Low'],
                close=combined_df[combined_df['Type'] == 'Predicted']['Close'],
                increasing_line_color='lightgreen',
                decreasing_line_color='lightcoral',
                name='Predicted OHLC'
            ))

            fig.update_layout(
                title=f"{ticker} - 1 Year Actual + 30 Days Forecast",
                xaxis_title='Date',
                yaxis_title='Price',
                xaxis_rangeslider_visible=True,
                autosize=False,
                width=1200,
                height=800,
                margin=dict(l=50, r=50, t=50, b=50)
            )

            st.plotly_chart(fig)

        else:
            st.error("No data retrieved. Please check your stock ticker.")


def main_ticker(refresh_rate,options):

    if options == 'Agricultural Products':
        tickers = ['136.KL','5278.KL','5300.KL','6633.KL','7084.KL','7085.KL','7134.KL','7174.KL','7176.KL','7252.KL','7439.KL','9385.KL','9776.KL']
        get_stock_data(tickers)
    elif options == 'Auto Parts':
        tickers = ['5015.KL','5198.KL','5271.KL','5322.KL','7004.KL','7096.KL','7132.KL','7192.KL','7226.KL','7773.KL','7811.KL','9083.KL']
        get_stock_data(tickers)
    elif options == 'Automotive':
        tickers = ['1619.KL','3301.KL','4006.KL','4197.KL','4405.KL','5242.KL','5248.KL','5983.KL','7060.KL','7080.KL']
        get_stock_data(tickers)
    elif options == 'Banking':
        tickers = ['1015.KL','1023.KL','1066.KL','1082.KL','1155.KL','1295.KL','2488.KL','5185.KL','5258.KL','5819.KL','2488R1.KL']
        get_stock_data(tickers)
    elif options == 'Building Materials':
        tickers = ['2852.KL','3794.KL','5000.KL','5009.KL','5021.KL','5048.KL','5165.KL','5273.KL','5371.KL','6211.KL','7016.KL','7043.KL','7073.KL','7086.KL','7115.KL','7140.KL','7162.KL','7165.KL','7219.KL','7232.KL','7235.KL','7239.KL','7544.KL','7609.KL','8117.KL','8419.KL','8435.KL','9237.KL']
        get_stock_data(tickers)
    elif options == 'Business Trust':
        tickers = ['5320.KL']
        get_stock_data(tickers)
    elif options == 'Chemicals':
        tickers = ['54.KL','3298.KL','4758.KL','5134.KL','5143.KL','5147.KL','5151.KL','5183.KL','5284.KL','5289.KL','5330.KL','7173.KL','7222.KL','7498.KL','8443.KL','9954.KL']
        get_stock_data(tickers)
    elif options == 'Closed End Fund':
        tickers = ['5108.KL']
        get_stock_data(tickers)
    elif options == 'Construction':
        tickers = ['192.KL','198.KL','2283.KL','3204.KL','3336.KL','3565.KL','4723.KL','4847.KL','5006.KL','5042.KL','5054.KL','5070.KL','5085.KL','5129.KL','5169.KL','5171.KL','5190.KL','5205.KL','5226.KL','5253.KL','5263.KL','5281.KL','5293.KL','5297.KL','5310.KL','5329.KL','5398.KL','5622.KL','5703.KL','5932.KL','6807.KL','7028.KL','7047.KL','7070.KL','7071.KL','7078.KL','7145.KL','7161.KL','7195.KL','7240.KL','7528.KL','7595.KL','8192.KL','8311.KL','8591.KL','8834.KL','8877.KL','9261.KL','9571.KL','9598.KL','9628.KL','9679.KL','9717.KL']
        get_stock_data(tickers)
    elif options == 'Consumer Services':
        tickers = ['180.KL','5104.KL','5131.KL','5166.KL','5231.KL','5908.KL','7121.KL','7129.KL','7208.KL','7223.KL','7315.KL','7757.KL','9091.KL','9423.KL','9792.KL']
        get_stock_data(tickers)
    elif options == 'Digital Services':
        tickers = ['29.KL','126.KL','138.KL','200.KL','253.KL','4456.KL','5011.KL','5028.KL','5204.KL','5216.KL','5301.KL','5309.KL','8338.KL','9008.KL','9075.KL']
        get_stock_data(tickers)
    elif options == 'Diversified Industrials':
        tickers = ['3034.KL','3395.KL','3476.KL','5211.KL','5311.KL','5843.KL','6491.KL','7005.KL','8702.KL']
        get_stock_data(tickers)
    elif options == 'Electricity':
        tickers = ['3069.KL','5264.KL','5347.KL','7471.KL']
        get_stock_data(tickers)
    elif options == 'Energy, Infrastructure, Equipment & Services':
        tickers = ['91.KL','219.KL','5071.KL','5115.KL','5132.KL','5133.KL','5141.KL','5142.KL','5186.KL','5210.KL','5218.KL','5243.KL','5255.KL','5257.KL','5321.KL','7108.KL','7228.KL','7250.KL','7253.KL','7277.KL','7293.KL','8613.KL']
        get_stock_data(tickers)
    elif options == 'Energy':
        tickers = ['3042.KL','4324.KL','5199.KL']
        get_stock_data(tickers)
    elif options == 'Food & Beverages':
        tickers = ['12.KL','212.KL','2658.KL','2828.KL','2836.KL','3026.KL','3255.KL','3662.KL','3689.KL','4065.KL','4707.KL','5008.KL','5024.KL','5102.KL','5157.KL','5187.KL','5188.KL','5202.KL','5306.KL','5328.KL','5533.KL','6203.KL','6432.KL','7035.KL','7103.KL','7107.KL','7167.KL','7216.KL','7237.KL','7243.KL','8303.KL','8478.KL','9946.KL']
        get_stock_data(tickers)
    elif options == 'Gas, Water & Multi-Utilities':
        tickers = ['4677.KL','5041.KL','5209.KL','5272.KL','6033.KL','6742.KL','8524.KL','8567.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Equipment & Services':
        tickers = ['1.KL','163.KL','256.KL','5168.KL','7106.KL','7113.KL','7153.KL','7191.KL','7803.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Providers':
        tickers = ['101.KL','222.KL','5225.KL','5878.KL']
        get_stock_data(tickers)
    elif options == 'Household Goods':
        tickers = ['197.KL','229.KL','239.KL','2755.KL','3719.KL','5022.KL','5066.KL','5107.KL','5159.KL','5160.KL','5336.KL','6939.KL','7006.KL','7062.KL','7088.KL','7089.KL','7094.KL','7128.KL','7149.KL','7152.KL','7180.KL','7186.KL','7200.KL','7202.KL','7203.KL','7211.KL','7215.KL','7246.KL','7412.KL','7935.KL','7943.KL','8079.KL','8605.KL','9172.KL','9407.KL','9997.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Engineering':
        tickers = ['151.KL','185.KL','5163.KL','5219.KL','5568.KL','6998.KL','7033.KL','7170.KL','7212.KL','7229.KL','9466.KL','9741.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Materials, Components & Equipment':
        tickers = ['149.KL','161.KL','196.KL','225.KL','270.KL','2127.KL','3247.KL','5007.KL','5068.KL','5152.KL','5167.KL','5170.KL','5192.KL','5208.KL','5220.KL','5276.KL','5277.KL','5291.KL','5302.KL','5317.KL','5327.KL','6637.KL','6963.KL','6971.KL','7050.KL','7076.KL','7091.KL','7095.KL','7100.KL','7133.KL','7137.KL','7146.KL','7155.KL','7197.KL','7207.KL','7227.KL','7231.KL','7233.KL','7986.KL','8176.KL','8648.KL','8907.KL','9318.KL','9601.KL','9822.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Services':
        tickers = ['39.KL','43.KL','58.KL','64.KL','99.KL','257.KL','268.KL','1368.KL','3107.KL','5035.KL','5037.KL','5308.KL','5673.KL','6874.KL','7018.KL','7036.KL','7083.KL','7163.KL','7201.KL','7241.KL','7374.KL','7579.KL','8044.KL','8486.KL']
        get_stock_data(tickers)
    elif options == 'Insurance':
        tickers = ['1058.KL','1163.KL','1198.KL','5230.KL','6009.KL','6139.KL','6459.KL','8621.KL','1163PA.KL']
        get_stock_data(tickers)
    elif options == 'Media':
        tickers = ['159.KL','4502.KL','5090.KL','5252.KL','6084.KL','6399.KL','9431.KL']
        get_stock_data(tickers)
    elif options == 'Metals':
        tickers = ['207.KL','2674.KL','2984.KL','3778.KL','4235.KL','5010.KL','5056.KL','5072.KL','5087.KL','5094.KL','5098.KL','5125.KL','5178.KL','5232.KL','5298.KL','5331.KL','5436.KL','5665.KL','5797.KL','5916.KL','6149.KL','6556.KL','7014.KL','7020.KL','7097.KL','7099.KL','7172.KL','7199.KL','7214.KL','7217.KL','7221.KL','7225.KL','7245.KL','7692.KL','8869.KL','9199.KL','9326.KL','9873.KL','9881.KL']
        get_stock_data(tickers)
    elif options == 'Oil & Gas Producers':
        tickers = ['3042.KL','4324.KL','5199.KL']
        get_stock_data(tickers)
    elif options == 'Other Energy Resources':
        tickers = ['2739.KL','7164.KL']
        get_stock_data(tickers)
    elif options == 'Other Financials':
        tickers = ['242.KL','1171.KL','1818.KL','2143.KL','2186.KL','3379.KL','3441.KL','5088.KL','5139.KL','5228.KL','5274.KL','5325.KL','6483.KL','7082.KL','9296.KL']
        get_stock_data(tickers)
    elif options == 'Packaging Materials':
        tickers = ['269.KL','3883.KL','4731.KL','5065.KL','5100.KL','5105.KL','6297.KL','7017.KL','7029.KL','7034.KL','7114.KL','7157.KL','7247.KL','7248.KL','7285.KL','8052.KL','8125.KL','8273.KL','8362.KL','9148.KL','9938.KL']
        get_stock_data(tickers)
    elif options == 'Personal Goods':
        tickers = ['49.KL','157.KL','183.KL','250.KL','3514.KL','4162.KL','5081.KL','5156.KL','5172.KL','5247.KL','5295.KL','6068.KL','7087.KL','7139.KL','7154.KL','7168.KL','7184.KL','7209.KL','7234.KL','7722.KL','8532.KL','8966.KL','9288.KL','9369.KL']
        get_stock_data(tickers)
    elif options == 'Pharmaceuticals':
        tickers = ['2.KL','201.KL','7081.KL','7090.KL','7148.KL','7178.KL']
        get_stock_data(tickers)
    elif options == 'Plantation':
        tickers = ['1899.KL','1902.KL','1929.KL','1961.KL','1996.KL','2038.KL','2054.KL','2089.KL','2135.KL','2291.KL','2445.KL','2453.KL','2542.KL','2569.KL','2593.KL','2607.KL','3948.KL','4316.KL','4383.KL','4936.KL','5012.KL','5026.KL','5027.KL','5029.KL','5047.KL','5069.KL','5112.KL','5113.KL','5126.KL','5135.KL','5138.KL','5222.KL','5223.KL','5285.KL','5319.KL','5323.KL','6262.KL','7054.KL','7382.KL','7501.KL','8982.KL','9059.KL','9695.KL']
        get_stock_data(tickers)
    elif options == 'Property':
        tickers = ['56.KL','230.KL','1147.KL','1503.KL','1538.KL','1589.KL','1651.KL','1694.KL','1724.KL','2224.KL','2259.KL','2305.KL','2429.KL','2682.KL','3158.KL','3174.KL','3239.KL','3417.KL','3557.KL','3573.KL','3611.KL','3743.KL','3913.KL','4022.KL','4057.KL','4251.KL','4286.KL','4375.KL','4464.KL','4596.KL','5020.KL','5038.KL','5040.KL','5049.KL','5053.KL','5062.KL','5073.KL','5075.KL','5084.KL','5148.KL','5175.KL','5182.KL','5191.KL','5200.KL','5207.KL','5213.KL','5236.KL','5239.KL','5249.KL','5283.KL','5288.KL','5313.KL','5315.KL','5401.KL','5606.KL','5738.KL','5789.KL','5827.KL','6017.KL','6041.KL','6076.KL','6114.KL','6173.KL','6181.KL','6378.KL','6602.KL','6718.KL','6769.KL','6815.KL','6912.KL','7003.KL','7007.KL','7010.KL','7055.KL','7066.KL','7077.KL','7079.KL','7105.KL','7120.KL','7131.KL','7179.KL','7198.KL','7249.KL','7323.KL','7617.KL','7765.KL','7889.KL','8141.KL','8206.KL','8494.KL','8583.KL','8664.KL','8893.KL','8923.KL','9539.KL','9687.KL','9814.KL','9962.KL']
        get_stock_data(tickers)
    elif options == 'Real Estate Investment Trusts':
        tickers = ['5106.KL','5109.KL','5110.KL','5111.KL','5116.KL','5120.KL','5121.KL','5123.KL','5127.KL','5130.KL','5176.KL','5180.KL','5212.KL','5227.KL','5269.KL','5280.KL','5299.KL','5307.KL','5338.KL','5235SS.KL']
        get_stock_data(tickers)
    elif options == 'Renewable Energy':
        tickers = ['118.KL','168.KL','193.KL','215.KL','223.KL','5184.KL','5614.KL','7130.KL']
        get_stock_data(tickers)
    elif options == 'Retailers':
        tickers = ['4995.KL','5080.KL','5250.KL','5275.KL','5296.KL','5305.KL','5316.KL','5318.KL','5326.KL','5337.KL','5657.KL','5681.KL','6351.KL','6599.KL','7048.KL','7052.KL','7230.KL','7668.KL','8672.KL']
        get_stock_data(tickers)
    elif options == 'Semiconductors':
        tickers = ['97.KL','127.KL','128.KL','143.KL','166.KL','3867.KL','4359.KL','5005.KL','5292.KL','7022.KL','7204.KL','9334.KL']
        get_stock_data(tickers)
    elif options == 'Software':
        tickers = ['8.KL','40.KL','41.KL','51.KL','65.KL','5195.KL','7181.KL']
        get_stock_data(tickers)
    elif options == 'Special Purpose Acquisition Company':
        tickers = ['5270.KL']
        get_stock_data(tickers)
    elif options == 'Technology Equipment':
        tickers = ['83.KL','90.KL','104.KL','113.KL','146.KL','208.KL','246.KL','259.KL','5036.KL','5161.KL','5162.KL','5286.KL','7160.KL','9377.KL','9393.KL']
        get_stock_data(tickers)
    elif options == 'Telecommunications Equipment':
        tickers = ['7031.KL']
        get_stock_data(tickers)
    elif options == 'Telecommunications Service Providers':
        tickers = ['32.KL','59.KL','82.KL','172.KL','4863.KL','5031.KL','5332.KL','6012.KL','6888.KL','6947.KL']
        get_stock_data(tickers)
    elif options == 'Transportation & Logistics Services':
        tickers = ['78.KL','2062.KL','3816.KL','4634.KL','5032.KL','5077.KL','5078.KL','5136.KL','5140.KL','5173.KL','5246.KL','5259.KL','5267.KL','5303.KL','6254.KL','6521.KL','7013.KL','7053.KL','7117.KL','7210.KL','7218.KL','7676.KL','8346.KL','8397.KL']
        get_stock_data(tickers)
    elif options == 'Transportation Equipment':
        tickers = ['5145.KL','5149.KL','7187.KL','8133.KL']
        get_stock_data(tickers)
    elif options == 'Travel, Leisure & Hospitality':
        tickers = ['37.KL','186.KL','1287.KL','1481.KL','1562.KL','1643.KL','2097.KL','3018.KL','3182.KL','3859.KL','3891.KL','3905.KL','4081.KL','4219.KL','4715.KL','5016.KL','5079.KL','5099.KL','5196.KL','5238.KL','5260.KL','5265.KL','5335.KL','5517.KL','5592.KL','8885.KL','9113.KL']
        get_stock_data(tickers)
    elif options == 'Wood & Wood Products':
        tickers = ['4243.KL','5001.KL','5025.KL','5082.KL','5095.KL','5101.KL','5197.KL','5576.KL','5649.KL','6904.KL','7025.KL','7123.KL','7169.KL','7188.KL','7854.KL','8745.KL','9016.KL','9121.KL']
        get_stock_data(tickers)


    placeholder = st.empty()

    while True:
        with placeholder.container():
            df = get_stock_data(tickers)
            st.dataframe(df.sort_values(by="Current Price", ascending=False), use_container_width=True)
        time.sleep(refresh_rate)


def ace_tickers(refresh_rate,options):
    if options == 'Agricultural Products':
        tickers = ['0148.KL','0171.KL','0300.KL']
        get_stock_data(tickers)
    elif options == 'Auto Parts':
        tickers = ['0190.KL','0263.KL','0322.KL','0350.KL']
        get_stock_data(tickers)
    elif options == 'Building Materials':
        tickers = ['0227.KL','0247.KL','0302.KL','0306.KL']
        get_stock_data(tickers)
    elif options == 'Chemicals':
        tickers = ['0038.KL','0055.KL','0105.KL','0301.KL','0331.KL','0349.KL']
        get_stock_data(tickers)
    elif options == 'Construction':
        tickers = ['0045.KL','0109.KL','0162.KL','0206.KL','0221.KL','0226.KL','0235.KL','0237.KL','0241.KL','0245.KL',
                '0273.KL','0292.KL','0310.KL','0345.KL','0347.KL','0351.KL','0359.KL','0360.KL']
        get_stock_data(tickers)
    elif options == 'Consumer Services':
        tickers = ['0140.KL','0158.KL','0178.KL','0280.KL','0281.KL','0304.KL','0330.KL','0342.KL','0356.KL']
        get_stock_data(tickers)
    elif options == 'Digital Services':
        tickers = ['0006.KL','0093.KL','0117.KL','0131.KL','0145.KL','0154.KL','0176.KL','0202.KL','0249.KL','0277.KL','0319.KL']
        get_stock_data(tickers)
    elif options == 'Energy Infrastructure Equipment & Services':
        tickers = ['0220.KL','0320.KL']
        get_stock_data(tickers)
    elif options == 'Food & Beverages':
        tickers = ['0074.KL','0095.KL','0179.KL','0252.KL','0260.KL','0271.KL','0309.KL','0312.KL','0316.KL','0327.KL','0338.KL']
        get_stock_data(tickers)
    elif options == 'Gas, Water & Multi-Utilities':
        tickers = ['0011.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Equipment & Services':
        tickers = ['0155.KL','0182.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Providers':
        tickers = ['0075.KL','0243.KL','0283.KL','0303.KL','0329.KL','0332.KL']
        get_stock_data(tickers)
    elif options == 'Household Goods':
        tickers = ['0170.KL','0205.KL','0216.KL','0279.KL','0326.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Engineering':
        tickers = ['0177.KL','0240.KL','0255.KL','0361.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Materials, Components & Equipment':
        tickers = ['0025.KL','0028.KL','0072.KL','0084.KL','0100.KL','0102.KL','0133.KL','0175.KL','0188.KL','0217.KL','0238.KL',
                '0248.KL','0288.KL','0295.KL','0298.KL','0307.KL','0325.KL','0337.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Services':
        tickers = ['0024.KL','0081.KL','0089.KL','0122.KL','0160.KL','0167.KL','0187.KL','0213.KL','0218.KL','0231.KL','0232.KL',
                '0261.KL','0284.KL','0289.KL','0291.KL','0293.KL','0296.KL','0317.KL','0321.KL','0323.KL','0339.KL',
                '0346.KL','0348.KL','0352.KL','0353.KL','0355.KL']
        get_stock_data(tickers)
    elif options == 'Media':
        tickers = ['0007.KL','0147.KL','0173.KL','0315.KL']
        get_stock_data(tickers)
    elif options == 'Metals':
        tickers = ['0098.KL','0211.KL','0266.KL','0297.KL','0313.KL','0336.KL','0341.KL']
        get_stock_data(tickers)
    elif options == 'Other Financials':
        tickers = ['0053.KL','0150.KL','0285.KL','0286.KL']
        get_stock_data(tickers)
    elif options == 'Packaging Materials':
        tickers = ['0228.KL']
        get_stock_data(tickers)
    elif options == 'Personal Goods':
        tickers = ['0333.KL','0335.KL']
        get_stock_data(tickers)
    elif options == 'Plantation':
        tickers = ['0189.KL']
        get_stock_data(tickers)
    elif options == 'Property':
        tickers = ['0308.KL']
        get_stock_data(tickers)
    elif options == 'Renewable Energy':
        tickers = ['0233.KL','0262.KL','0318.KL','0340.KL']
        get_stock_data(tickers)
    elif options == 'Retailers':
        tickers = ['0210.KL','0287.KL','0357.KL']
        get_stock_data(tickers)
    elif options == 'Semiconductors':
        tickers = ['0070.KL','0120.KL','0251.KL','0272.KL','0275.KL','0328.KL']
        get_stock_data(tickers)
    elif options == 'Software':
        tickers = ['0010.KL','0018.KL','0020.KL','0023.KL','0026.KL','0050.KL','0066.KL','0068.KL','0069.KL','0079.KL','0086.KL','0094.KL',
                '0106.KL','0107.KL','0108.KL','0119.KL','0132.KL','0152.KL','0156.KL','0174.KL','0203.KL','0236.KL','0258.KL',
                '0276.KL','0290.KL','0311.KL','0343.KL']
        get_stock_data(tickers)
    elif options == 'Technology Equipment':
        tickers = ['0005.KL','0036.KL','0060.KL','0085.KL','0111.KL','0112.KL','0169.KL','0181.KL','0191.KL','0209.KL','0265.KL',
                '0267.KL','0278.KL','0358.KL']
        get_stock_data(tickers)
    elif options == 'Telecommunications Equipment':
        tickers = ['0017.KL','0035.KL','0096.KL','0103.KL','0123.KL','0129.KL']
        get_stock_data(tickers)
    elif options == 'Telecom Service Providers':
        tickers = ['0092.KL','0165.KL','0195.KL']
        get_stock_data(tickers)
    elif options == 'Transportation & Logistics':
        tickers = ['0034.KL','0048.KL','0080.KL','0199.KL','0282.KL','0299.KL','0305.KL']
        get_stock_data(tickers)
    elif options == 'Travel, Leisure & Hospitality':
        tickers = ['0022.KL','0116.KL','0153.KL']
        get_stock_data(tickers)
   

    placeholder = st.empty()

    while True:
        with placeholder.container():
            df = get_stock_data(tickers)
            st.dataframe(df.sort_values(by="Current Price", ascending=False), use_container_width=True)
        time.sleep(refresh_rate)

def etf_tickers(refresh_rate,options):

    if options == 'Bond Fund':
        tickers = ['0800EA.KL']
        get_stock_data(tickers)
    elif options == 'Commodity Fund':
        tickers = ['0828EA.KL']
        get_stock_data(tickers)
    elif options == 'Equity Fund':
        tickers = ['0820EA.KL','0821EA.KL','0822EA.KL','0823EA.KL','0824EA.KL','0825EA.KL','0827EA.KL','0829EA.KL','0829EB.KL','0838EA.KL','0839EA.KL']
        get_stock_data(tickers)


    placeholder = st.empty()

    while True:
        with placeholder.container():
            df = get_stock_data(tickers)
            st.dataframe(df.sort_values(by="Current Price", ascending=False), use_container_width=True)
        time.sleep(refresh_rate)


def leap_tickers(refresh_rate,options):

    if options == 'Agricultural Products':
        tickers = ['03051.KL']
        get_stock_data(tickers)
    elif options == 'Building Materials':
        tickers = ['03043.KL','03060.KL']
        get_stock_data(tickers)
    elif options == 'Construction':
        tickers = ['03017.KL','03042.KL','03050.KL']
        get_stock_data(tickers)
    elif options == 'Consumer Services':
        tickers = ['03015.KL','03019.KL','03021.KL','03025.KL','03053.KL','03063.KL']
        get_stock_data(tickers)
    elif options == 'Digital Services':
        tickers = ['03001.KL','03002.KL','03008.KL','03022.KL','03036.KL','03045.KL']
        get_stock_data(tickers)
    elif options == 'Food & Beverages':
        tickers = ['03032.KL','03048.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Providers':
        tickers = ['03023.KL']
        get_stock_data(tickers)
    elif options == 'Household Goods':
        tickers = ['03009.KL','03012.KL','03054.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Materials, Components & Equipment':
        tickers = ['03027.KL','03031.KL','03056.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Services':
        tickers = ['03024.KL','03029.KL','03033.KL','03052.KL','03061.KL','03062.KL']
        get_stock_data(tickers)
    elif options == 'Metals':
        tickers = ['03028.KL']
        get_stock_data(tickers)
    elif options == 'Other Financials':
        tickers = ['03059.KL']
        get_stock_data(tickers)
    elif options == 'Packaging Materials':
        tickers = ['03040.KL']
        get_stock_data(tickers)
    elif options == 'Personal Goods':
        tickers = ['03037.KL']
        get_stock_data(tickers)
    elif options == 'Pharmaceuticals':
        tickers = ['03006.KL']
        get_stock_data(tickers)
    elif options == 'Plantation':
        tickers = ['03055.KL']
        get_stock_data(tickers)
    elif options == 'Semiconductors':
        tickers = ['03011.KL']
        get_stock_data(tickers)
    elif options == 'Software':
        tickers = ['03030.KL','03039.KL','03041.KL','03046.KL','03057.KL','03058.KL']
        get_stock_data(tickers)



    placeholder = st.empty()

    while True:
        with placeholder.container():
            df = get_stock_data(tickers)
            st.dataframe(df.sort_values(by="Current Price", ascending=False), use_container_width=True)
        time.sleep(refresh_rate)



#comapring

def main_ticker_compare(invest_amount,options):

    if options == 'Agricultural Products':
        tickers = ['136.KL','5278.KL','5300.KL','6633.KL','7084.KL','7085.KL','7134.KL','7174.KL','7176.KL','7252.KL','7439.KL','9385.KL','9776.KL']
        get_stock_data(tickers)
    elif options == 'Auto Parts':
        tickers = ['5015.KL','5198.KL','5271.KL','5322.KL','7004.KL','7096.KL','7132.KL','7192.KL','7226.KL','7773.KL','7811.KL','9083.KL']
        get_stock_data(tickers)
    elif options == 'Automotive':
        tickers = ['1619.KL','3301.KL','4006.KL','4197.KL','4405.KL','5242.KL','5248.KL','5983.KL','7060.KL','7080.KL']
        get_stock_data(tickers)
    elif options == 'Banking':
        tickers = ['1015.KL','1023.KL','1066.KL','1082.KL','1155.KL','1295.KL','2488.KL','5185.KL','5258.KL','5819.KL','2488R1.KL']
        get_stock_data(tickers)
    elif options == 'Building Materials':
        tickers = ['2852.KL','3794.KL','5000.KL','5009.KL','5021.KL','5048.KL','5165.KL','5273.KL','5371.KL','6211.KL','7016.KL','7043.KL','7073.KL','7086.KL','7115.KL','7140.KL','7162.KL','7165.KL','7219.KL','7232.KL','7235.KL','7239.KL','7544.KL','7609.KL','8117.KL','8419.KL','8435.KL','9237.KL']
        get_stock_data(tickers)
    elif options == 'Business Trust':
        tickers = ['5320.KL']
        get_stock_data(tickers)
    elif options == 'Chemicals':
        tickers = ['54.KL','3298.KL','4758.KL','5134.KL','5143.KL','5147.KL','5151.KL','5183.KL','5284.KL','5289.KL','5330.KL','7173.KL','7222.KL','7498.KL','8443.KL','9954.KL']
        get_stock_data(tickers)
    elif options == 'Closed End Fund':
        tickers = ['5108.KL']
        get_stock_data(tickers)
    elif options == 'Construction':
        tickers = ['192.KL','198.KL','2283.KL','3204.KL','3336.KL','3565.KL','4723.KL','4847.KL','5006.KL','5042.KL','5054.KL','5070.KL','5085.KL','5129.KL','5169.KL','5171.KL','5190.KL','5205.KL','5226.KL','5253.KL','5263.KL','5281.KL','5293.KL','5297.KL','5310.KL','5329.KL','5398.KL','5622.KL','5703.KL','5932.KL','6807.KL','7028.KL','7047.KL','7070.KL','7071.KL','7078.KL','7145.KL','7161.KL','7195.KL','7240.KL','7528.KL','7595.KL','8192.KL','8311.KL','8591.KL','8834.KL','8877.KL','9261.KL','9571.KL','9598.KL','9628.KL','9679.KL','9717.KL']
        get_stock_data(tickers)
    elif options == 'Consumer Services':
        tickers = ['180.KL','5104.KL','5131.KL','5166.KL','5231.KL','5908.KL','7121.KL','7129.KL','7208.KL','7223.KL','7315.KL','7757.KL','9091.KL','9423.KL','9792.KL']
        get_stock_data(tickers)
    elif options == 'Digital Services':
        tickers = ['29.KL','126.KL','138.KL','200.KL','253.KL','4456.KL','5011.KL','5028.KL','5204.KL','5216.KL','5301.KL','5309.KL','8338.KL','9008.KL','9075.KL']
        get_stock_data(tickers)
    elif options == 'Diversified Industrials':
        tickers = ['3034.KL','3395.KL','3476.KL','5211.KL','5311.KL','5843.KL','6491.KL','7005.KL','8702.KL']
        get_stock_data(tickers)
    elif options == 'Electricity':
        tickers = ['3069.KL','5264.KL','5347.KL','7471.KL']
        get_stock_data(tickers)
    elif options == 'Energy, Infrastructure, Equipment & Services':
        tickers = ['91.KL','219.KL','5071.KL','5115.KL','5132.KL','5133.KL','5141.KL','5142.KL','5186.KL','5210.KL','5218.KL','5243.KL','5255.KL','5257.KL','5321.KL','7108.KL','7228.KL','7250.KL','7253.KL','7277.KL','7293.KL','8613.KL']
        get_stock_data(tickers)
    elif options == 'Energy':
        tickers = ['3042.KL','4324.KL','5199.KL']
        get_stock_data(tickers)
    elif options == 'Food & Beverages':
        tickers = ['12.KL','212.KL','2658.KL','2828.KL','2836.KL','3026.KL','3255.KL','3662.KL','3689.KL','4065.KL','4707.KL','5008.KL','5024.KL','5102.KL','5157.KL','5187.KL','5188.KL','5202.KL','5306.KL','5328.KL','5533.KL','6203.KL','6432.KL','7035.KL','7103.KL','7107.KL','7167.KL','7216.KL','7237.KL','7243.KL','8303.KL','8478.KL','9946.KL']
        get_stock_data(tickers)
    elif options == 'Gas, Water & Multi-Utilities':
        tickers = ['4677.KL','5041.KL','5209.KL','5272.KL','6033.KL','6742.KL','8524.KL','8567.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Equipment & Services':
        tickers = ['1.KL','163.KL','256.KL','5168.KL','7106.KL','7113.KL','7153.KL','7191.KL','7803.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Providers':
        tickers = ['101.KL','222.KL','5225.KL','5878.KL']
        get_stock_data(tickers)
    elif options == 'Household Goods':
        tickers = ['197.KL','229.KL','239.KL','2755.KL','3719.KL','5022.KL','5066.KL','5107.KL','5159.KL','5160.KL','5336.KL','6939.KL','7006.KL','7062.KL','7088.KL','7089.KL','7094.KL','7128.KL','7149.KL','7152.KL','7180.KL','7186.KL','7200.KL','7202.KL','7203.KL','7211.KL','7215.KL','7246.KL','7412.KL','7935.KL','7943.KL','8079.KL','8605.KL','9172.KL','9407.KL','9997.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Engineering':
        tickers = ['151.KL','185.KL','5163.KL','5219.KL','5568.KL','6998.KL','7033.KL','7170.KL','7212.KL','7229.KL','9466.KL','9741.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Materials, Components & Equipment':
        tickers = ['149.KL','161.KL','196.KL','225.KL','270.KL','2127.KL','3247.KL','5007.KL','5068.KL','5152.KL','5167.KL','5170.KL','5192.KL','5208.KL','5220.KL','5276.KL','5277.KL','5291.KL','5302.KL','5317.KL','5327.KL','6637.KL','6963.KL','6971.KL','7050.KL','7076.KL','7091.KL','7095.KL','7100.KL','7133.KL','7137.KL','7146.KL','7155.KL','7197.KL','7207.KL','7227.KL','7231.KL','7233.KL','7986.KL','8176.KL','8648.KL','8907.KL','9318.KL','9601.KL','9822.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Services':
        tickers = ['39.KL','43.KL','58.KL','64.KL','99.KL','257.KL','268.KL','1368.KL','3107.KL','5035.KL','5037.KL','5308.KL','5673.KL','6874.KL','7018.KL','7036.KL','7083.KL','7163.KL','7201.KL','7241.KL','7374.KL','7579.KL','8044.KL','8486.KL']
        get_stock_data(tickers)
    elif options == 'Insurance':
        tickers = ['1058.KL','1163.KL','1198.KL','5230.KL','6009.KL','6139.KL','6459.KL','8621.KL','1163PA.KL']
        get_stock_data(tickers)
    elif options == 'Media':
        tickers = ['159.KL','4502.KL','5090.KL','5252.KL','6084.KL','6399.KL','9431.KL']
        get_stock_data(tickers)
    elif options == 'Metals':
        tickers = ['207.KL','2674.KL','2984.KL','3778.KL','4235.KL','5010.KL','5056.KL','5072.KL','5087.KL','5094.KL','5098.KL','5125.KL','5178.KL','5232.KL','5298.KL','5331.KL','5436.KL','5665.KL','5797.KL','5916.KL','6149.KL','6556.KL','7014.KL','7020.KL','7097.KL','7099.KL','7172.KL','7199.KL','7214.KL','7217.KL','7221.KL','7225.KL','7245.KL','7692.KL','8869.KL','9199.KL','9326.KL','9873.KL','9881.KL']
        get_stock_data(tickers)
    elif options == 'Oil & Gas Producers':
        tickers = ['3042.KL','4324.KL','5199.KL']
        get_stock_data(tickers)
    elif options == 'Other Energy Resources':
        tickers = ['2739.KL','7164.KL']
        get_stock_data(tickers)
    elif options == 'Other Financials':
        tickers = ['242.KL','1171.KL','1818.KL','2143.KL','2186.KL','3379.KL','3441.KL','5088.KL','5139.KL','5228.KL','5274.KL','5325.KL','6483.KL','7082.KL','9296.KL']
        get_stock_data(tickers)
    elif options == 'Packaging Materials':
        tickers = ['269.KL','3883.KL','4731.KL','5065.KL','5100.KL','5105.KL','6297.KL','7017.KL','7029.KL','7034.KL','7114.KL','7157.KL','7247.KL','7248.KL','7285.KL','8052.KL','8125.KL','8273.KL','8362.KL','9148.KL','9938.KL']
        get_stock_data(tickers)
    elif options == 'Personal Goods':
        tickers = ['49.KL','157.KL','183.KL','250.KL','3514.KL','4162.KL','5081.KL','5156.KL','5172.KL','5247.KL','5295.KL','6068.KL','7087.KL','7139.KL','7154.KL','7168.KL','7184.KL','7209.KL','7234.KL','7722.KL','8532.KL','8966.KL','9288.KL','9369.KL']
        get_stock_data(tickers)
    elif options == 'Pharmaceuticals':
        tickers = ['2.KL','201.KL','7081.KL','7090.KL','7148.KL','7178.KL']
        get_stock_data(tickers)
    elif options == 'Plantation':
        tickers = ['1899.KL','1902.KL','1929.KL','1961.KL','1996.KL','2038.KL','2054.KL','2089.KL','2135.KL','2291.KL','2445.KL','2453.KL','2542.KL','2569.KL','2593.KL','2607.KL','3948.KL','4316.KL','4383.KL','4936.KL','5012.KL','5026.KL','5027.KL','5029.KL','5047.KL','5069.KL','5112.KL','5113.KL','5126.KL','5135.KL','5138.KL','5222.KL','5223.KL','5285.KL','5319.KL','5323.KL','6262.KL','7054.KL','7382.KL','7501.KL','8982.KL','9059.KL','9695.KL']
        get_stock_data(tickers)
    elif options == 'Property':
        tickers = ['56.KL','230.KL','1147.KL','1503.KL','1538.KL','1589.KL','1651.KL','1694.KL','1724.KL','2224.KL','2259.KL','2305.KL','2429.KL','2682.KL','3158.KL','3174.KL','3239.KL','3417.KL','3557.KL','3573.KL','3611.KL','3743.KL','3913.KL','4022.KL','4057.KL','4251.KL','4286.KL','4375.KL','4464.KL','4596.KL','5020.KL','5038.KL','5040.KL','5049.KL','5053.KL','5062.KL','5073.KL','5075.KL','5084.KL','5148.KL','5175.KL','5182.KL','5191.KL','5200.KL','5207.KL','5213.KL','5236.KL','5239.KL','5249.KL','5283.KL','5288.KL','5313.KL','5315.KL','5401.KL','5606.KL','5738.KL','5789.KL','5827.KL','6017.KL','6041.KL','6076.KL','6114.KL','6173.KL','6181.KL','6378.KL','6602.KL','6718.KL','6769.KL','6815.KL','6912.KL','7003.KL','7007.KL','7010.KL','7055.KL','7066.KL','7077.KL','7079.KL','7105.KL','7120.KL','7131.KL','7179.KL','7198.KL','7249.KL','7323.KL','7617.KL','7765.KL','7889.KL','8141.KL','8206.KL','8494.KL','8583.KL','8664.KL','8893.KL','8923.KL','9539.KL','9687.KL','9814.KL','9962.KL']
        get_stock_data(tickers)
    elif options == 'Real Estate Investment Trusts':
        tickers = ['5106.KL','5109.KL','5110.KL','5111.KL','5116.KL','5120.KL','5121.KL','5123.KL','5127.KL','5130.KL','5176.KL','5180.KL','5212.KL','5227.KL','5269.KL','5280.KL','5299.KL','5307.KL','5338.KL','5235SS.KL']
        get_stock_data(tickers)
    elif options == 'Renewable Energy':
        tickers = ['118.KL','168.KL','193.KL','215.KL','223.KL','5184.KL','5614.KL','7130.KL']
        get_stock_data(tickers)
    elif options == 'Retailers':
        tickers = ['4995.KL','5080.KL','5250.KL','5275.KL','5296.KL','5305.KL','5316.KL','5318.KL','5326.KL','5337.KL','5657.KL','5681.KL','6351.KL','6599.KL','7048.KL','7052.KL','7230.KL','7668.KL','8672.KL']
        get_stock_data(tickers)
    elif options == 'Semiconductors':
        tickers = ['97.KL','127.KL','128.KL','143.KL','166.KL','3867.KL','4359.KL','5005.KL','5292.KL','7022.KL','7204.KL','9334.KL']
        get_stock_data(tickers)
    elif options == 'Software':
        tickers = ['8.KL','40.KL','41.KL','51.KL','65.KL','5195.KL','7181.KL']
        get_stock_data(tickers)
    elif options == 'Special Purpose Acquisition Company':
        tickers = ['5270.KL']
        get_stock_data(tickers)
    elif options == 'Technology Equipment':
        tickers = ['83.KL','90.KL','104.KL','113.KL','146.KL','208.KL','246.KL','259.KL','5036.KL','5161.KL','5162.KL','5286.KL','7160.KL','9377.KL','9393.KL']
        get_stock_data(tickers)
    elif options == 'Telecommunications Equipment':
        tickers = ['7031.KL']
        get_stock_data(tickers)
    elif options == 'Telecommunications Service Providers':
        tickers = ['32.KL','59.KL','82.KL','172.KL','4863.KL','5031.KL','5332.KL','6012.KL','6888.KL','6947.KL']
        get_stock_data(tickers)
    elif options == 'Transportation & Logistics Services':
        tickers = ['78.KL','2062.KL','3816.KL','4634.KL','5032.KL','5077.KL','5078.KL','5136.KL','5140.KL','5173.KL','5246.KL','5259.KL','5267.KL','5303.KL','6254.KL','6521.KL','7013.KL','7053.KL','7117.KL','7210.KL','7218.KL','7676.KL','8346.KL','8397.KL']
        get_stock_data(tickers)
    elif options == 'Transportation Equipment':
        tickers = ['5145.KL','5149.KL','7187.KL','8133.KL']
        get_stock_data(tickers)
    elif options == 'Travel, Leisure & Hospitality':
        tickers = ['37.KL','186.KL','1287.KL','1481.KL','1562.KL','1643.KL','2097.KL','3018.KL','3182.KL','3859.KL','3891.KL','3905.KL','4081.KL','4219.KL','4715.KL','5016.KL','5079.KL','5099.KL','5196.KL','5238.KL','5260.KL','5265.KL','5335.KL','5517.KL','5592.KL','8885.KL','9113.KL']
        get_stock_data(tickers)
    elif options == 'Wood & Wood Products':
        tickers = ['4243.KL','5001.KL','5025.KL','5082.KL','5095.KL','5101.KL','5197.KL','5576.KL','5649.KL','6904.KL','7025.KL','7123.KL','7169.KL','7188.KL','7854.KL','8745.KL','9016.KL','9121.KL']
        get_stock_data(tickers)


    if 'tickers' in locals():
        df = get_stock_data(tickers)
        df_filtered = df[(df['Open'] <= invest_amount)]

        st.dataframe(
            df_filtered.sort_values(by="Current Price", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Please select a sector to load tickers.")


def ace_tickers_compare(invest_amount,options):
    if options == 'Agricultural Products':
        tickers = ['0148.KL','0171.KL','0300.KL']
        get_stock_data(tickers)
    elif options == 'Auto Parts':
        tickers = ['0190.KL','0263.KL','0322.KL','0350.KL']
        get_stock_data(tickers)
    elif options == 'Building Materials':
        tickers = ['0227.KL','0247.KL','0302.KL','0306.KL']
        get_stock_data(tickers)
    elif options == 'Chemicals':
        tickers = ['0038.KL','0055.KL','0105.KL','0301.KL','0331.KL','0349.KL']
        get_stock_data(tickers)
    elif options == 'Construction':
        tickers = ['0045.KL','0109.KL','0162.KL','0206.KL','0221.KL','0226.KL','0235.KL','0237.KL','0241.KL','0245.KL',
                '0273.KL','0292.KL','0310.KL','0345.KL','0347.KL','0351.KL','0359.KL','0360.KL']
        get_stock_data(tickers)
    elif options == 'Consumer Services':
        tickers = ['0140.KL','0158.KL','0178.KL','0280.KL','0281.KL','0304.KL','0330.KL','0342.KL','0356.KL']
        get_stock_data(tickers)
    elif options == 'Digital Services':
        tickers = ['0006.KL','0093.KL','0117.KL','0131.KL','0145.KL','0154.KL','0176.KL','0202.KL','0249.KL','0277.KL','0319.KL']
        get_stock_data(tickers)
    elif options == 'Energy Infrastructure Equipment & Services':
        tickers = ['0220.KL','0320.KL']
        get_stock_data(tickers)
    elif options == 'Food & Beverages':
        tickers = ['0074.KL','0095.KL','0179.KL','0252.KL','0260.KL','0271.KL','0309.KL','0312.KL','0316.KL','0327.KL','0338.KL']
        get_stock_data(tickers)
    elif options == 'Gas, Water & Multi-Utilities':
        tickers = ['0011.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Equipment & Services':
        tickers = ['0155.KL','0182.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Providers':
        tickers = ['0075.KL','0243.KL','0283.KL','0303.KL','0329.KL','0332.KL']
        get_stock_data(tickers)
    elif options == 'Household Goods':
        tickers = ['0170.KL','0205.KL','0216.KL','0279.KL','0326.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Engineering':
        tickers = ['0177.KL','0240.KL','0255.KL','0361.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Materials, Components & Equipment':
        tickers = ['0025.KL','0028.KL','0072.KL','0084.KL','0100.KL','0102.KL','0133.KL','0175.KL','0188.KL','0217.KL','0238.KL',
                '0248.KL','0288.KL','0295.KL','0298.KL','0307.KL','0325.KL','0337.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Services':
        tickers = ['0024.KL','0081.KL','0089.KL','0122.KL','0160.KL','0167.KL','0187.KL','0213.KL','0218.KL','0231.KL','0232.KL',
                '0261.KL','0284.KL','0289.KL','0291.KL','0293.KL','0296.KL','0317.KL','0321.KL','0323.KL','0339.KL',
                '0346.KL','0348.KL','0352.KL','0353.KL','0355.KL']
        get_stock_data(tickers)
    elif options == 'Media':
        tickers = ['0007.KL','0147.KL','0173.KL','0315.KL']
        get_stock_data(tickers)
    elif options == 'Metals':
        tickers = ['0098.KL','0211.KL','0266.KL','0297.KL','0313.KL','0336.KL','0341.KL']
        get_stock_data(tickers)
    elif options == 'Other Financials':
        tickers = ['0053.KL','0150.KL','0285.KL','0286.KL']
        get_stock_data(tickers)
    elif options == 'Packaging Materials':
        tickers = ['0228.KL']
        get_stock_data(tickers)
    elif options == 'Personal Goods':
        tickers = ['0333.KL','0335.KL']
        get_stock_data(tickers)
    elif options == 'Plantation':
        tickers = ['0189.KL']
        get_stock_data(tickers)
    elif options == 'Property':
        tickers = ['0308.KL']
        get_stock_data(tickers)
    elif options == 'Renewable Energy':
        tickers = ['0233.KL','0262.KL','0318.KL','0340.KL']
        get_stock_data(tickers)
    elif options == 'Retailers':
        tickers = ['0210.KL','0287.KL','0357.KL']
        get_stock_data(tickers)
    elif options == 'Semiconductors':
        tickers = ['0070.KL','0120.KL','0251.KL','0272.KL','0275.KL','0328.KL']
        get_stock_data(tickers)
    elif options == 'Software':
        tickers = ['0010.KL','0018.KL','0020.KL','0023.KL','0026.KL','0050.KL','0066.KL','0068.KL','0069.KL','0079.KL','0086.KL','0094.KL',
                '0106.KL','0107.KL','0108.KL','0119.KL','0132.KL','0152.KL','0156.KL','0174.KL','0203.KL','0236.KL','0258.KL',
                '0276.KL','0290.KL','0311.KL','0343.KL']
        get_stock_data(tickers)
    elif options == 'Technology Equipment':
        tickers = ['0005.KL','0036.KL','0060.KL','0085.KL','0111.KL','0112.KL','0169.KL','0181.KL','0191.KL','0209.KL','0265.KL',
                '0267.KL','0278.KL','0358.KL']
        get_stock_data(tickers)
    elif options == 'Telecommunications Equipment':
        tickers = ['0017.KL','0035.KL','0096.KL','0103.KL','0123.KL','0129.KL']
        get_stock_data(tickers)
    elif options == 'Telecom Service Providers':
        tickers = ['0092.KL','0165.KL','0195.KL']
        get_stock_data(tickers)
    elif options == 'Transportation & Logistics':
        tickers = ['0034.KL','0048.KL','0080.KL','0199.KL','0282.KL','0299.KL','0305.KL']
        get_stock_data(tickers)
    elif options == 'Travel, Leisure & Hospitality':
        tickers = ['0022.KL','0116.KL','0153.KL']
        get_stock_data(tickers)
  

    if 'tickers' in locals():
        df = get_stock_data(tickers)
        df_filtered = df[(df['Open'] <= invest_amount)]

        st.dataframe(
            df_filtered.sort_values(by="Current Price", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Please select a sector to load tickers.")

def etf_tickers_compare(invest_amount,options):

    if options == 'Bond Fund':
        tickers = ['0800EA.KL']
        get_stock_data(tickers)
    elif options == 'Commodity Fund':
        tickers = ['0828EA.KL']
        get_stock_data(tickers)
    elif options == 'Equity Fund':
        tickers = ['0820EA.KL','0821EA.KL','0822EA.KL','0823EA.KL','0824EA.KL','0825EA.KL','0827EA.KL','0829EA.KL','0829EB.KL','0838EA.KL','0839EA.KL']
        get_stock_data(tickers)


    if 'tickers' in locals():
        df = get_stock_data(tickers)
        df_filtered = df[(df['Open'] <= invest_amount)]

        st.dataframe(
            df_filtered.sort_values(by="Current Price", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Please select a sector to load tickers.")


def leap_tickers_compare(invest_amount,options):

    if options == 'Agricultural Products':
        tickers = ['03051.KL']
        get_stock_data(tickers)
    elif options == 'Building Materials':
        tickers = ['03043.KL','03060.KL']
        get_stock_data(tickers)
    elif options == 'Construction':
        tickers = ['03017.KL','03042.KL','03050.KL']
        get_stock_data(tickers)
    elif options == 'Consumer Services':
        tickers = ['03015.KL','03019.KL','03021.KL','03025.KL','03053.KL','03063.KL']
        get_stock_data(tickers)
    elif options == 'Digital Services':
        tickers = ['03001.KL','03002.KL','03008.KL','03022.KL','03036.KL','03045.KL']
        get_stock_data(tickers)
    elif options == 'Food & Beverages':
        tickers = ['03032.KL','03048.KL']
        get_stock_data(tickers)
    elif options == 'Health Care Providers':
        tickers = ['03023.KL']
        get_stock_data(tickers)
    elif options == 'Household Goods':
        tickers = ['03009.KL','03012.KL','03054.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Materials, Components & Equipment':
        tickers = ['03027.KL','03031.KL','03056.KL']
        get_stock_data(tickers)
    elif options == 'Industrial Services':
        tickers = ['03024.KL','03029.KL','03033.KL','03052.KL','03061.KL','03062.KL']
        get_stock_data(tickers)
    elif options == 'Metals':
        tickers = ['03028.KL']
        get_stock_data(tickers)
    elif options == 'Other Financials':
        tickers = ['03059.KL']
        get_stock_data(tickers)
    elif options == 'Packaging Materials':
        tickers = ['03040.KL']
        get_stock_data(tickers)
    elif options == 'Personal Goods':
        tickers = ['03037.KL']
        get_stock_data(tickers)
    elif options == 'Pharmaceuticals':
        tickers = ['03006.KL']
        get_stock_data(tickers)
    elif options == 'Plantation':
        tickers = ['03055.KL']
        get_stock_data(tickers)
    elif options == 'Semiconductors':
        tickers = ['03011.KL']
        get_stock_data(tickers)
    elif options == 'Software':
        tickers = ['03030.KL','03039.KL','03041.KL','03046.KL','03057.KL','03058.KL']
        get_stock_data(tickers)



    if 'tickers' in locals():
        df = get_stock_data(tickers)
        df_filtered = df[(df['Open'] <= invest_amount)]

        st.dataframe(
            df_filtered.sort_values(by="Current Price", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Please select a sector to load tickers.")

def main_ticker_compare2(invest_amount,options2):

    if options2 == 'Agricultural Products':
        tickers = ['0136.KL','5278.KL','5300.KL','6633.KL','7084.KL','7085.KL','7134.KL','7174.KL','7176.KL','7252.KL','7439.KL','9385.KL','9776.KL']
        get_stock_data(tickers)
    elif options2 == 'Auto Parts':
        tickers = ['5015.KL','5198.KL','5271.KL','5322.KL','7004.KL','7096.KL','7132.KL','7192.KL','7226.KL','7773.KL','7811.KL','9083.KL']
        get_stock_data(tickers)
    elif options2 == 'Automotive':
        tickers = ['1619.KL','3301.KL','4006.KL','4197.KL','4405.KL','5242.KL','5248.KL','5983.KL','7060.KL','7080.KL']
        get_stock_data(tickers)
    elif options2 == 'Banking':
        tickers = ['1015.KL','1023.KL','1066.KL','1082.KL','1155.KL','1295.KL','2488.KL','5185.KL','5258.KL','5819.KL','2488R1.KL']
        get_stock_data(tickers)
    elif options2 == 'Building Materials':
        tickers = ['2852.KL','3794.KL','5000.KL','5009.KL','5021.KL','5048.KL','5165.KL','5273.KL','5371.KL','6211.KL','7016.KL','7043.KL','7073.KL','7086.KL','7115.KL','7140.KL','7162.KL','7165.KL','7219.KL','7232.KL','7235.KL','7239.KL','7544.KL','7609.KL','8117.KL','8419.KL','8435.KL','9237.KL']
        get_stock_data(tickers)
    elif options2 == 'Business Trust':
        tickers = ['5320.KL']
        get_stock_data(tickers)
    elif options2 == 'Chemicals':
        tickers = ['54.KL','3298.KL','4758.KL','5134.KL','5143.KL','5147.KL','5151.KL','5183.KL','5284.KL','5289.KL','5330.KL','7173.KL','7222.KL','7498.KL','8443.KL','9954.KL']
        get_stock_data(tickers)
    elif options2 == 'Closed End Fund':
        tickers = ['5108.KL']
        get_stock_data(tickers)
    elif options2 == 'Construction':
        tickers = ['192.KL','198.KL','2283.KL','3204.KL','3336.KL','3565.KL','4723.KL','4847.KL','5006.KL','5042.KL','5054.KL','5070.KL','5085.KL','5129.KL','5169.KL','5171.KL','5190.KL','5205.KL','5226.KL','5253.KL','5263.KL','5281.KL','5293.KL','5297.KL','5310.KL','5329.KL','5398.KL','5622.KL','5703.KL','5932.KL','6807.KL','7028.KL','7047.KL','7070.KL','7071.KL','7078.KL','7145.KL','7161.KL','7195.KL','7240.KL','7528.KL','7595.KL','8192.KL','8311.KL','8591.KL','8834.KL','8877.KL','9261.KL','9571.KL','9598.KL','9628.KL','9679.KL','9717.KL']
        get_stock_data(tickers)
    elif options2 == 'Consumer Services':
        tickers = ['180.KL','5104.KL','5131.KL','5166.KL','5231.KL','5908.KL','7121.KL','7129.KL','7208.KL','7223.KL','7315.KL','7757.KL','9091.KL','9423.KL','9792.KL']
        get_stock_data(tickers)
    elif options2 == 'Digital Services':
        tickers = ['29.KL','126.KL','138.KL','200.KL','253.KL','4456.KL','5011.KL','5028.KL','5204.KL','5216.KL','5301.KL','5309.KL','8338.KL','9008.KL','9075.KL']
        get_stock_data(tickers)
    elif options2 == 'Diversified Industrials':
        tickers = ['3034.KL','3395.KL','3476.KL','5211.KL','5311.KL','5843.KL','6491.KL','7005.KL','8702.KL']
        get_stock_data(tickers)
    elif options2 == 'Electricity':
        tickers = ['3069.KL','5264.KL','5347.KL','7471.KL']
        get_stock_data(tickers)
    elif options2 == 'Energy, Infrastructure, Equipment & Services':
        tickers = ['91.KL','219.KL','5071.KL','5115.KL','5132.KL','5133.KL','5141.KL','5142.KL','5186.KL','5210.KL','5218.KL','5243.KL','5255.KL','5257.KL','5321.KL','7108.KL','7228.KL','7250.KL','7253.KL','7277.KL','7293.KL','8613.KL']
        get_stock_data(tickers)
    elif options2 == 'Energy':
        tickers = ['3042.KL','4324.KL','5199.KL']
        get_stock_data(tickers)
    elif options2 == 'Food & Beverages':
        tickers = ['12.KL','212.KL','2658.KL','2828.KL','2836.KL','3026.KL','3255.KL','3662.KL','3689.KL','4065.KL','4707.KL','5008.KL','5024.KL','5102.KL','5157.KL','5187.KL','5188.KL','5202.KL','5306.KL','5328.KL','5533.KL','6203.KL','6432.KL','7035.KL','7103.KL','7107.KL','7167.KL','7216.KL','7237.KL','7243.KL','8303.KL','8478.KL','9946.KL']
        get_stock_data(tickers)
    elif options2 == 'Gas, Water & Multi-Utilities':
        tickers = ['4677.KL','5041.KL','5209.KL','5272.KL','6033.KL','6742.KL','8524.KL','8567.KL']
        get_stock_data(tickers)
    elif options2 == 'Health Care Equipment & Services':
        tickers = ['1.KL','163.KL','256.KL','5168.KL','7106.KL','7113.KL','7153.KL','7191.KL','7803.KL']
        get_stock_data(tickers)
    elif options2 == 'Health Care Providers':
        tickers = ['101.KL','222.KL','5225.KL','5878.KL']
        get_stock_data(tickers)
    elif options2 == 'Household Goods':
        tickers = ['197.KL','229.KL','239.KL','2755.KL','3719.KL','5022.KL','5066.KL','5107.KL','5159.KL','5160.KL','5336.KL','6939.KL','7006.KL','7062.KL','7088.KL','7089.KL','7094.KL','7128.KL','7149.KL','7152.KL','7180.KL','7186.KL','7200.KL','7202.KL','7203.KL','7211.KL','7215.KL','7246.KL','7412.KL','7935.KL','7943.KL','8079.KL','8605.KL','9172.KL','9407.KL','9997.KL']
        get_stock_data(tickers)
    elif options2 == 'Industrial Engineering':
        tickers = ['151.KL','185.KL','5163.KL','5219.KL','5568.KL','6998.KL','7033.KL','7170.KL','7212.KL','7229.KL','9466.KL','9741.KL']
        get_stock_data(tickers)
    elif options2 == 'Industrial Materials, Components & Equipment':
        tickers = ['149.KL','161.KL','196.KL','225.KL','270.KL','2127.KL','3247.KL','5007.KL','5068.KL','5152.KL','5167.KL','5170.KL','5192.KL','5208.KL','5220.KL','5276.KL','5277.KL','5291.KL','5302.KL','5317.KL','5327.KL','6637.KL','6963.KL','6971.KL','7050.KL','7076.KL','7091.KL','7095.KL','7100.KL','7133.KL','7137.KL','7146.KL','7155.KL','7197.KL','7207.KL','7227.KL','7231.KL','7233.KL','7986.KL','8176.KL','8648.KL','8907.KL','9318.KL','9601.KL','9822.KL']
        get_stock_data(tickers)
    elif options2 == 'Industrial Services':
        tickers = ['39.KL','43.KL','58.KL','64.KL','99.KL','257.KL','268.KL','1368.KL','3107.KL','5035.KL','5037.KL','5308.KL','5673.KL','6874.KL','7018.KL','7036.KL','7083.KL','7163.KL','7201.KL','7241.KL','7374.KL','7579.KL','8044.KL','8486.KL']
        get_stock_data(tickers)
    elif options2 == 'Insurance':
        tickers = ['1058.KL','1163.KL','1198.KL','5230.KL','6009.KL','6139.KL','6459.KL','8621.KL','1163PA.KL']
        get_stock_data(tickers)
    elif options2 == 'Media':
        tickers = ['159.KL','4502.KL','5090.KL','5252.KL','6084.KL','6399.KL','9431.KL']
        get_stock_data(tickers)
    elif options2 == 'Metals':
        tickers = ['207.KL','2674.KL','2984.KL','3778.KL','4235.KL','5010.KL','5056.KL','5072.KL','5087.KL','5094.KL','5098.KL','5125.KL','5178.KL','5232.KL','5298.KL','5331.KL','5436.KL','5665.KL','5797.KL','5916.KL','6149.KL','6556.KL','7014.KL','7020.KL','7097.KL','7099.KL','7172.KL','7199.KL','7214.KL','7217.KL','7221.KL','7225.KL','7245.KL','7692.KL','8869.KL','9199.KL','9326.KL','9873.KL','9881.KL']
        get_stock_data(tickers)
    elif options2 == 'Oil & Gas Producers':
        tickers = ['3042.KL','4324.KL','5199.KL']
        get_stock_data(tickers)
    elif options2 == 'Other Energy Resources':
        tickers = ['2739.KL','7164.KL']
        get_stock_data(tickers)
    elif options2 == 'Other Financials':
        tickers = ['242.KL','1171.KL','1818.KL','2143.KL','2186.KL','3379.KL','3441.KL','5088.KL','5139.KL','5228.KL','5274.KL','5325.KL','6483.KL','7082.KL','9296.KL']
        get_stock_data(tickers)
    elif options2 == 'Packaging Materials':
        tickers = ['269.KL','3883.KL','4731.KL','5065.KL','5100.KL','5105.KL','6297.KL','7017.KL','7029.KL','7034.KL','7114.KL','7157.KL','7247.KL','7248.KL','7285.KL','8052.KL','8125.KL','8273.KL','8362.KL','9148.KL','9938.KL']
        get_stock_data(tickers)
    elif options2 == 'Personal Goods':
        tickers = ['49.KL','157.KL','183.KL','250.KL','3514.KL','4162.KL','5081.KL','5156.KL','5172.KL','5247.KL','5295.KL','6068.KL','7087.KL','7139.KL','7154.KL','7168.KL','7184.KL','7209.KL','7234.KL','7722.KL','8532.KL','8966.KL','9288.KL','9369.KL']
        get_stock_data(tickers)
    elif options2 == 'Pharmaceuticals':
        tickers = ['2.KL','201.KL','7081.KL','7090.KL','7148.KL','7178.KL']
        get_stock_data(tickers)
    elif options2 == 'Plantation':
        tickers = ['1899.KL','1902.KL','1929.KL','1961.KL','1996.KL','2038.KL','2054.KL','2089.KL','2135.KL','2291.KL','2445.KL','2453.KL','2542.KL','2569.KL','2593.KL','2607.KL','3948.KL','4316.KL','4383.KL','4936.KL','5012.KL','5026.KL','5027.KL','5029.KL','5047.KL','5069.KL','5112.KL','5113.KL','5126.KL','5135.KL','5138.KL','5222.KL','5223.KL','5285.KL','5319.KL','5323.KL','6262.KL','7054.KL','7382.KL','7501.KL','8982.KL','9059.KL','9695.KL']
        get_stock_data(tickers)
    elif options2 == 'Property':
        tickers = ['56.KL','230.KL','1147.KL','1503.KL','1538.KL','1589.KL','1651.KL','1694.KL','1724.KL','2224.KL','2259.KL','2305.KL','2429.KL','2682.KL','3158.KL','3174.KL','3239.KL','3417.KL','3557.KL','3573.KL','3611.KL','3743.KL','3913.KL','4022.KL','4057.KL','4251.KL','4286.KL','4375.KL','4464.KL','4596.KL','5020.KL','5038.KL','5040.KL','5049.KL','5053.KL','5062.KL','5073.KL','5075.KL','5084.KL','5148.KL','5175.KL','5182.KL','5191.KL','5200.KL','5207.KL','5213.KL','5236.KL','5239.KL','5249.KL','5283.KL','5288.KL','5313.KL','5315.KL','5401.KL','5606.KL','5738.KL','5789.KL','5827.KL','6017.KL','6041.KL','6076.KL','6114.KL','6173.KL','6181.KL','6378.KL','6602.KL','6718.KL','6769.KL','6815.KL','6912.KL','7003.KL','7007.KL','7010.KL','7055.KL','7066.KL','7077.KL','7079.KL','7105.KL','7120.KL','7131.KL','7179.KL','7198.KL','7249.KL','7323.KL','7617.KL','7765.KL','7889.KL','8141.KL','8206.KL','8494.KL','8583.KL','8664.KL','8893.KL','8923.KL','9539.KL','9687.KL','9814.KL','9962.KL']
        get_stock_data(tickers)
    elif options2 == 'Real Estate Investment Trusts':
        tickers = ['5106.KL','5109.KL','5110.KL','5111.KL','5116.KL','5120.KL','5121.KL','5123.KL','5127.KL','5130.KL','5176.KL','5180.KL','5212.KL','5227.KL','5269.KL','5280.KL','5299.KL','5307.KL','5338.KL','5235SS.KL']
        get_stock_data(tickers)
    elif options2 == 'Renewable Energy':
        tickers = ['118.KL','168.KL','193.KL','215.KL','223.KL','5184.KL','5614.KL','7130.KL']
        get_stock_data(tickers)
    elif options2 == 'Retailers':
        tickers = ['4995.KL','5080.KL','5250.KL','5275.KL','5296.KL','5305.KL','5316.KL','5318.KL','5326.KL','5337.KL','5657.KL','5681.KL','6351.KL','6599.KL','7048.KL','7052.KL','7230.KL','7668.KL','8672.KL']
        get_stock_data(tickers)
    elif options2 == 'Semiconductors':
        tickers = ['97.KL','127.KL','128.KL','143.KL','166.KL','3867.KL','4359.KL','5005.KL','5292.KL','7022.KL','7204.KL','9334.KL']
        get_stock_data(tickers)
    elif options2 == 'Software':
        tickers = ['8.KL','40.KL','41.KL','51.KL','65.KL','5195.KL','7181.KL']
        get_stock_data(tickers)
    elif options2 == 'Special Purpose Acquisition Company':
        tickers = ['5270.KL']
        get_stock_data(tickers)
    elif options2 == 'Technology Equipment':
        tickers = ['83.KL','90.KL','104.KL','113.KL','146.KL','208.KL','246.KL','259.KL','5036.KL','5161.KL','5162.KL','5286.KL','7160.KL','9377.KL','9393.KL']
        get_stock_data(tickers)
    elif options2 == 'Telecommunications Equipment':
        tickers = ['7031.KL']
        get_stock_data(tickers)
    elif options2 == 'Telecommunications Service Providers':
        tickers = ['32.KL','59.KL','82.KL','172.KL','4863.KL','5031.KL','5332.KL','6012.KL','6888.KL','6947.KL']
        get_stock_data(tickers)
    elif options2 == 'Transportation & Logistics Services':
        tickers = ['78.KL','2062.KL','3816.KL','4634.KL','5032.KL','5077.KL','5078.KL','5136.KL','5140.KL','5173.KL','5246.KL','5259.KL','5267.KL','5303.KL','6254.KL','6521.KL','7013.KL','7053.KL','7117.KL','7210.KL','7218.KL','7676.KL','8346.KL','8397.KL']
        get_stock_data(tickers)
    elif options2 == 'Transportation Equipment':
        tickers = ['5145.KL','5149.KL','7187.KL','8133.KL']
        get_stock_data(tickers)
    elif options2 == 'Travel, Leisure & Hospitality':
        tickers = ['37.KL','186.KL','1287.KL','1481.KL','1562.KL','1643.KL','2097.KL','3018.KL','3182.KL','3859.KL','3891.KL','3905.KL','4081.KL','4219.KL','4715.KL','5016.KL','5079.KL','5099.KL','5196.KL','5238.KL','5260.KL','5265.KL','5335.KL','5517.KL','5592.KL','8885.KL','9113.KL']
        get_stock_data(tickers)
    elif options2 == 'Wood & Wood Products':
        tickers = ['4243.KL','5001.KL','5025.KL','5082.KL','5095.KL','5101.KL','5197.KL','5576.KL','5649.KL','6904.KL','7025.KL','7123.KL','7169.KL','7188.KL','7854.KL','8745.KL','9016.KL','9121.KL']
        get_stock_data(tickers)


    if 'tickers' in locals():
        df = get_stock_data(tickers)
        df_filtered = df[(df['Open'] <= invest_amount)]

        st.dataframe(
            df_filtered.sort_values(by="Current Price", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Please select a sector to load tickers.")


def ace_tickers_compare2(invest_amount, options2):
    if options2 == 'Agricultural Products':
        tickers = ['0148.KL','0171.KL','0300.KL']
        get_stock_data(tickers)
    elif options2 == 'Auto Parts':
        tickers = ['0190.KL','0263.KL','0322.KL','0350.KL']
        get_stock_data(tickers)
    elif options2 == 'Building Materials':
        tickers = ['0227.KL','0247.KL','0302.KL','0306.KL']
        get_stock_data(tickers)
    elif options2 == 'Chemicals':
        tickers = ['0038.KL','0055.KL','0105.KL','0301.KL','0331.KL','0349.KL']
        get_stock_data(tickers)
    elif options2 == 'Construction':
        tickers = ['0045.KL','0109.KL','0162.KL','0206.KL','0221.KL','0226.KL','0235.KL','0237.KL','0241.KL','0245.KL',
                '0273.KL','0292.KL','0310.KL','0345.KL','0347.KL','0351.KL','0359.KL','0360.KL']
        get_stock_data(tickers)
    elif options2 == 'Consumer Services':
        tickers = ['0140.KL','0158.KL','0178.KL','0280.KL','0281.KL','0304.KL','0330.KL','0342.KL','0356.KL']
        get_stock_data(tickers)
    elif options2 == 'Digital Services':
        tickers = ['0006.KL','0093.KL','0117.KL','0131.KL','0145.KL','0154.KL','0176.KL','0202.KL','0249.KL','0277.KL','0319.KL']
        get_stock_data(tickers)
    elif options2 == 'Energy Infrastructure Equipment & Services':
        tickers = ['0220.KL','0320.KL']
        get_stock_data(tickers)
    elif options2 == 'Food & Beverages':
        tickers = ['0074.KL','0095.KL','0179.KL','0252.KL','0260.KL','0271.KL','0309.KL','0312.KL','0316.KL','0327.KL','0338.KL']
        get_stock_data(tickers)
    elif options2 == 'Gas, Water & Multi-Utilities':
        tickers = ['0011.KL']
        get_stock_data(tickers)
    elif options2 == 'Health Care Equipment & Services':
        tickers = ['0155.KL','0182.KL']
        get_stock_data(tickers)
    elif options2 == 'Health Care Providers':
        tickers = ['0075.KL','0243.KL','0283.KL','0303.KL','0329.KL','0332.KL']
        get_stock_data(tickers)
    elif options2 == 'Household Goods':
        tickers = ['0170.KL','0205.KL','0216.KL','0279.KL','0326.KL']
        get_stock_data(tickers)
    elif options2 == 'Industrial Engineering':
        tickers = ['0177.KL','0240.KL','0255.KL','0361.KL']
        get_stock_data(tickers)
    elif options2 == 'Industrial Materials, Components & Equipment':
        tickers = ['0025.KL','0028.KL','0072.KL','0084.KL','0100.KL','0102.KL','0133.KL','0175.KL','0188.KL','0217.KL','0238.KL',
                '0248.KL','0288.KL','0295.KL','0298.KL','0307.KL','0325.KL','0337.KL']
        get_stock_data(tickers)
    elif options2 == 'Industrial Services':
        tickers = ['0024.KL','0081.KL','0089.KL','0122.KL','0160.KL','0167.KL','0187.KL','0213.KL','0218.KL','0231.KL','0232.KL',
                '0261.KL','0284.KL','0289.KL','0291.KL','0293.KL','0296.KL','0317.KL','0321.KL','0323.KL','0339.KL',
                '0346.KL','0348.KL','0352.KL','0353.KL','0355.KL']
        get_stock_data(tickers)
    elif options2 == 'Media':
        tickers = ['0007.KL','0147.KL','0173.KL','0315.KL']
        get_stock_data(tickers)
    elif options2 == 'Metals':
        tickers = ['0098.KL','0211.KL','0266.KL','0297.KL','0313.KL','0336.KL','0341.KL']
        get_stock_data(tickers)
    elif options2 == 'Other Financials':
        tickers = ['0053.KL','0150.KL','0285.KL','0286.KL']
        get_stock_data(tickers)
    elif options2 == 'Packaging Materials':
        tickers = ['0228.KL']
        get_stock_data(tickers)
    elif options2 == 'Personal Goods':
        tickers = ['0333.KL','0335.KL']
        get_stock_data(tickers)
    elif options2 == 'Plantation':
        tickers = ['0189.KL']
        get_stock_data(tickers)
    elif options2 == 'Property':
        tickers = ['0308.KL']
        get_stock_data(tickers)
    elif options2 == 'Renewable Energy':
        tickers = ['0233.KL','0262.KL','0318.KL','0340.KL']
        get_stock_data(tickers)
    elif options2 == 'Retailers':
        tickers = ['0210.KL','0287.KL','0357.KL']
        get_stock_data(tickers)
    elif options2 == 'Semiconductors':
        tickers = ['0070.KL','0120.KL','0251.KL','0272.KL','0275.KL','0328.KL']
        get_stock_data(tickers)
    elif options2 == 'Software':
        tickers = ['0010.KL','0018.KL','0020.KL','0023.KL','0026.KL','0050.KL','0066.KL','0068.KL','0069.KL','0079.KL','0086.KL','0094.KL',
                '0106.KL','0107.KL','0108.KL','0119.KL','0132.KL','0152.KL','0156.KL','0174.KL','0203.KL','0236.KL','0258.KL',
                '0276.KL','0290.KL','0311.KL','0343.KL']
        get_stock_data(tickers)
    elif options2 == 'Technology Equipment':
        tickers = ['0005.KL','0036.KL','0060.KL','0085.KL','0111.KL','0112.KL','0169.KL','0181.KL','0191.KL','0209.KL','0265.KL',
                '0267.KL','0278.KL','0358.KL']
        get_stock_data(tickers)
    elif options2 == 'Telecommunications Equipment':
        tickers = ['0017.KL','0035.KL','0096.KL','0103.KL','0123.KL','0129.KL']
        get_stock_data(tickers)
    elif options2 == 'Telecom Service Providers':
        tickers = ['0092.KL','0165.KL','0195.KL']
        get_stock_data(tickers)
    elif options2 == 'Transportation & Logistics':
        tickers = ['0034.KL','0048.KL','0080.KL','0199.KL','0282.KL','0299.KL','0305.KL']
        get_stock_data(tickers)
    elif options2 == 'Travel, Leisure & Hospitality':
        tickers = ['0022.KL','0116.KL','0153.KL']
        get_stock_data(tickers)


    if 'tickers' in locals():
        df = get_stock_data(tickers)
        df_filtered = df[(df['Open'] <= invest_amount)]

        st.dataframe(
            df_filtered.sort_values(by="Current Price", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Please select a sector to load tickers.")

def etf_tickers_compare2(invest_amount, options2):

    if options2 == 'Bond Fund':
        tickers = ['0800EA.KL']
        get_stock_data(tickers)
    elif options2 == 'Commodity Fund':
        tickers = ['0828EA.KL']
        get_stock_data(tickers)
    elif options2 == 'Equity Fund':
        tickers = ['0820EA.KL','0821EA.KL','0822EA.KL','0823EA.KL','0824EA.KL',
                   '0825EA.KL','0827EA.KL','0829EA.KL','0829EB.KL','0838EA.KL','0839EA.KL']
        get_stock_data(tickers)

    if 'tickers' in locals():
        df = get_stock_data(tickers)
        df_filtered = df[(df['Open'] <= invest_amount)]

        st.dataframe(
            df_filtered.sort_values(by="Current Price", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Please select a sector to load tickers.")



def leap_tickers_compare2(invest_amount, options2):

    if options2 == 'Agricultural Products':
        tickers = ['03051.KL']
        get_stock_data(tickers)
    elif options2 == 'Building Materials':
        tickers = ['03043.KL', '03060.KL']
        get_stock_data(tickers)
    elif options2 == 'Construction':
        tickers = ['03017.KL', '03042.KL', '03050.KL']
        get_stock_data(tickers)
    elif options2 == 'Consumer Services':
        tickers = ['03015.KL', '03019.KL', '03021.KL', '03025.KL', '03053.KL', '03063.KL']
        get_stock_data(tickers)
    elif options2 == 'Digital Services':
        tickers = ['03001.KL', '03002.KL', '03008.KL', '03022.KL', '03036.KL', '03045.KL']
        get_stock_data(tickers)
    elif options2 == 'Food & Beverages':
        tickers = ['03032.KL', '03048.KL']
        get_stock_data(tickers)
    elif options2 == 'Health Care Providers':
        tickers = ['03023.KL']
        get_stock_data(tickers)
    elif options2 == 'Household Goods':
        tickers = ['03009.KL', '03012.KL', '03054.KL']
        get_stock_data(tickers)
    elif options2 == 'Industrial Materials, Components & Equipment':
        tickers = ['03027.KL', '03031.KL', '03056.KL']
        get_stock_data(tickers)
    elif options2 == 'Industrial Services':
        tickers = ['03024.KL', '03029.KL', '03033.KL', '03052.KL', '03061.KL', '03062.KL']
        get_stock_data(tickers)
    elif options2 == 'Metals':
        tickers = ['03028.KL']
        get_stock_data(tickers)
    elif options2 == 'Other Financials':
        tickers = ['03059.KL']
        get_stock_data(tickers)
    elif options2 == 'Packaging Materials':
        tickers = ['03040.KL']
        get_stock_data(tickers)
    elif options2 == 'Personal Goods':
        tickers = ['03037.KL']
        get_stock_data(tickers)
    elif options2 == 'Pharmaceuticals':
        tickers = ['03006.KL']
        get_stock_data(tickers)
    elif options2 == 'Plantation':
        tickers = ['03055.KL']
        get_stock_data(tickers)
    elif options2 == 'Semiconductors':
        tickers = ['03011.KL']
        get_stock_data(tickers)
    elif options2 == 'Software':
        tickers = ['03030.KL', '03039.KL', '03041.KL', '03046.KL', '03057.KL', '03058.KL']
        get_stock_data(tickers)



    if 'tickers' in locals():
        df = get_stock_data(tickers)
        df_filtered = df[(df['Open'] <= invest_amount)]

        st.dataframe(
            df_filtered.sort_values(by="Current Price", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Please select a sector to load tickers.")