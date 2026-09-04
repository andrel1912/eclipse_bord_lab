import streamlit as st
import pandas as pd
import httpx
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.title("eClipseBord")

response = httpx.get(f"{BACKEND_URL}/data", timeout=30)

if response.status_code == 200:

    df = pd.DataFrame(response.json())

    df["Eclipse Magnitude"] = pd.to_numeric(
        df["Eclipse Magnitude"], errors="coerce"
    )

    df["Year"] = pd.to_numeric(
        df["Calendar Date"].astype(str).str.extract(r"(-?\d+)")[0],
        errors="coerce"
    )

    st.header("Explore Solar Eclipses")

    col1, col2 = st.columns(2)

    with col1:
        eclipse_types = st.multiselect(
            "Eclipse type",
            sorted(df["Eclipse Type"].dropna().unique())
        )

    with col2:
        year_range = st.slider(
            "Year range",
            int(df["Year"].min()),
            int(df["Year"].max()),
            (2000, 2026),
            key="year_filter"
        )

    filtered_df = df[df["Year"].between(*year_range)]

    if eclipse_types:
        filtered_df = filtered_df[
            filtered_df["Eclipse Type"].isin(eclipse_types)
        ]

    st.write(f"{len(filtered_df):,} eclipses found")

    st.header("Eclipse frequency")

    yearly = filtered_df.groupby("Year").size()

    st.line_chart(yearly)

    st.header("Next Solar Eclipse")

    future = filtered_df.copy()
    future["Date"] = pd.to_datetime(
        future["Calendar Date"],
        format="%Y %B %d",
        errors="coerce"
    )

    future = future[
        future["Date"] >= pd.Timestamp.today()
    ].sort_values("Date")

    if not future.empty:
        eclipse = future.iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric("Date", eclipse["Date"].strftime("%d %b %Y"))
        col2.metric("Type", eclipse["Eclipse Type"])
        col3.metric("Magnitude", f"{eclipse['Eclipse Magnitude']:.3f}")

    st.header("Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total eclipses", f"{len(df):,}")
    col2.metric("Filtered eclipses", f"{len(filtered_df):,}")
    col3.metric("Eclipse types", filtered_df["Eclipse Type"].nunique())

    st.subheader("Eclipse locations")

    map_df = filtered_df[
        ["Latitude", "Longitude", "Eclipse Magnitude"]
    ].dropna().copy()

    map_df["lat"] = map_df["Latitude"].apply(
        lambda x: float(str(x)[:-1])
        if str(x)[-1] in ["N", "S"] else None
    )

    map_df["lon"] = map_df["Longitude"].apply(
        lambda x: float(str(x)[:-1])
        if str(x)[-1] in ["E", "W"] else None
    )

    map_df.loc[
        map_df["Latitude"].astype(str).str.endswith("S"), "lat"
    ] *= -1

    map_df.loc[
        map_df["Longitude"].astype(str).str.endswith("W"), "lon"
    ] *= -1

    map_df["size"] = map_df["Eclipse Magnitude"].clip(lower=0.1) * 3

    st.map(
        map_df[["lat", "lon", "size"]],
        latitude="lat",
        longitude="lon",
        size="size"
    )

    st.subheader("Eclipse data")

    columns = [
        "Catalog Number",
        "Calendar Date",
        "Eclipse Time",
        "Eclipse Type",
        "Eclipse Magnitude",
        "Latitude",
        "Longitude",
        "Central Duration"
    ]

    st.dataframe(
        filtered_df[columns],
        use_container_width=True,
        hide_index=True
    )

else:
    st.error("Could not connect to the backend.")