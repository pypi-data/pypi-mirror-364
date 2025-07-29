from datetime import datetime
from pathlib import Path
from typing import Annotated
import fnmatch

import pandas as pd
import geopandas as gpd
from geojson import Feature, Point
from fastapi import APIRouter, Request, Query, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.datastructures import URL

from sageodata_db import connect as connect_to_sageodata
from sageodata_db import load_predefined_query
from sageodata_db.utils import parse_query_metadata

import dew_gwdata as gd
from dew_gwdata.sageodata_datamart import get_sageodata_datamart_connection
import ausweather

from dew_gwdata.webapp import utils as webapp_utils
from dew_gwdata.webapp import query_models


router = APIRouter(prefix="/app", include_in_schema=False)

templates_path = Path(__file__).parent.parent / "templates"

templates = Jinja2Templates(directory=templates_path)


@router.get("/rainfall_stations")
def rainfall_stations(
    request: Request,
    query: Annotated[query_models.RainfallStations, Depends()],
):
    df, title, query_params = query.find_stations()

    if len(df) == 1:
        return RedirectResponse(f"/app/rainfall_station?{query_params}")

    title_series = df.apply(
        lambda row: (
            f'<nobr><a href="/app/rainfall_station?station_id={row.station_id}">'
            f"{row.station_id}</a></nobr>"
        ),
        axis=1,
    )
    df.insert(0, "title", title_series)

    gdf = gpd.GeoDataFrame(
        df[["station_id"]],
        geometry=gpd.points_from_xy(df["lon"], df["lat"], crs="epsg:7844"),
    )
    gdf["suburb"] = gd.locate_points_in_suburbs(gdf)
    df2 = pd.merge(df, gdf, on="station_id", how="left")

    cols = [
            "title",
            "station_id",
            "suburb",
            "station_name",
            "distance_km",
            "start",
            "end",
            "current",
            "total_span_yrs",
            "aws",
            "state",
        ]
    if not "distance_km" in df2:
        cols = [c for c in cols if not c == "distance_km"]
    else:
        df2["distance_km"] = df2.distance_km.round(1)
    df2 = df2[cols]
    df2["total_span_yrs"] = df2.total_span_yrs.round(0).astype(int)
    df2.loc[df2.current == False, "current"] = ""
    df2.loc[df2.aws == False, "aws"] = ""

    table = webapp_utils.frame_to_html(df2)

    return templates.TemplateResponse(
        "rainfall_stations.html",
        {
            "request": request,
            # "redirect_to": "group_summary",
            # "singular_redirect_to": "well_summary",
            # "plural_redirect_to": "wells_summary",
            "query": query,
            "df": df2,
            "table": table,
        },
    )


@router.get("/rainfall_station")
def rainfall_station(
    request: Request,
    query: Annotated[query_models.RainfallStations, Depends()],
    avg_pd_start: str = "",
    avg_pd_end: str = "",
    fetch_from_silo: bool = False,
):
    df, title, query_params = query.find_stations()

    try:
        avg_pd_start = int(avg_pd_start)
    except:
        pass
    try:
        avg_pd_end = int(avg_pd_end)
    except:
        pass

    if len(df) != 1:
        return RedirectResponse(f"/app/rainfall_stations?{query_params}")

    site = df.iloc[0]

    app_db = webapp_utils.open_db()
    rf0 = webapp_utils.load_rainfall_from_db(site.station_id, app_db)
    currency = datetime.now() - rf0.daily.date_added.max()

    if len(rf0.daily) == 0:
        fetch_from_silo = True
    elif pd.isnull(rf0.daily.date.max()):
        fetch_from_silo = True
    elif currency > pd.Timedelta(days=30):
        fetch_from_silo = True
    else:
        fetch_from_silo = fetch_from_silo
    if fetch_from_silo:
        rf1 = ausweather.RainfallStationData.from_bom_via_silo(
            site.station_id,
            "groundwater@sa.gov.au",
            clip_ends=False,
            data_end=pd.Timestamp(datetime.now()),
        )
        webapp_utils.write_daily_rainfall_to_db(site.station_id, rf1.daily, app_db)
        rf = webapp_utils.load_rainfall_from_db(site.station_id, app_db)
        message = "Data fetched live from SILO Patched Point Data website."
    else:
        rf = webapp_utils.load_rainfall_from_db(site.station_id, app_db)
        message = f"Data fetched from local database cache as it has been updated in the last 30 days (last data point is {currency} ago)"

    st = ausweather.annual_stats(
        rf.calendar, avg_pd_start=avg_pd_start, avg_pd_end=avg_pd_end
    )
    st = {
        k: v
        for k, v in st.items()
        if k in ["min", "pct5", "pct25", "mean", "median", "pct75", "pct95", "max"]
    }
    st = pd.Series(st)[
        ["min", "pct5", "pct25", "mean", "median", "pct75", "pct95", "max"]
    ].round(decimals=1)

    app_db.close()

    annual = (
        rf.daily.groupby(["year", "interpolated_desc"])
        .rainfall.sum()
        .unstack(level=1)
        .fillna(0)
        .reset_index()
    )
    print(f"annual:\n{annual}")

    cols_for_record = [
        "year",
        "total",
        "observed",
        "deaccumulated",
        "interpolated",
        "mean",
        "pct5",
        "pct95",
    ]
    annual["mean"] = st["mean"]
    annual["pct5"] = st["pct5"]
    annual["pct95"] = st["pct95"]
    for col in cols_for_record:
        if not col in annual:
            annual[col] = 0
    annual["total"] = annual.observed + annual.deaccumulated + annual.interpolated

    chart_rows = []
    for idx, record in annual.iterrows():
        record = record.to_dict()
        row_values = [webapp_utils.fmt_for_js(record[col]) for col in cols_for_record]
        row = "[" + ", ".join(row_values) + "]"
        chart_rows.append(row)
    calendar_js_dataset = ",\n ".join(chart_rows)

    site_table = webapp_utils.series_to_html(site, transpose=False)
    st_table = webapp_utils.series_to_html(st, transpose=False)

    return templates.TemplateResponse(
        "rainfall_station.html",
        {
            "request": request,
            "title": f"{site.station_id}: {site.station_name}",
            "message": message,
            "query": query,
            # "redirect_to": "group_summary",
            # "singular_redirect_to": "well_summary",
            # "plural_redirect_to": "wells_summary",
            "site": site,
            "stats": st,
            "stats_table": st_table,
            "site_table": site_table,
            "calendar_js_dataset": calendar_js_dataset,
            "avg_pd_start": avg_pd_start,
            "avg_pd_end": avg_pd_end,
            "avg_pd_start_label": avg_pd_start
            if avg_pd_start
            else rf.calendar.year.min(),
            "avg_pd_end_label": avg_pd_end if avg_pd_end else rf.calendar.year.max(),
        },
    )
