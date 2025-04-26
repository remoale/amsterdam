import pandas as pd
import plotly.express as px
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype
)

# Display title
st.title("Airbnb Amsterdam")

# Read dataframe
dataframe = pd.read_csv(
    "data/WK1_Airbnb_Amsterdam_listings_proj_solution.csv",
    names=[
        "Airbnb Listing ID",
        "Price",
        "Latitude",
        "Longitude",
        "Meters from chosen location",
        "Location",
    ],
)

# We have a limited budget, therefore we would like to exclude
# listings with a price above 100 pounds per night
dataframe = dataframe[dataframe["Price"] <= 100]

# Display as integer
dataframe["Airbnb Listing ID"] = dataframe["Airbnb Listing ID"].astype(int)
# Round of values
dataframe["Price"] = "€ " + dataframe["Price"].round(2).astype(str)
# Rename the number to a string
dataframe["Location"] = dataframe["Location"].replace(
    {1.0: "To visit", 0.0: "Airbnb listing"}
)

# Display map
st.subheader("Explore")

# Display text
st.write("Dam Square (52.3731° N, 4.8939° E) is the historic heart of Amsterdam, Netherlands and serves as the central reference point on the map.")

# Create the plotly express figure
fig = px.scatter_map(
    dataframe,
    lat="Latitude",
    lon="Longitude",
    color="Location",
    zoom=11,
    height=500,
    width=800,
    hover_name="Price",
    hover_data=["Meters from chosen location", "Location"],
    labels={"color": "Locations"},
)
fig.update_geos(center=dict(lat=dataframe.iloc[0]["Latitude"], lon=dataframe.iloc[0]["Longitude"]))

# Show the figure
st.plotly_chart(fig, use_container_width=True)

# Display dataframe
st.subheader("Listings")

# Display text
st.write("900+ listings under €100 per night.")

# Display dataframe
st.dataframe(dataframe)

# Filter dataframe
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns
    Args:
        df (pd.DataFrame): Original dataframe
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                # Specify format parameter to avoid the warning
                df[col] = pd.to_datetime(df[col], format='mixed')
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df

# Display text
st.write("2000+ hosting sources with house-specific attributes.")

# Display filtered dataframe
df = pd.read_csv(
    "data/WK2_Airbnb_Amsterdam_listings_proj_solution.csv", index_col=0
)
st.dataframe(filter_dataframe(df))
