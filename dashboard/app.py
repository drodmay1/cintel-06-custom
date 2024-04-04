from pathlib import Path
import pandas as pd
from faicons import icon_svg
from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import output_ui
from shinywidgets import render_plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Import stocks dictionary from stocks.py
from stocks import stocks

# Default to the last month
end = pd.Timestamp.now()
start = end - pd.Timedelta(weeks=4)

# AAPL as default selected stock
selected_stock = "AAPL"

# Function to get data for selected stock
@reactive.calc
def get_data():
    dates = input.dates()
    date_range = pd.date_range(start=dates[0], end=dates[1], periods=20)  # Ensure 20 dates are generated

    # Adjusted volume values
    volume_values = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145]

    # Construct DataFrame with same length arrays
    return pd.DataFrame({'Date': date_range, 
                         'Open': [100, 102, 105, 103, 104, 105, 106, 107, 108, 109, 100, 115, 118, 120, 124, 140, 141, 143, 145, 150],
                         'High': [105, 107, 108, 109, 110, 115, 118, 120, 124, 140, 141, 143, 145, 150, 153, 157, 160, 165, 189, 190],
                         'Low': [99, 101, 103, 102, 103, 104, 105, 106, 107, 108, 109, 100, 115, 118, 120, 124, 140, 141, 143, 145],
                         'Close': [103, 105, 107, 109, 100, 102, 105, 103, 104, 105, 106, 107, 108, 109, 100, 157, 160, 165, 189,194],
                         'Volume': volume_values}).set_index('Date')

# UI
ui.page_opts(title="Apple AAPL Stock Explorer", fillable=True)

with ui.sidebar():
    # Search input
    ui.input_date_range("dates", "Select dates", start=start, end=end)
    ui.input_numeric("quantity", "Quantity", min=1, max=100, step=1, value=1)

    # Links and newsfeed section
    ui.h6("Newsfeed and links:")
    ui.a(
        "APPL Google Financial today",
        href="https://www.google.com/search?sca_esv=f16471168e6fc9b9&sca_upv=1&rlz=1C5CHFA_enUS748US748&sxsrf=ACQVn0_zAqWeiIBc3fzp9NY3AiSMHIloog:1712106682380&q=google+finance+AAPL&sa=X&ved=2ahUKEwiaiPu07qSFAxULElkFHQ3ODS0Q7xYoAHoECAkQAg&biw=1598&bih=788&dpr=1",
        style="color: #007bff;",  # Blue color for links
        target="_blank",
    )

    ui.a(
        "APPL Bloomberg",
        href="https://www.bloomberg.com/news/articles/2024-04-02/apple-flirts-with-support-levels-after-worst-quarter-in-a-decade?embedded-checkout=true",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
    ui.a(
        "APPL Yahoo Finance Today",
        href="https://finance.yahoo.com/quote/AAPL/",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )

    ui.a(
        "GitHub Source",
        href="https://github.com/drodmay1/cintel-06-custom",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
    
    ui.a(
        "GitHub App",
        href="https://github.com/drodmay1/cintel-06-custom/blob/main/dashboard/app.py",
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
    ui.a(
        "PyShiny", 
        href="https://shiny.posit.co/py/", 
        target="_blank",
        style="color: #007bff;",  # Blue color for links
    )
   
with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=icon_svg("dollar-sign")):
        "Current Price"

        @render.ui
        def price():
            data = get_data()
            if not data.empty:
                close = data["Close"]
                return f"{close.iloc[-1]:.2f}"
            else:
                return "N/A"

    with ui.value_box(showcase=output_ui("change_icon")):
        "Change"

        @render.ui
        def change():
            change = get_change()
            if change is not None:
                return f"${change:.2f}"
            else:
                return "N/A"

    with ui.value_box(showcase=icon_svg("percent")):
        "Percent Change"

        @render.ui
        def change_percent():
            change_percent = get_change_percent()
            if change_percent is not None:
                return f"{change_percent:.2f}%"
            else:
                return "N/A"
        
    with ui.value_box(showcase=icon_svg("coins")):
        "Total Value"

        @render.ui
        def total_value():
            data = get_data()
            quantity = input.quantity()
            if not data.empty and quantity is not None:
                close_price = data["Close"].iloc[-1]
                return f"${close_price * quantity:.2f}"
            else:
                return "N/A"
            
        ui.include_css(Path(__file__).parent / "styles.css")


with ui.layout_columns(col_widths=[9, 3]):
    with ui.card(full_screen=True):
        ui.card_header("Price history and volume")

        @render_plotly
        def price_and_volume():
            data = get_data()

            # Check if data is not empty
            if not data.empty:
                # Create a new plotly figure
                fig = go.Figure()

                # Add candlestick trace
                fig.add_trace(
                    go.Candlestick(x=data.index,
                                   open=data['Open'],
                                   high=data['High'],
                                   low=data['Low'],
                                   close=data['Close'],
                                   increasing_line_color='rgba(0,128,0,0.7)',
                                   decreasing_line_color='rgba(255,0,0,0.7)',
                                   name="Candlestick")
                )

                # Add volume trace as a bar chart
                fig.add_trace(
                    go.Bar(x=data.index, y=data['Volume'], name="Volume", marker_color='rgba(31,119,180,0.5)')  
                    # Adjust marker_color as needed
                )

                # Update layout
                fig.update_layout(
                    title="Price History and Volume",
                xaxis=dict(title="Date"),
                hovermode="x unified",
                paper_bgcolor='rgba(255,255,255,0.8)',
                plot_bgcolor='rgba(255,255,255,0.8)',
                )

                return fig
    
    with ui.card():
        ui.card_header("Latest data")

        @render.data_frame
        def latest_data():
            data = get_data()
            if not data.empty:
                x = data[:1].T.reset_index()
                x.columns = ["Category", "Value"]
                x["Value"] = x["Value"].apply(lambda v: f"{v:.1f}")
                return x
            else:
                return None

# Reactive calculations
@reactive.calc
def get_change():
    data = get_data()
    if not data.empty:
        close = data["Close"]
        return close.iloc[-1] - close.iloc[-2]
    else:
        return None

@reactive.calc
def get_change_percent():
    data = get_data()
    if not data.empty:
        close = data["Close"]
        change = close.iloc[-1] - close.iloc[-2]
        return change / close.iloc[-2] * 100
    else:
        return None

with ui.hold():

    @render.ui
    def change_icon():
        change = get_change()
        if change is not None:
            icon = icon_svg("arrow-up" if change >= 0 else "arrow-down")
            icon.add_class(f"text-{('success' if change >= 0 else 'danger')}")
            return icon
        else:
            return None