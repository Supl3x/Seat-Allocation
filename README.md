# 🎓 Merit Seat Checker

A comprehensive, interactive Streamlit web application designed to help students check their specialization allotments, track section assignments, and predict admission chances based on merit positions.

## 🚀 Features

The application is divided into five distinct sections to provide an intuitive and data-rich experience:

### 1. 🔍 Lookup Student
Quickly search for any student using their **Roll Number** (e.g., CT-247) or **Name**. 
- View an individualized student card displaying their CGPA, Merit Rank, Old/New sections.
- See their detailed preference list, highlighting which choice they were successfully allocated.
- Displays immediate status (Allocated, No Response, Missing).

### 2. 📋 Full Merit List
A fully filterable, sortable, and responsive datatable containing the entire merit list.
- **Dynamic Filters:** Filter by Old Section, New Section, Allocated Specialisation, and Allocation Status.
- **CGPA Slider:** Filter students within a specific CGPA range.
- **Export Data:** Download your filtered datasets instantly as a CSV file for offline use.

### 3. 🔀 Section Crosswalk
Analyze student movement between sections using data visualization.
- View a detailed crosswalk table (Crosstab) showing how students transitioned from their "Old Sections" into their "New Sections".
- Interactive **Heatmap** to visualize the density of section changes.
- **Drill-down feature:** Select a specific Old ➔ New section pathway to see the exact students who made that transition.

### 4. 📊 Overview & Statistics
High-level analytics of the admission and allocation process.
- **Distribution Charts:** View bar charts of students per specialization.
- **Choice Satisfaction:** Pie charts showcasing how many students received their 1st, 2nd, or 3rd choices.
- **Closing Merits:** See the lowest CGPA that successfully secured a seat in each specialization.

### 5. 🔮 Prediction & Seat Allocation
Help future students analyze historical averages and predict their admission chances.
- **Seat Allocation Table:** See exactly how many seats are currently allocated to each specialization.
- **Historical Statistics:** Review the Highest, Average, and Minimum (Closing) CGPAs for each field.
- **Chances Calculator:** Use an interactive slider to input an expected CGPA and see the predicted likelihood (🟢 Likely, 🟡 Possible, 🔴 Unlikely) of securing a seat in each specific specialization.

## 🛠️ Technology Stack
- **Python:** Core language
- **Streamlit:** Frontend framework and interactive UI
- **Pandas:** Data manipulation, cleaning, and filtering
- **Plotly Express:** Advanced interactive data visualization

## 📂 Data Structure
The application runs on a core dataset stored in `data/master_merit_list.csv`. It dynamically reads, cleans, and handles missing information to ensure a seamless experience.

## 💻 How to Run Locally

1. Ensure you have Python installed.
2. Clone this repository.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
