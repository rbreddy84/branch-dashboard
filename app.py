import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Branch Performance Viewer", layout="centered")
st.title("🏦 Comprehensive Branch Dashboard")

# File Upload Component
uploaded_file = st.file_uploader("Upload your Deposits Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        # Clean column names
        df.columns = df.columns.astype(str).str.strip()
        
        # Remove the "TOTAL" row at the bottom
        df = df[df["Name of the Branch"].str.upper() != "TOTAL"]

        st.success("Data loaded successfully!")
        
        # Exact column names
        branch_col = "Name of the Branch"
        district_col = "District"
        target_col = "Target for June 2026"
        achieved_col = "Achieved as aon 30-06-2026"
        percent_col = "Percentage of achivement to Target"
        nodal_col = "Nodal Officer"
        co_col = "Controlling Officer"

        # Calculate Rankings
        df['Overall Rank'] = df[percent_col].rank(ascending=False, method='min').fillna(0).astype(int)
        if district_col in df.columns:
            df['District Rank'] = df.groupby(district_col)[percent_col].rank(ascending=False, method='min').fillna(0).astype(int)
        
        total_branches = len(df)

        # --- Branch Selection ---
        st.markdown("### 🏢 Select a Branch")
        branch_list = sorted(list(df[branch_col].dropna().unique()))
        selected_branch = st.selectbox("Search or click to select a branch:", branch_list)

        branch_data = df[df[branch_col] == selected_branch].iloc[0]

        st.divider()
        
        # --- Officer Information ---
        st.markdown(f"## Profile: **{selected_branch}**")
        
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            nodal = branch_data.get(nodal_col, "Not Available")
            st.info(f"**👤 Nodal Officer:**\n\n### {nodal}")
            
        with info_col2:
            co = branch_data.get(co_col, "Not Available")
            st.success(f"**👨‍💼 Controlling Officer:**\n\n### {co}")

        # --- Ranking Display ---
        st.markdown("### 🏆 Branch Rankings")
        rank_col1, rank_col2 = st.columns(2)
        
        dist_name = branch_data.get(district_col, "Unknown")
        total_in_district = len(df[df[district_col] == dist_name]) if district_col in df.columns else 0
        
        with rank_col1:
            if district_col in df.columns:
                st.metric(f"District Rank ({dist_name})", f"#{branch_data['District Rank']} of {total_in_district}")
            else:
                st.metric("District Rank", "Data N/A")
                
        with rank_col2:
            st.metric("Overall Rank (All Districts)", f"#{branch_data['Overall Rank']} of {total_branches}")

        # --- Visual Performance Metrics ---
        st.markdown("### 📊 Performance Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Target", f"₹ {branch_data[target_col]:,.2f}")
        col2.metric("Achieved", f"₹ {branch_data[achieved_col]:,.2f}")
        col3.metric("Achievement %", f"{branch_data[percent_col]:.2f}%")
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = branch_data[percent_col],
            title = {'text': "Target Achievement"},
            number = {'suffix': "%"},
            gauge = {
                'axis': {'range': [None, max(120, branch_data[percent_col] + 10)]},
                'bar': {'color': "#1f77b4"}, 
                'steps' : [
                    {'range': [0, 90], 'color': "#ffcccb"},     
                    {'range': [90, 100], 'color': "#ffffE0"},   
                    {'range': [100, 200], 'color': "#90EE90"}   
                ],
                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()

        # --- NEW: Top 5 and Bottom 5 Leaderboards ---
        st.markdown("### 🥇 Best Performing 5 & ⚠️ Least Performing 5 Performers")
        
        # Extract the necessary columns for a clean table view
        display_cols = [branch_col, district_col, percent_col] if district_col in df.columns else [branch_col, percent_col]
        
        top_5 = df.nlargest(5, percent_col)[display_cols]
        bottom_5 = df.nsmallest(5, percent_col)[display_cols].sort_values(by=percent_col, ascending=True)

        # Rename columns to be cleaner in the UI
        rename_dict = {branch_col: "Branch", district_col: "District", percent_col: "Achievement (%)"}
        top_5 = top_5.rename(columns=rename_dict)
        bottom_5 = bottom_5.rename(columns=rename_dict)

        # Display side-by-side
        tb_col1, tb_col2 = st.columns(2)
        
        with tb_col1:
            st.markdown("#### 🌟 Top 5 Branches")
            st.dataframe(top_5, hide_index=True, use_container_width=True)
            
        with tb_col2:
            st.markdown("#### 📉 Bottom 5 Branches")
            st.dataframe(bottom_5, hide_index=True, use_container_width=True)

    except Exception as e:
        st.error(f"Error processing the file: {e}")
else:
    st.info("Awaiting file upload. Please drag and drop your file above.")
