import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from db_utils.fetch_utils import  fetch_user_projects_views


def dashboard():
    if st.button("🔄Refresh dashboard"):
        df = pd.DataFrame(fetch_user_projects_views()).sort_values("Full name")
    else:
        df = pd.DataFrame(fetch_user_projects_views()).sort_values("Full name")

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(filter=True, sortable=True, resizable=True, enableRowGroup=True,)

    grid_options = gb.build()

    AgGrid(df, gridOptions=grid_options, height=500, fit_columns_on_grid_load=True, enable_enterprise_modules=True)
