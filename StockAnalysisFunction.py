import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st
from sklearn.ensemble import RandomForestRegressor


def scrap(sector_choice):
    market_choice = "MAIN-MKT"
    url = "https://www.bursamalaysia.com/market_information/equities_prices#"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    try:
        wait.until(EC.element_to_be_clickable((By.ID, "stock-tab"))).click()

        show_filter = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "show-filter")))
        driver.execute_script("arguments[0].scrollIntoView(true);", show_filter)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", show_filter)

        market_select_elem = wait.until(EC.presence_of_element_located((By.NAME, "board")))
        time.sleep(0.8)
        Select(market_select_elem).select_by_value(market_choice)

        sector_select_elem = wait.until(EC.presence_of_element_located((By.NAME, "sector")))
        time.sleep(0.8)
        Select(sector_select_elem).select_by_visible_text(sector_choice)

        entries_50 = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-length='50']")))
        driver.execute_script("arguments[0].click();", entries_50)
        time.sleep(1.5)

        data = []

        while True:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#DataTables_Table_0 tbody tr")))
            rows = driver.find_elements(By.CSS_SELECTOR, "#DataTables_Table_0 tbody tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = [cell.text.strip() for cell in cells]
                if row_data:
                    data.append(row_data)

            next_btn = driver.find_element(By.ID, "DataTables_Table_0_next")
            if "disabled" in next_btn.get_attribute("class"):
                break
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(1.5)

    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        driver.quit()

    headers = [
        "No", "Stock Name", "Stock Code", "REM", "Last Done", "LACP", "CHG", "%CHG",
        "Vol ('00)", "BUY Vol ('00)", "BUY", "SELL", "SELL Vol ('00)", "HIGH", "LOW"
    ]

    if not data or any(len(row) != len(headers) for row in data):
        return pd.DataFrame(columns=headers)

    df = pd.DataFrame(data, columns=headers)
    return df


def scrap_all():
    market_choice = "MAIN-MKT"
    url = "https://www.bursamalaysia.com/market_information/equities_prices#"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")

    headers = [
        "No", "Stock Name", "Stock Code", "REM", "Last Done", "LACP", "CHG", "%CHG",
        "Vol ('00)", "BUY Vol ('00)", "BUY", "SELL", "SELL Vol ('00)", "HIGH", "LOW"
    ]

    data = []

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)

        wait.until(EC.element_to_be_clickable((By.ID, "stock-tab"))).click()

        show_filter = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "show-filter")))
        driver.execute_script("arguments[0].scrollIntoView(true);", show_filter)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", show_filter)

        market_select_elem = wait.until(EC.presence_of_element_located((By.NAME, "board")))
        time.sleep(0.8)
        Select(market_select_elem).select_by_value(market_choice)

        entries_50 = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-length='50']")))
        driver.execute_script("arguments[0].click();", entries_50)
        time.sleep(1.5)

        while True:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#DataTables_Table_0 tbody tr")))
            rows = driver.find_elements(By.CSS_SELECTOR, "#DataTables_Table_0 tbody tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = [cell.text.strip() for cell in cells]
                if row_data:
                    data.append(row_data)

            next_btn = driver.find_element(By.ID, "DataTables_Table_0_next")
            if "disabled" in next_btn.get_attribute("class"):
                break
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(1.5)

    except Exception as e:
        print(f"Error in scrap_all(): {e}")

    finally:
        driver.quit()

    if not data or any(len(row) != len(headers) for row in data):
        return pd.DataFrame(columns=headers)

    df = pd.DataFrame(data, columns=headers)
    return df





def show_BT(options):
    table = scrap(options)

    search_stock = st.text_input("Search for a stock listing:", "",key='s10').strip()
    if search_stock:
        table = table[table.iloc[:, 1].str.contains(search_stock, case=False, na=False)]
    st.dataframe(table, hide_index=True)  

def show_all():
    table2 = scrap_all()

    search_stock2 = st.text_input("Search for a stock listing:", "",key='s12').strip()
    if search_stock2:
        table2 = table2[table2.iloc[:, 1].str.contains(search_stock2, case=False, na=False)]
    st.dataframe(table2, hide_index=True)  


def clean_column(options):
    return (
        options.astype(str)
        .str.replace(',', '', regex=False)
        .str.extract(r'(\d+\.?\d*)')[0]
        .astype(float)
    )

def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def predict(options, invest_amount):
    table = scrap(options)

    for col in ['BUY', '%CHG', 'CHG', 'SELL', 'HIGH', 'LOW', "Vol ('00)"]:
        table[col] = clean_column(table[col])

    filtered_df = table[(table['BUY'] >= 0) & (table['BUY'] <= invest_amount)].copy()

    features = ['%CHG', 'CHG', "Vol ('00)"]
    targets = ['BUY', 'SELL', 'HIGH', 'LOW']
    filtered_df.dropna(subset=features + targets, inplace=True)

    if filtered_df.empty:
        st.warning("No data available after filtering. Adjust your criteria.")
        return


    for target in targets:
        model = RandomForestRegressor()
        model.fit(filtered_df[features], filtered_df[target])
        filtered_df[f"{target} Predicted"] = model.predict(filtered_df[features])

    spread = (filtered_df['SELL Predicted'] - filtered_df['BUY Predicted']) / filtered_df['BUY Predicted']
    range_ratio = (filtered_df['HIGH Predicted'] - filtered_df['LOW Predicted']) / filtered_df['LOW Predicted']
    volume_scaled = normalize(filtered_df["Vol ('00)"])

    filtered_df['Composite Score'] = (
        0.5 * spread.fillna(0) +
        0.3 * range_ratio.fillna(0) +
        0.2 * volume_scaled.fillna(0)
    )

    filtered_df.insert(0, 'Rank', range(1, 1 + len(filtered_df)))
    st.subheader("Top 10 Best Stock Based On Composite Score")
    st.dataframe(filtered_df.iloc[:10, :], hide_index=True)

def predict2(col2_options, invest_amount):
    table2 = scrap(col2_options)

    for col in ['BUY', '%CHG', 'CHG', 'SELL', 'HIGH', 'LOW', "Vol ('00)"]:
        table2[col] = clean_column(table2[col])

    filtered_df2 = table2[(table2['BUY'] >= 0) & (table2['BUY'] <= invest_amount)].copy()

    features = ['%CHG', 'CHG', "Vol ('00)"]
    targets = ['BUY', 'SELL', 'HIGH', 'LOW']
    filtered_df2.dropna(subset=features + targets, inplace=True)

    if filtered_df2.empty:
        st.warning("No data available after filtering. Adjust your criteria.")
        return

    for target in targets:
        model = RandomForestRegressor()
        model.fit(filtered_df2[features], filtered_df2[target])
        filtered_df2[f"{target} Predicted"] = model.predict(filtered_df2[features])

    spread = (filtered_df2['SELL Predicted'] - filtered_df2['BUY Predicted']) / filtered_df2['BUY Predicted']
    range_ratio = (filtered_df2['HIGH Predicted'] - filtered_df2['LOW Predicted']) / filtered_df2['LOW Predicted']
    volume_scaled = normalize(filtered_df2["Vol ('00)"])

    filtered_df2['Composite Score'] = (
        0.5 * spread.fillna(0) +
        0.3 * range_ratio.fillna(0) +
        0.2 * volume_scaled.fillna(0)
    )

    filtered_df2.sort_values('Composite Score', ascending=False, inplace=True)
    filtered_df2.insert(0, 'Rank', range(1, 1 + len(filtered_df2)))
    st.subheader("Top 10 Best Stock Based On Composite Score")
    st.dataframe(filtered_df2.iloc[:10, :], hide_index=True)

def predict_all2(invest_amount):
    table2 = scrap_all()

    for col in ['BUY', '%CHG', 'CHG', 'SELL', 'HIGH', 'LOW', "Vol ('00)"]:
        table2[col] = clean_column(table2[col])

    filtered_df2 = table2[(table2['BUY'] >= 0) & (table2['BUY'] <= invest_amount)].copy()

    features = ['%CHG', 'CHG', "Vol ('00)"]
    targets = ['BUY', 'SELL', 'HIGH', 'LOW']
    filtered_df2.dropna(subset=features + targets, inplace=True)

    if filtered_df2.empty:
        st.warning("No data available after filtering. Adjust your criteria.")
        return

    for target in targets:
        model = RandomForestRegressor()
        model.fit(filtered_df2[features], filtered_df2[target])
        filtered_df2[f"{target} Predicted"] = model.predict(filtered_df2[features])

    spread = (filtered_df2['SELL Predicted'] - filtered_df2['BUY Predicted']) / filtered_df2['BUY Predicted']
    range_ratio = (filtered_df2['HIGH Predicted'] - filtered_df2['LOW Predicted']) / filtered_df2['LOW Predicted']
    volume_scaled = normalize(filtered_df2["Vol ('00)"])

    filtered_df2['Composite Score'] = (
        0.5 * spread.fillna(0) +
        0.3 * range_ratio.fillna(0) +
        0.2 * volume_scaled.fillna(0)
    )

    filtered_df2.sort_values('Composite Score', ascending=False, inplace=True)
    filtered_df2.insert(0, 'Rank', range(1, 1 + len(filtered_df2)))
    st.subheader("Top 10 Best Stock Based On Composite Score ")
    st.dataframe(filtered_df2.iloc[:10, :], hide_index=True)

def predict_all(invest_amount):
    table = scrap_all()

    for col in ['BUY', '%CHG', 'CHG', 'SELL', 'HIGH', 'LOW', "Vol ('00)"]:
        table[col] = clean_column(table[col])

    filtered_df = table[(table['BUY'] >= 0) & (table['BUY'] <= invest_amount)].copy()

    features = ['%CHG', 'CHG', "Vol ('00)"]
    targets = ['BUY', 'SELL', 'HIGH', 'LOW']
    filtered_df.dropna(subset=features + targets, inplace=True)

    if filtered_df.empty:
        st.warning("No data available after filtering. Adjust your criteria.")
        return

    for target in targets:
        model = RandomForestRegressor()
        model.fit(filtered_df[features], filtered_df[target])
        filtered_df[f"{target} Predicted"] = model.predict(filtered_df[features])

    spread = (filtered_df['SELL Predicted'] - filtered_df['BUY Predicted']) / filtered_df['BUY Predicted']
    range_ratio = (filtered_df['HIGH Predicted'] - filtered_df['LOW Predicted']) / filtered_df['LOW Predicted']
    volume_scaled = normalize(filtered_df["Vol ('00)"])

    filtered_df['Composite Score'] = (
        0.5 * spread.fillna(0) +
        0.3 * range_ratio.fillna(0) +
        0.2 * volume_scaled.fillna(0)
    )

    filtered_df.sort_values('Composite Score', ascending=False, inplace=True)
    filtered_df.insert(0, 'Rank', range(1, 1 + len(filtered_df)))
    st.subheader("Top 10 Best Stock Based On Composite Score")
    st.dataframe(filtered_df.iloc[:10, :], hide_index=True)