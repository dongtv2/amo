import streamlit as st
import os
import pandas as pd
from datetime import datetime, time, timedelta
import numpy as np
import plotly.express as px # type: ignore
import plotly.graph_objs as go # type: ignore
from datetime import datetime

main_bases = ['SGN', 'HAN', 'DAD', 'CXR', 'HPH', 'VII', 'VCA', 'PQC']


def find_nightstop(df, main_bases):
    """
    Tìm những tàu nightstop và không bay trong đêm.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.
        main_bases (list): Danh sách các mainbase.

    Trả về:
        pd.DataFrame: DataFrame chứa các tàu nightstop.
    """
    # Lấy last row của mỗi REG
    last_rows = df.groupby('REG').last().reset_index()
    
    # Kiểm tra xem REG có bay trong đêm hay không
    nightstop = last_rows[last_rows['ARR'].isin(main_bases)]

    # Reset index
    nightstop.reset_index(drop=True, inplace=True)

    # Sort STA 
    nightstop.sort_values('STA')
    
    return nightstop

def calculate_crs_nightstop_times(df):
    """
    Tính toán thời gian START và END cho CRS.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.

    Trả về:
        pd.DataFrame: DataFrame chứa các cột START và END.
    """

    # Tính toán thời gian START (trước 15 phút)
    df['START'] = df['STA'] - pd.Timedelta(minutes=15)

    # Tính toán thời gian END = STD + 30 phút
    df['END'] = df['STD'] - pd.Timedelta(minutes=30)

    return df