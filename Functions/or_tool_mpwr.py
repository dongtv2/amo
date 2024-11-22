import collections
import pandas as pd
from ortools.sat.python import cp_model
import plotly.express as px
import plotly.graph_objects as go

def calculate_staffing_with_overlap_and_shifts(df):
    """
    Tính toán nhân lực cần thiết (CRS A, B1, B2) theo từng khung giờ và peak times.

    Tham số:
        df (pd.DataFrame): Dữ liệu chuyến bay với các cột START, END, TYPE.

    Trả về:
        dict: Kết quả bao gồm số lượng CRS A, B1, B2 cần thiết theo từng khung giờ và peak times.
    """
    # Tạo danh sách các sự kiện (START và END)
    time_events = []
    for i, row in df.iterrows():
        time_events.append({'time': row['START'], 'event': 'start'})
        time_events.append({'time': row['END'], 'event': 'end'})

    time_events_df = pd.DataFrame(time_events).sort_values('time')

    # Tính toán số lượng tàu trên mặt đất tại mỗi thời điểm
    ground_count = 0
    ground_counts = []
    for i, row in time_events_df.iterrows():
        if row['event'] == 'start':
            ground_count += 1
        elif row['event'] == 'end':
            ground_count -= 1
        ground_counts.append({'time': row['time'], 'ground_count': ground_count})

    ground_counts_df = pd.DataFrame(ground_counts)

    # Tìm peak times
    peak_times = ground_counts_df[ground_counts_df['ground_count'] == ground_counts_df['ground_count'].max()]
    peak_ground_count = peak_times['ground_count'].max()

    # CRS A calculation
    crs_a_needed = ground_counts_df['ground_count'].max()  # CRS A xử lý tất cả các tàu trên mặt đất.

    # CRS B1 và B2 calculation (standby)
    crs_b1_needed = 1  # Ít nhất 1 CRS B1 standby
    crs_b2_needed = 1  # Ít nhất 1 CRS B2 standby

    # Tính toán số lượng nhân lực theo từng khung giờ
    time_slots = []
    current_time = ground_counts_df['time'].min()
    end_time = ground_counts_df['time'].max()
    slot_duration = pd.Timedelta(minutes=30)  # Chia khung giờ 30 phút
    while current_time < end_time:
        next_time = current_time + slot_duration
        overlap_in_slot = ground_counts_df[
            (ground_counts_df['time'] >= current_time) &
            (ground_counts_df['time'] < next_time)
        ]['ground_count'].max()
        time_slots.append({
            'start': current_time,
            'end': next_time,
            'crs_a_needed': overlap_in_slot if not pd.isna(overlap_in_slot) else 0,
            'crs_b1_needed': 1,  # CRS B1 standby
            'crs_b2_needed': 1   # CRS B2 standby
        })
        current_time = next_time

    # Kết quả
    staffing_result = {
        'Peak Ground Count': peak_ground_count,
        'Peak Times': peak_times[['time', 'ground_count']].to_dict(orient='records'),
        'CRS A Needed': crs_a_needed,
        'CRS B1 Needed': crs_b1_needed,
        'CRS B2 Needed': crs_b2_needed,
        'Time Slot Staffing': time_slots
    }

    # Tạo biểu đồ hiển thị
    fig = px.line(
        ground_counts_df,
        x='time',
        y='ground_count',
        title='Number of Aircraft on Ground Over Time',
        labels={'time': 'Time', 'ground_count': 'Number of Aircraft on Ground'}
    )
    fig.update_layout(height=800, xaxis=dict(showgrid=True), yaxis=dict(showgrid=True))

    # Highlight peak times
    fig.add_trace(go.Scatter(
        x=peak_times['time'],
        y=peak_times['ground_count'],
        mode='markers',
        name='Peak Times',
        marker=dict(color='red', size=10, symbol='x'),
        showlegend=True
    ))

    # Hiển thị biểu đồ trên Streamlit (nếu có)
    try:
        import streamlit as st
        st.plotly_chart(fig)
    except ImportError:
        fig.show()

    return staffing_result

# Example usage (replace `data` with your actual DataFrame):
# staffing_result = calculate_staffing_with_overlap_and_shifts(data)
# print(staffing_result)