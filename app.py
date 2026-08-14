import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Seat Checker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTS & CONFIG ---
SPECIALIZATIONS = [
    "Computer Science",
    "Artificial Intelligence",
    "Data Science",
    "Cyber Security",
    "Gaming & Animation"
]

# --- DATA LOADING ---
def load_data():
    df = pd.read_csv("data/master_merit_list.csv")
    
    # Sort to determine merit rank (CGPA desc, Roll asc)
    df = df.sort_values(by=["cgpa", "roll"], ascending=[False, True]).reset_index(drop=True)
    df["merit_rank"] = df.index + 1
    
    # Fill NAs cleanly
    # Some Pandas versions prefer fillna over replace for this, so we handle columns explicitly
    string_cols = [
        "choice_1", "choice_2", "choice_3", "choice_4", "choice_5",
        "allocated_specialisation", "new_section", "old_section", "status"
    ]
    df[string_cols] = df[string_cols].fillna("")
    
    # Clean up status field for missing ones
    df.loc[df['status'] == "", 'status'] = "unknown"
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Error: Could not find `data/master_merit_list.csv`. Please ensure the file is present in the data folder.")
    st.stop()

# --- HELPER FUNCTIONS ---
def get_choice_rank(row):
    alloc = row['allocated_specialisation']
    if not alloc:
        return "Not Allocated"
    for i in range(1, 6):
        if row[f'choice_{i}'] == alloc:
            return f"Choice {i}"
    return "Not in choices"

df['choice_received'] = df.apply(get_choice_rank, axis=1)

def render_student_card(student):
    """Renders a responsive, native Streamlit card for a student."""
    with st.container(border=True):
        st.subheader(f"{student['name']} ({student['roll']})")
        
        # Status Badge
        status = student['status']
        if status == 'allocated':
            st.success("Allocated")
        elif status == 'no_response_not_allocated':
            st.warning("No Response - Not Allocated")
        else:
            st.error("Missing From Official Lists")
            
        # Top Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("CGPA", f"{student['cgpa']:.3f}")
        col2.metric("Merit Rank", f"#{student['merit_rank']}")
        col3.metric("Gender", student.get('gender', 'Unknown'))
        col4.metric("Old Section", student['old_section'])
        col5.metric("New Section", student['new_section'] if student['new_section'] else "-")
        
        st.markdown(f"**Allocated Specialisation:** {student['allocated_specialisation'] if student['allocated_specialisation'] else '-'}")
        
        # Preferences List
        st.markdown("**Preferences:**")
        for i in range(1, 6):
            choice = student[f'choice_{i}']
            if not choice:
                continue
            
            is_alloc = (choice == student['allocated_specialisation']) and (student['allocated_specialisation'] != "")
            
            if is_alloc:
                st.markdown(f"{i}. **:green[{choice}]** *(Allocated)*")
            else:
                st.markdown(f"{i}. {choice}")

@st.dialog("Student Details")
def show_student_modal(student):
    render_student_card(student)

# --- UI LAYOUT ---
st.title("🎓 Merit Seat Checker")
st.markdown("Check your specialization allotment, section assignment, and merit position.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🔍 Lookup", "📋 Full List", "🔀 Section Crosswalk", "📊 Overview", "🔮 Prediction", "📈 Advanced Analysis"])

# ==========================================
# TAB 1: STUDENT LOOKUP
# ==========================================
with tab1:
    st.header("Lookup Student")
    search_term = st.text_input("Search by Roll Number (e.g., CT-247) or Name (e.g., Feras)", "").strip().lower()
    
    if search_term:
        mask = df['roll'].str.lower().str.contains(search_term, na=False) | df['name'].str.lower().str.contains(search_term, na=False)
        results = df[mask]
        
        if len(results) == 0:
            st.warning("No students found matching your search.")
        else:
            st.success(f"Found {len(results)} matching student(s)")
            for _, student in results.iterrows():
                render_student_card(student)
    else:
        st.info("Enter a name or roll number above to view a student's result card.")

# ==========================================
# TAB 2: FULL LIST
# ==========================================
with tab2:
    st.header("Full Merit List")
    
    # We place filters inside an expander on mobile / sidebar on desktop using standard Streamlit Sidebar
    with st.sidebar:
        st.header("Filters")
        
        if st.button("Reset Filters"):
            st.session_state.clear()
            st.rerun() 
            
        f_old_sec = st.multiselect("Old Section", sorted([s for s in df['old_section'].unique() if s]))
        f_new_sec = st.multiselect("New Section", sorted([s for s in df['new_section'].unique() if s]))
        f_spec = st.multiselect("Allocated Specialisation", sorted([s for s in df['allocated_specialisation'].unique() if s]))
        f_status = st.multiselect("Status", sorted([s for s in df['status'].unique() if s]))
        f_gender = st.multiselect("Gender", sorted([s for s in df.get('gender', pd.Series()).unique() if s]))
        
        min_cgpa, max_cgpa = float(df['cgpa'].min()), float(df['cgpa'].max())
        f_cgpa = st.slider("CGPA Range", min_value=min_cgpa, max_value=max_cgpa, value=(min_cgpa, max_cgpa))
        
        f_roll = st.text_input("Roll Number Starts With (e.g., CT-1)")
        
        st.markdown("---")
        st.subheader("Sorting")
        sort_options = ['merit_rank', 'roll', 'name', 'cgpa', 'old_section', 'new_section', 'allocated_specialisation']
        if 'gender' in df.columns:
            sort_options.insert(4, 'gender')
            
        sort_col = st.selectbox("Sort Data By", sort_options, index=0)
        sort_asc = st.toggle("Sort Ascending", value=True)

    # Apply filters dynamically
    filtered_df = df.copy()
    if f_old_sec:
        filtered_df = filtered_df[filtered_df['old_section'].isin(f_old_sec)]
    if f_new_sec:
        filtered_df = filtered_df[filtered_df['new_section'].isin(f_new_sec)]
    if f_spec:
        filtered_df = filtered_df[filtered_df['allocated_specialisation'].isin(f_spec)]
    if f_status:
        filtered_df = filtered_df[filtered_df['status'].isin(f_status)]
    if f_gender and 'gender' in df.columns:
        filtered_df = filtered_df[filtered_df['gender'].isin(f_gender)]
    
    filtered_df = filtered_df[(filtered_df['cgpa'] >= f_cgpa[0]) & (filtered_df['cgpa'] <= f_cgpa[1])]
    
    if f_roll:
        filtered_df = filtered_df[filtered_df['roll'].str.upper().str.startswith(f_roll.upper())]
        
    # Apply explicit sorting in Python
    filtered_df = filtered_df.sort_values(by=sort_col, ascending=sort_asc)
        
    st.write(f"Showing **{len(filtered_df)}** of {len(df)} total students.")
    
    # Columns to display by default vs expanded
    display_cols = [
        'merit_rank', 'roll', 'name', 'cgpa', 'gender', 'old_section', 'new_section', 
        'allocated_specialisation', 'status', 
        'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5'
    ]
    
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    
    display_df = filtered_df[display_cols].reset_index(drop=True)
    display_df.index = display_df.index + 1  # 1-based
    display_df.index.name = 'S.No'
    
    # hide_index=False so S.No shows as a fixed row label, not a sortable column
    st.dataframe(display_df, use_container_width=True, hide_index=False)
    
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered CSV",
        data=csv_data,
        file_name="filtered_merit_list.csv",
        mime="text/csv"
    )

# ==========================================
# TAB 3: SECTION CROSSWALK
# ==========================================
with tab3:
    st.header("Section Crosswalk")
    st.write("Analyze how students shifted from their Old Sections into New Sections.")
    
    cw_spec = st.multiselect(
        "Filter Crosswalk by Allocated Specialisation (Optional)", 
        sorted([s for s in df['allocated_specialisation'].unique() if s]), 
        key="cw_spec"
    )
    
    cw_df = df.copy()
    if cw_spec:
        cw_df = cw_df[cw_df['allocated_specialisation'].isin(cw_spec)]
        
    # Remove students without an old section for the crosswalk
    cw_df = cw_df[cw_df['old_section'] != ""]
    
    if len(cw_df) == 0:
        st.warning("No data matches the selected filters.")
    else:
        # Prepare data for crosstab
        cw_df['new_section_display'] = cw_df['new_section'].replace("", "Unallocated")
        
        # 1. Crosstab Table
        crosstab = pd.crosstab(cw_df['old_section'], cw_df['new_section_display'], margins=True, margins_name="Total")
        
        # 2. Heatmap via Plotly
        hm_data = pd.crosstab(cw_df['old_section'], cw_df['new_section_display'])
        fig = px.imshow(
            hm_data, 
            text_auto=True, 
            aspect="auto", 
            color_continuous_scale="Blues",
            labels=dict(x="New Section", y="Old Section", color="Students")
        )
        
        col_ct, col_hm = st.columns([1, 1.5])
        with col_ct:
            st.subheader("Data Table")
            st.dataframe(crosstab, use_container_width=True)
        with col_hm:
            st.subheader("Heatmap")
            st.plotly_chart(fig, use_container_width=True)
            
        # 3. Drill Down Viewer
        st.markdown("---")
        st.subheader("Drill Down")
        st.write("View the specific students within any cell of the crosswalk matrix.")
        
        dd_col1, dd_col2 = st.columns(2)
        with dd_col1:
            dd_old = st.selectbox("Select Old Section", sorted(cw_df['old_section'].unique()))
        with dd_col2:
            dd_new = st.selectbox("Select New Section", sorted(cw_df['new_section_display'].unique()))
            
        drill_mask = (cw_df['old_section'] == dd_old) & (cw_df['new_section_display'] == dd_new)
        drill_results = cw_df[drill_mask]
        
        st.write(f"**Found {len(drill_results)} student(s)** moving from Old Section **{dd_old}** ➔ New Section **{dd_new}**.")
        for _, student in drill_results.iterrows():
            render_student_card(student)

# ==========================================
# TAB 4: OVERVIEW & STATS
# ==========================================
with tab4:
    st.header("Overview & Statistics")
    
    # Top Level Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Students Processed", len(df))
    m2.metric("Successfully Allocated", len(df[df['status'] == 'allocated']))
    m3.metric("Not Allocated / Missing", len(df[df['status'] != 'allocated']))
    
    st.markdown("---")
    
    # Charts
    st.subheader("Students per Specialisation")
    spec_counts = df[df['allocated_specialisation'] != ""]['allocated_specialisation'].value_counts().reset_index()
    spec_counts.columns = ['Specialisation', 'Students']
    
    if not spec_counts.empty:
        fig1 = px.bar(spec_counts, x='Students', y='Specialisation', orientation='h', color='Specialisation')
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.write("No allocation data.")
            
    st.markdown("---")
    
    # Closing Merits
    st.subheader("Closing Merit Lists")
    st.write("The lowest CGPA that successfully secured a seat in each specialisation.")
    
    closing_merits = []
    for spec in SPECIALIZATIONS:
        spec_df = df[df['allocated_specialisation'] == spec]
        if not spec_df.empty:
            # Since df is sorted by CGPA desc, the last row is the lowest CGPA
            lowest = spec_df.iloc[-1]
            closing_merits.append({
                "Specialisation": spec,
                "Lowest CGPA": lowest['cgpa'],
                "Student Name": lowest['name'],
                "Roll No": lowest['roll'],
                "Merit Rank": lowest['merit_rank']
            })
            
    if closing_merits:
        cm_df = pd.DataFrame(closing_merits)
        # Format the CGPA column for display
        st.dataframe(cm_df, use_container_width=True)
    else:
        st.write("No closing merit data available yet.")

# ==========================================
# TAB 5: PREDICTION
# ==========================================
with tab5:
    st.header("🔮 Admission Predictor")
    st.write("Analyze historical averages and predict your chances based on this year's merit allocation.")
    
    st.subheader("Seat Allocation")
    spec_counts = df[df['allocated_specialisation'] != ""]['allocated_specialisation'].value_counts().reset_index()
    spec_counts.columns = ['Specialisation', 'Allocated Seats']
    if not spec_counts.empty:
        st.dataframe(spec_counts, use_container_width=True, hide_index=True)
    else:
        st.write("No allocation data available for seats.")
        
    st.markdown("---")
    
    stats = []
    for spec in SPECIALIZATIONS:
        spec_df = df[df['allocated_specialisation'] == spec]
        if not spec_df.empty:
            avg_cgpa = spec_df['cgpa'].mean()
            min_cgpa = spec_df['cgpa'].min()
            max_cgpa = spec_df['cgpa'].max()
            
            stats.append({
                "Specialisation": spec,
                "Highest CGPA": max_cgpa,
                "Average CGPA": avg_cgpa,
                "Minimum CGPA (Closing Merit)": min_cgpa,
                "Safe Target": avg_cgpa
            })
            
    if stats:
        stats_df = pd.DataFrame(stats)
        
        st.subheader("Historical Statistics")
        st.dataframe(
            stats_df.style.format({
                "Highest CGPA": "{:.3f}",
                "Average CGPA": "{:.3f}",
                "Minimum CGPA (Closing Merit)": "{:.3f}",
                "Safe Target": "{:.3f}"
            }), 
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("Chances Calculator")
        user_cgpa = st.slider("Select your expected CGPA:", min_value=1.5, max_value=4.0, value=3.5, step=0.01)
        
        cols = st.columns(len(SPECIALIZATIONS))
        for i, row in stats_df.iterrows():
            with cols[i]:
                spec = row["Specialisation"]
                max_cgpa = row["Highest CGPA"]
                avg_cgpa = row["Average CGPA"]
                min_cgpa = row["Minimum CGPA (Closing Merit)"]
                
                with st.container(border=True):
                    # Using shortened names to fit layout better
                    short_spec = spec.replace('Computer Science', 'CS').replace('Artificial Intelligence', 'AI').replace('Gaming & Animation', 'Gaming')
                    st.markdown(f"**{short_spec}**")
                    if user_cgpa >= avg_cgpa:
                        st.success("🟢 Likely")
                    elif user_cgpa >= min_cgpa:
                        st.warning("🟡 Possible")
                    else:
                        st.error("🔴 Unlikely")
                    st.caption(f"Min: {min_cgpa:.3f}\n\nAvg: {avg_cgpa:.3f}\n\nMax: {max_cgpa:.3f}")
    else:
        st.write("No allocation data available for predictions.")

# ==========================================
# TAB 6: ADVANCED ANALYSIS
# ==========================================
with tab6:
    st.header("📈 Advanced Analysis")
    st.write("Deep dive into demographic metrics, choice satisfaction, and CGPA distributions.")
    
    # 1. Advanced CGPA Distribution
    st.subheader("Advanced CGPA Distribution")
    st.write("Analyze the CGPA distribution with custom color coding and filters. Click any dot to see full student details.")
    
    # Filter Controls
    with st.expander("⚙️ Chart Controls & Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            color_by = st.selectbox("Color By", ["Gender", "Old Section", "New Section"], index=0)
        with col2:
            min_cgpa, max_cgpa = float(df['cgpa'].min()), float(df['cgpa'].max())
            f_cgpa = st.slider("CGPA Range", min_value=min_cgpa, max_value=max_cgpa, value=(min_cgpa, max_cgpa))
        with col3:
            f_old_sec = st.multiselect("Filter by Old Section", sorted([s for s in df['old_section'].unique() if s]))
            f_new_sec = st.multiselect("Filter by New Section", sorted([s for s in df['new_section'].unique() if s]))
            
    # Apply Filters
    plot_df = df.copy()
    if 'gender' in df.columns:
        plot_df = plot_df[plot_df['gender'].isin(['Male', 'Female'])]
        
    if f_old_sec:
        plot_df = plot_df[plot_df['old_section'].isin(f_old_sec)]
    if f_new_sec:
        plot_df = plot_df[plot_df['new_section'].isin(f_new_sec)]
        
    plot_df = plot_df[(plot_df['cgpa'] >= f_cgpa[0]) & (plot_df['cgpa'] <= f_cgpa[1])]
    
    # Map color_by to column name
    color_col_map = {
        "Gender": "gender",
        "Old Section": "old_section",
        "New Section": "new_section"
    }
    color_col = color_col_map[color_by]
    
    # Remove empty values for the selected color column
    plot_df = plot_df[plot_df[color_col] != ""]
    
    if not plot_df.empty:
        # Distinct generic colors requested by user (Red, Blue, Green, Yellow, Light Gray instead of white for visibility, Dark Gray instead of black)
        generic_colors = ["#ef4444", "#3b82f6", "#22c55e", "#eab308", "#d1d5db", "#374151", "#a855f7", "#ec4899", "#f97316"]
        
        # Sort so the legend and X axis are consistent
        plot_df = plot_df.sort_values(by=color_col)
        
        fig_scatter = px.strip(
            plot_df, 
            x=color_col, 
            y='cgpa', 
            color=color_col,
            hover_data={'name': True, 'roll': True, 'cgpa': True, color_col: False},
            custom_data=['roll'],
            stripmode='overlay',
            color_discrete_sequence=generic_colors,
            labels={color_col: color_by, 'cgpa': 'CGPA'}
        )
        
        # Add average lines dynamically
        unique_groups = plot_df[color_col].unique()
        for idx, group in enumerate(unique_groups):
            avg_val = plot_df[plot_df[color_col] == group]['cgpa'].mean()
            line_color = generic_colors[idx % len(generic_colors)]
            
            fig_scatter.add_hline(y=avg_val, line_dash="dash", line_color=line_color, 
                                  annotation_text=f"{group} Avg: {avg_val:.2f}", 
                                  annotation_position="bottom right" if idx % 2 == 0 else "top right")
                                  
        event = st.plotly_chart(fig_scatter, use_container_width=True, on_select="rerun", selection_mode="points")
        
        selection = getattr(event, "selection", event.get("selection", {}) if isinstance(event, dict) else {})
        points = selection.get("points", [])
        
        if points:
            selected_roll = points[0]["customdata"][0]
            student = df[df['roll'] == selected_roll].iloc[0]
            show_student_modal(student)
    else:
        st.write("No data matches the selected filters.")
        
    st.markdown("---")
    
    # 2. Gender Distribution and Choice Satisfaction
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Gender Distribution")
        if 'gender' in df.columns:
            gender_counts = df['gender'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'Students']
            fig3 = px.pie(gender_counts, names='Gender', values='Students', hole=0.4, color='Gender', color_discrete_map={'Male': '#3b82f6', 'Female': '#ec4899', 'Review': '#f59e0b'})
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.write("Gender data not available.")
            
    with col2:
        st.subheader("Choice Satisfaction")
        valid_choices = df[df['choice_received'] != 'Not Allocated']
        if not valid_choices.empty:
            choice_counts = valid_choices['choice_received'].value_counts().reset_index()
            choice_counts.columns = ['Choice', 'Students']
            
            # Show pie chart
            fig2 = px.pie(choice_counts, names='Choice', values='Students', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
            
            # Add textual explanation for Choice Satisfaction
            st.write("### Choice Allocation Breakdown")
            total_allocated = valid_choices.shape[0]
            st.write(f"**Total Allocated Students:** {total_allocated}")
            
            # Sort choices (Choice 1, Choice 2, etc.) to show them in order
            choice_counts = choice_counts.sort_values(by='Choice')
            for index, row in choice_counts.iterrows():
                choice = row['Choice']
                count = row['Students']
                pct = (count / total_allocated) * 100
                st.write(f"- **{choice}:** {count} students received this choice, which is **{pct:.1f}%** of allocated students.")
        else:
            st.write("No choice data available.")
            
    st.markdown("---")
    
    # 3. Gender Division by Section
    if 'gender' in df.columns:
        st.subheader("Gender Division by Section")
        st.write("Analyze the distribution of boys and girls across the newly allocated sections.")
        
        # Filter out empty sections
        gen_df = df[df['new_section'] != ""].copy()
        gen_df['new_section_display'] = gen_df['new_section']
        
        if not gen_df.empty:
            gen_crosstab = pd.crosstab(gen_df['new_section_display'], gen_df['gender'], margins=True, margins_name="Total")
            
            gen_hm_data = pd.crosstab(gen_df['new_section_display'], gen_df['gender'])
            fig_gen = px.imshow(
                gen_hm_data, 
                text_auto=True, 
                aspect="auto", 
                color_continuous_scale="Purples",
                labels=dict(x="Gender", y="New Section", color="Students")
            )
            
            gc1, gc2 = st.columns([1, 1.5])
            with gc1:
                st.dataframe(gen_crosstab, use_container_width=True)
            with gc2:
                st.plotly_chart(fig_gen, use_container_width=True)
        else:
            st.write("No section data available for gender division.")

    st.markdown("---")
    
    st.subheader("Specialisation Demand Analysis")
    st.write("Analyze the popularity of each specialisation across student preferences.")
    
    pref_data = []
    for spec in SPECIALIZATIONS:
        row = {"Specialisation": spec}
        for i in range(1, 6):
            # Use startswith to catch "Computer Science - (No Specialisation)"
            count = df[df[f'choice_{i}'].str.startswith(spec, na=False)].shape[0]
            row[f'Choice {i}'] = count
        pref_data.append(row)
        
    if pref_data:
        pref_df = pd.DataFrame(pref_data)
        pref_melt = pref_df.melt(id_vars=["Specialisation"], var_name="Preference Level", value_name="Students")
        
        fig_pref = px.bar(
            pref_melt, 
            x="Specialisation", 
            y="Students", 
            color="Preference Level", 
            barmode="group",
            text="Students"
        )
        fig_pref.update_traces(textposition='outside')
        st.plotly_chart(fig_pref, use_container_width=True)
        
        st.write("### Allocation Success by Specialisation")
        st.write("For students allocated to each specialisation, which choice was it for them?")
        
        alloc_success_data = []
        for spec in SPECIALIZATIONS:
            spec_allocs = df[df['allocated_specialisation'] == spec]
            total_alloc = len(spec_allocs)
            if total_alloc > 0:
                row = {"Specialisation": spec, "Total Allocated": total_alloc}
                choice_counts = spec_allocs['choice_received'].value_counts()
                for i in range(1, 6):
                    c_name = f"Choice {i}"
                    row[c_name] = choice_counts.get(c_name, 0)
                alloc_success_data.append(row)
                
        if alloc_success_data:
            alloc_success_df = pd.DataFrame(alloc_success_data)
            st.dataframe(alloc_success_df, use_container_width=True, hide_index=True)
