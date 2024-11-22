import streamlit as st
import pandas as pd
import numpy as np
import os


from Functions.flightplan_process import *
from Functions.preflight_process import *
from Functions.transit_process import *
from Functions.nighstop import *
from Functions.charts import *
from Functions.or_tool_mpwr import *

os.environ['STREAMLIT_DEBUG'] = 'true'
# Config pages
st.set_page_config(
    page_title="MPWR APPs",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title('MPWR APPs for AMO')

tabs = st.tabs(['Read Flight Plan', 'Flight Plan Cleaned', 'Preflight', 'Transit', 'NightStop', 'Visualization', 'OR-TOOLS'])

with tabs[0]:
    st.write('Read flightplan')
    try:
        col1, col2 = st.columns(2)

        with col1:
            st.write('Please upload a flightplan day 1')
            uploaded_file_day1 = st.file_uploader("Choose a file", key='uploadfile_1')
            df_day1 = pd.read_excel(uploaded_file_day1) if uploaded_file_day1 else None
            st.write("File uploaded" if df_day1 is not None else 'Please upload a file')

        with col2:
            st.write('Please upload a flightplan day 2')
            uploaded_file_day2 = st.file_uploader("Choose a file", key='uploadfile_2')
            df_day2 = pd.read_excel(uploaded_file_day2) if uploaded_file_day2 else None
            st.write("File uploaded" if df_day2 is not None else 'Please upload a file')
    except Exception as e:
        st.error(e)
with tabs[1]:
    st.write('Flight Plan Cleaned')
    try:
        col1, col2 = st.columns(2)

        with col1:
            st.write('Flight Plan Day 1')
            if df_day1 is not None:
                with st.expander('Click to see the flight data day 1'):
                    df_day1 = clean_dataframe(df_day1)
                    df_day1 = adjust_sta_std_datetime(df_day1)
                    st.write(df_day1)
                with st.expander('Click to see the combined flight data day 1'):
                    st.write("Dữ liệu nối dòng")
                    df_day1_combined = combine_flights(df_day1)
                    st.write(df_day1_combined)
            else:
                st.write('No file uploaded for day 1')

        with col2:
            st.write('Flight Plan Day 2')
            if df_day2 is not None:
                with st.expander('Click to see the flight data day 2'):
                    df_day2 = clean_dataframe(df_day2)
                    df_day2 = adjust_sta_std_datetime(df_day2)
                    st.write(df_day2)
                with st.expander('Click to see the combined flight data day 2'):
                    df_day2_combined = combine_flights(df_day2)
                    st.write(df_day2_combined)
            else:
                st.write('No file uploaded for day 2')
    except Exception as e:
        st.error(e)
with tabs[2]:
    st.write('Preflight')
    try:
        with st.expander('Get all Preflight in SGN'):
            df_day1_preflight_sgn = get_all_REG_preflight(df_day1_combined, ['SGN']) if df_day1_combined is not None else None
            st.write(df_day1_preflight_sgn)

        with st.expander('CRS START - END Preflight in SGN'):
            if df_day1_preflight_sgn is not None:
                df_day1_preflight_sgn_START_END = calculate_preflight_crs_times(df_day1_preflight_sgn)
                columns_to_drop = ['Route', 'FLT_1', 'AC', 'DEP_1', 'ARR_1', 'ARR_2', 'STA_1', 'FLT_2', 'DEP_2', 'STD_2', 'STA_2']
                df_day1_preflight_sgn_START_END.drop(columns=columns_to_drop, errors='ignore', inplace=True)
                df_day1_preflight_sgn_START_END.rename(columns={'STD_1': 'STD'}, inplace=True)
                new_column_order = ['REG', 'DATE', 'START_SHIFT', 'STD', 'START', 'END']
                df_day1_preflight_sgn_START_END = df_day1_preflight_sgn_START_END[new_column_order]
                st.write(df_day1_preflight_sgn_START_END)

        with st.expander('Vẽ sơ đồ biểu diễn chuyến bay đầu ngày ở SGN'):
            if df_day1_preflight_sgn_START_END is not None:
                fig_preflight = plot_flight_density(df_day1_preflight_sgn_START_END)

        with st.expander("Vẽ các chuyến overlap"):
            if df_day1_preflight_sgn_START_END is not None:
                visualize_overlap(df_day1_preflight_sgn_START_END)

        with st.expander('Gant chart preflught'):
            if df_day1_preflight_sgn_START_END is not None:
                gantt_chart(df_day1_preflight_sgn_START_END)
    except Exception as e:
        st.error(e)
with tabs[3]:
    st.write('Transit')
    try:
        with st.expander("Get all transit flight in SGN"):
            df_d1_transit_sgn = filter_transit_flights_at_sgn(df_day1_combined) if df_day1_combined is not None else None
            st.write(df_d1_transit_sgn)

        with st.expander('CRS START - END Trasit in SGN'):
            if df_d1_transit_sgn is not None:
                df_d1_transit_sgn_START_END = calculate_crs_transit_times(df_d1_transit_sgn)
                columns_to_drop = ['Route', 'FLT_1', 'AC', 'DEP_1', 'ARR_1', 'ARR_2', 'STD_1', 'FLT_2', 'DEP_2', 'STA_2']
                df_d1_transit_sgn_START_END.drop(columns=columns_to_drop, errors='ignore', inplace=True)
                df_d1_transit_sgn_START_END.rename(columns={'STD_2': 'STD', 'STA_1': 'STA'}, inplace=True)
                df_d1_transit_sgn_START_END.sort_values('STA', inplace=True)
                st.write(df_d1_transit_sgn_START_END)

        with st.expander('Biểu đò phân bổ các chuyến bay transit'):
            if df_d1_transit_sgn_START_END is not None:
                plot_flight_density(df_d1_transit_sgn_START_END)

        with st.expander('Biểu overlap'):
            if df_d1_transit_sgn_START_END is not None:
                visualize_overlap(df_d1_transit_sgn_START_END)

        with st.expander('Gant Chart - Transit'):
            if df_d1_transit_sgn_START_END is not None:
                gantt_chart(df_d1_transit_sgn_START_END)
    except Exception as e:
        st.error(e)
with tabs[4]:
    st.write('Nightstop')
    try:
        with st.expander('Nightstop - DAY 1'):
            df_d1_nightstop_sgn = find_nightstop(df_day1, ['SGN']) if df_day1 is not None else None
            st.write(df_d1_nightstop_sgn)

        with st.expander('Preflight - Day 2'):
            df_day2_preflight_sgn = get_all_REG_preflight(df_day2_combined, ['SGN']) if df_day2_combined is not None else None
            if df_day2_preflight_sgn is not None:
                columns_to_drop = ['Route', 'FLT_1', 'AC', 'DEP_1', 'STA_1', 'STD_2', 'ARR_1', 'ARR_2', 'FLT_2', 'DEP_2', 'STA_2']
                df_day2_preflight_sgn.drop(columns=columns_to_drop, errors='ignore', inplace=True)
                df_joined = df_d1_nightstop_sgn.merge(df_day2_preflight_sgn, on='REG', how='left')
                columns_to_drop_dfjoined = ['Route', 'FLT', 'AC', 'DEP', 'STD', 'ARR', 'ARR_2', 'DATE_y']
                df_joined.drop(columns=columns_to_drop_dfjoined, errors='ignore', inplace=True)
                df_joined.rename(columns={'DATE_x': 'DATE', 'STD_1': 'STD'}, inplace=True)
                st.write(df_joined)

        with st.expander('Tính START END của CRS tàu nightstop'):
            if df_joined is not None:
                df_d1_nightstop_sgn_START_END = calculate_crs_nightstop_times(df_joined)
                st.write(df_d1_nightstop_sgn_START_END)

        with st.expander('Biểu đò phân bổ các chuyến nighstop'):
            if df_d1_nightstop_sgn_START_END is not None:
                plot_flight_density(df_d1_nightstop_sgn_START_END)

        with st.expander('Biểu overlap'):
            if df_d1_nightstop_sgn_START_END is not None:
                visualize_overlap(df_d1_nightstop_sgn_START_END)

        with st.expander('Gant Chart - Night Stop'):
            if df_d1_nightstop_sgn_START_END is not None:
                gantt_chart(df_d1_nightstop_sgn_START_END)
    except Exception as e:
        st.error(e)
with tabs[5]:
    st.write('Visualization')
    try:
        if df_day1_preflight_sgn_START_END is not None and df_d1_nightstop_sgn_START_END is not None and df_d1_transit_sgn_START_END is not None:
            df_day1_preflight_sgn_START_END['TYPE'] = 'Preflight'
            df_d1_nightstop_sgn_START_END['TYPE'] = 'Night Stop'
            df_d1_transit_sgn_START_END['TYPE'] = 'Transit'
            df_day1_merged = pd.concat([df_day1_preflight_sgn_START_END, df_d1_transit_sgn_START_END, df_d1_nightstop_sgn_START_END], ignore_index=True)
            st.write(df_day1_merged)
            plot_flight_density(df_day1_merged)
            gantt_chart_type(df_day1_merged)
            visualize_ground_time_overlap(df_day1_merged)
    except Exception as e:
        st.error(e)
with tabs[6]:
    st.write('Tính toán nhân lực CRS A transit + preflight + daily/weekly')
    st.write('Các thông số có thể thay đổi được tuỳ theo đầu vào. B1+B2 được mặc định cho việc tính toán là standby = 1,1')
    try:
        with st.expander("Overlap + Peak _ Slot Staffing , Time Slot Staffing"):
            if df_day1_merged is not None:
                mpwr_1 = calculate_staffing_with_overlap_and_shifts(df_day1_merged)

                # Display results as a table
                st.write("Peak Times:")
                peak_times_df = pd.DataFrame(mpwr_1["Peak Times"])
                st.write(peak_times_df)

                st.write("Time Slot Staffing:")
                time_slot_staffing_df = pd.DataFrame(mpwr_1["Time Slot Staffing"])
                st.write(time_slot_staffing_df)

                # Plot Peak Times
                fig_peak_times = px.scatter(peak_times_df, x='time', y='ground_count', title='Peak Times', labels={'time': 'Time', 'ground_count': 'Ground Count'})
                st.plotly_chart(fig_peak_times)

                # Plot Time Slot Staffing
                fig_time_slot_staffing = px.line(time_slot_staffing_df, x='start', y='crs_a_needed', title='Time Slot Staffing', labels={'start': 'Start Time', 'crs_a_needed': 'CRS A Needed'})
                fig_time_slot_staffing.add_trace(go.Scatter(x=time_slot_staffing_df['start'], y=time_slot_staffing_df['crs_b1_needed'], mode='lines', name='CRS B1 Needed'))
                fig_time_slot_staffing.add_trace(go.Scatter(x=time_slot_staffing_df['start'], y=time_slot_staffing_df['crs_b2_needed'], mode='lines', name='CRS B2 Needed'))
                st.plotly_chart(fig_time_slot_staffing)
    except Exception as e:
        st.error(e)