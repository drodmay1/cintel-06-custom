from pathlib import Path
import cufflinks as cf
import pandas as pd
import yfinance as yf
from faicons import icon_svg
from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import output_ui
from shinywidgets import render_plotly
from stocks import stocks

# Default to the last month
end = pd.Timestamp.now()
start = end - pd.Timedelta(weeks=4)

ui.page_opts(title="Apple AAPL Stock Explorer", fillable=True)
selected_stock = "AAPL" #default selected stock

with ui.sidebar():
    # Search input
    ui.input_text("search", "Search Stock e.g. AAPL", placeholder="Enter stock symbol")
    ui.input_selectize("ticker", "Select Stocks", choices=stocks, selected="AAPL")
    ui.input_date_range("dates", "Select dates", start=start, end=end)
    ui.input_numeric("quantity", "Quantity", min=1, max=100, step=1, value=1)


with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=icon_svg("dollar-sign")):
        "Current Price"

        @render.ui
        def price():
            close = get_data()["Close"]
            return f"{close.iloc[-1]:.2f}"

    with ui.value_box(showcase=output_ui("change_icon")):
        "Change"

        @render.ui
        def change():
            return f"${get_change():.2f}"

    with ui.value_box(showcase=icon_svg("percent")):
        "Percent Change"

        @render.ui
        def change_percent():
            return f"{get_change_percent():.2f}%"


with ui.layout_columns(col_widths=[9, 3]):
    with ui.card(full_screen=True):
        ui.card_header("Price history")

        @render_plotly
        def price_history():
            qf = cf.QuantFig(
                get_data(),
                name=input.ticker(),
                up_color="#44bb70",
                down_color="#040548",
                legend="top",
            )
            qf.add_sma()
            qf.add_volume(up_color="#44bb70", down_color="#040548")
            fig = qf.figure()
            fig.update_layout(
                hovermode="x unified",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            return fig

    with ui.card():
        ui.card_header("Latest data")

        @render.data_frame
        def latest_data():
            x = get_data()[:1].T.reset_index()
            x.columns = ["Category", "Value"]
            x["Value"] = x["Value"].apply(lambda v: f"{v:.1f}")
            return x
        
    with ui.card():
        ui.card_header(icon_svg("chart-line"), "Total Value")

        @render.ui
        def total_value():
            data = get_data()
            quantity = input.quantity()
            if data.empty or quantity is None:
                return "N/A"
            else:
                close_price = data["Close"].iloc[-1]
                return f"${close_price * quantity:.2f}"


ui.include_css(Path(__file__).parent / "styles.css")

# Reactive calculations

@reactive.calc
def get_ticker():
    return yf.Ticker(selected_stock)

@reactive.calc
def get_data():
    dates = input.dates()
    return get_ticker().history(start=dates[0], end=dates[1])


@reactive.calc
def get_change():
    close = get_data()["Close"]
    return close.iloc[-1] - close.iloc[-2]


@reactive.calc
def get_change_percent():
    close = get_data()["Close"]
    change = close.iloc[-1] - close.iloc[-2]
    return change / close.iloc[-2] * 100

@reactive.calc
def update_selected_stock():
    search_input = input.search()  # Get the value from the search input
    if search_input:
        return search_input.upper()  # Update the selected stock with the search input
    else:
        return input.ticker()  # Use the selected stock from the dropdown if search input is empty
    

with ui.hold():

    @render.ui
    def change_icon():
        change = get_change()
        icon = icon_svg("arrow-up" if change >= 0 else "arrow-down")
        icon.add_class(f"text-{('success' if change >= 0 else 'danger')}")
        return icon