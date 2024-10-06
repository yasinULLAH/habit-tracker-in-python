import sys
import subprocess

# Install required packages
required = {'pandas', 'matplotlib', 'streamlit'}
installed = {pkg.split('==')[0].lower() for pkg in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode().splitlines()}
missing = required - installed

if missing:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# File paths
HABITS_FILE = 'habits.csv'
COMPLETIONS_FILE = 'completions.csv'

# Initialize files if they don't exist
if not os.path.exists(HABITS_FILE):
    df_habits = pd.DataFrame(columns=['Habit ID', 'Habit Name', 'Created On'])
    df_habits.to_csv(HABITS_FILE, index=False)

if not os.path.exists(COMPLETIONS_FILE):
    df_completions = pd.DataFrame(columns=['Habit ID', 'Date'])
    df_completions.to_csv(COMPLETIONS_FILE, index=False)

# Load data
df_habits = pd.read_csv(HABITS_FILE)
df_completions = pd.read_csv(COMPLETIONS_FILE)

st.title("📈 Habit Tracker")

menu = ["Add Habit", "View Habits", "Statistics", "Delete Habit"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Habit":
    st.header("Add a New Habit")
    habit_name = st.text_input("Habit Name")
    if st.button("Add Habit"):
        if habit_name:
            new_id = df_habits['Habit ID'].max() + 1 if not df_habits.empty else 1
            new_habit = {'Habit ID': new_id, 'Habit Name': habit_name, 'Created On': datetime.today().strftime('%Y-%m-%d')}
            df_habits = df_habits.append(new_habit, ignore_index=True)
            df_habits.to_csv(HABITS_FILE, index=False)
            st.success(f"Habit '{habit_name}' added successfully!")
        else:
            st.error("Please enter a habit name.")

elif choice == "View Habits":
    st.header("Your Habits")
    if not df_habits.empty:
        for index, row in df_habits.iterrows():
            st.subheader(row['Habit Name'])
            habit_id = row['Habit ID']
            today = datetime.today().date()
            last_30_days = [today - timedelta(days=i) for i in range(30)]
            completions = df_completions[df_completions['Habit ID'] == habit_id]['Date'].tolist()
            completions = [datetime.strptime(date, '%Y-%m-%d').date() for date in completions]
            status = [1 if day in completions else 0 for day in last_30_days]
            df_status = pd.DataFrame({
                'Date': last_30_days,
                'Completed': status
            })
            df_status = df_status.sort_values('Date')
            fig, ax = plt.subplots(figsize=(10, 2))
            ax.bar(df_status['Date'], df_status['Completed'], color='green')
            ax.set_ylim(0, 1.5)
            ax.set_yticks([])
            ax.set_xticks([])
            st.pyplot(fig)
            if st.button(f"Mark as Completed for Today - {row['Habit Name']}"):
                if not df_completions[(df_completions['Habit ID'] == habit_id) & (df_completions['Date'] == today.strftime('%Y-%m-%d'))].empty:
                    st.warning("Already marked as completed today.")
                else:
                    new_completion = {'Habit ID': habit_id, 'Date': today.strftime('%Y-%m-%d')}
                    df_completions = df_completions.append(new_completion, ignore_index=True)
                    df_completions.to_csv(COMPLETIONS_FILE, index=False)
                    st.success("Marked as completed for today!")

    else:
        st.info("No habits added yet.")

elif choice == "Statistics":
    st.header("Habit Statistics")
    if not df_habits.empty:
        habit = st.selectbox("Select Habit", df_habits['Habit Name'])
        habit_id = df_habits[df_habits['Habit Name'] == habit]['Habit ID'].values[0]
        completions = df_completions[df_completions['Habit ID'] == habit_id]['Date'].tolist()
        completions = [datetime.strptime(date, '%Y-%m-%d').date() for date in completions]
        df_stats = pd.DataFrame({'Date': completions})
        df_stats['Count'] = 1
        df_stats = df_stats.groupby('Date').sum().reset_index()
        fig, ax = plt.subplots()
        ax.plot(df_stats['Date'], df_stats['Count'], marker='o')
        ax.set_title(f"Progress for '{habit}'")
        ax.set_xlabel("Date")
        ax.set_ylabel("Completions")
        st.pyplot(fig)

        # Streak Calculation
        streak = 0
        current = datetime.today().date()
        while current.strftime('%Y-%m-%d') in df_completions[df_completions['Habit ID'] == habit_id]['Date'].values:
            streak += 1
            current -= timedelta(days=1)
        st.metric("Current Streak", f"{streak} days")

    else:
        st.info("No habits available for statistics.")

elif choice == "Delete Habit":
    st.header("Delete a Habit")
    if not df_habits.empty:
        habit = st.selectbox("Select Habit to Delete", df_habits['Habit Name'])
        if st.button("Delete"):
            habit_id = df_habits[df_habits['Habit Name'] == habit]['Habit ID'].values[0]
            df_habits = df_habits[df_habits['Habit ID'] != habit_id]
            df_completions = df_completions[df_completions['Habit ID'] != habit_id]
            df_habits.to_csv(HABITS_FILE, index=False)
            df_completions.to_csv(COMPLETIONS_FILE, index=False)
            st.success(f"Habit '{habit}' deleted successfully!")
    else:
        st.info("No habits to delete.")
