<<<<<<< HEAD
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# Streamlit UI
st.title("Comprehensive Sales Analysis Dashboard")

# File upload option
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    try:
        # Load data
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
        st.write("## Data Preview")
        st.dataframe(df.head())

        # Convert date columns
        date_columns = ["Created Date", "DemoDate", "QuoteSentDate", "Next Action Date"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

        # Dashboard options
        analysis_option = st.selectbox(
            "Choose Analysis",
            [
                "Select",
                "Company Count by Order Stage",
                "Salesperson Performance Analysis",
                "Sales Funnel Analysis",
                "Average Duration Between Stages",
                "Key Sales Metrics"
            ]
        )

        # Analysis: Company Count by Order Stage
        if analysis_option == "Company Count by Order Stage":
            st.subheader("Company Count by Order Stage")
            if "Order Status" in df.columns and "Company" in df.columns:
                stage_summary = df.groupby("Order Status").agg(
                    Company_Count=("Company", "count")
                ).reset_index()

                st.subheader("Grouped Data by Order Status")
                st.dataframe(stage_summary)

                # Plot Bar Chart
                if not stage_summary.empty:
                    plt.figure(figsize=(12, 6))
                    barplot = sns.barplot(
                        x="Order Status",
                        y="Company_Count",
                        data=stage_summary,
                        color="skyblue"
                    )
                    plt.ylabel("Company Count", fontsize=12, color="blue")
                    plt.xlabel("Order Status (Stage)", fontsize=12)
                    plt.title("Company Count by Stage", fontsize=14)
                    plt.xticks(rotation=45, fontsize=10)

                    # Annotate bars
                    for p in barplot.patches:
                        plt.annotate(
                            format(p.get_height(), ".0f"),
                            (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha="center", va="center", fontsize=10, color="black", xytext=(0, 5),
                            textcoords="offset points"
                        )
                    st.pyplot(plt)
                else:
                    st.warning("No data available for this analysis.")

        # Analysis: Salesperson Performance
        elif analysis_option == "Salesperson Performance Analysis":
            st.subheader("Salesperson Performance Analysis")

            if all(col in df.columns for col in ["Created By", "Company", "Order Status"]):
                # Aggregate data
                salesperson_summary = df.groupby("Created By").agg(
                    Total_Leads=("Company", "count"),
                    Wins=("Order Status", lambda x: (x.str.contains("Win", na=False)).sum())
                ).reset_index()

                # Correct Win Rate Calculation
                salesperson_summary["Win Rate"] = salesperson_summary["Wins"] / salesperson_summary["Total_Leads"]
                salesperson_summary["Win Rate"] = salesperson_summary["Win Rate"].fillna(0) * 100  # Convert to %

                st.write("## Salesperson Summary")
                st.dataframe(salesperson_summary)

                # Plot Bar & Line Chart
                fig, ax1 = plt.subplots(figsize=(12, 6))

                # Bar plot for Wins
                sns.barplot(x="Created By", y="Wins", data=salesperson_summary, ax=ax1, color="skyblue")
                ax1.set_ylabel("Total Wins", fontsize=12, color="blue")
                ax1.set_xlabel("Salesperson", fontsize=12)
                ax1.tick_params(axis="x", rotation=45, labelsize=10)
                ax1.set_title("Total Wins and Win Rate by Salesperson", fontsize=14)

                # Annotate Wins
                for p in ax1.patches:
                    ax1.annotate(
                        format(p.get_height(), ".0f"),
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha="center", va="bottom", fontsize=10, color="black", xytext=(0, 5),
                        textcoords="offset points"
                    )

                # Secondary axis for Win Rate
                ax2 = ax1.twinx()
                win_rate_plot = sns.lineplot(
                    x="Created By",
                    y="Win Rate",
                    data=salesperson_summary,
                    ax=ax2,
                    color="red",
                    marker="o",
                    linewidth=2
                )
                ax2.set_ylabel("Win Rate (%)", fontsize=12, color="red")
                ax2.tick_params(axis="y", labelcolor="red")
                ax2.set_ylim(0, 100)  # Adjusted to show percentage scale

                # Annotate Win Rate values
                for i, txt in enumerate(salesperson_summary["Win Rate"]):
                    ax2.text(i, txt, f"{txt:.1f}%", ha="center", va="bottom", fontsize=10, color="red", fontweight="bold")

                plt.tight_layout()
                st.pyplot(fig)

        # Analysis: Sales Funnel
        elif analysis_option == "Sales Funnel Analysis":
            st.subheader("Sales Funnel Analysis")
            if "DemoStatus" in df.columns and "QuoteSentDate" in df.columns and "Order Status" in df.columns:
                total_leads = len(df)
                demo_completed = df["DemoStatus"].str.contains("Yes", na=False).sum()
                quote_sent = df["QuoteSentDate"].notnull().sum()
                won = df["Order Status"].str.contains("Win", na=False).sum()

                stages = ["Total Leads", "Demo Completed", "Quote Sent", "Won"]
                values = [total_leads, demo_completed, quote_sent, won]

                fig = go.Figure(go.Funnel(
                    y=stages,
                    x=values,
                    textinfo="value+percent initial",
                    marker={"color": ["blue", "lightblue", "skyblue", "dodgerblue"]}
                ))

                fig.update_layout(title="Sales Funnel Analysis", font=dict(size=16))
                st.plotly_chart(fig)

        # Analysis: Average Duration Between Stages
        elif analysis_option == "Average Duration Between Stages":
            st.subheader("Average Duration Between Stages")
            df["Time to Demo"] = (df["DemoDate"] - df["Created Date"]).dt.days
            df["Demo to Quote"] = (df["QuoteSentDate"] - df["DemoDate"]).dt.days
            df["Total Process Duration"] = (df["QuoteSentDate"] - df["Created Date"]).dt.days

            avg_time_to_demo = df["Time to Demo"].mean()
            avg_demo_to_quote = df["Demo to Quote"].mean()
            avg_total_process = df["Total Process Duration"].mean()

            stages = ["Time to Demo", "Demo to Quote", "Total Process Duration"]
            durations = [avg_time_to_demo, avg_demo_to_quote, avg_total_process]

            fig = go.Figure(data=[go.Bar(x=stages, y=durations, marker_color=["blue", "orange", "green"])])

            fig.update_layout(
                title="Average Duration Between Stages",
                xaxis_title="Stage",
                yaxis_title="Average Duration (days)",
                template="plotly_white"
            )

            st.plotly_chart(fig)

        # Analysis: Key Sales Metrics
        elif analysis_option == "Key Sales Metrics":
            st.subheader("Key Sales Metrics")
            total_leads = df.shape[0]
            win_leads = df[df["Order Status"].str.contains("Win", na=False, case=False)]
            win_rate = (len(win_leads) / total_leads) * 100
            active_leads = df[~df["Order Status"].str.contains("Win|Drop", na=False, case=False)].shape[0]

            st.write(f"**Total Leads:** {total_leads}")
            st.write(f"**Win Rate:** {win_rate:.2f}%")
            st.write(f"**Active Leads:** {active_leads}")

    except Exception as e:
        st.error(f"Error loading or processing the file: {e}")

else:
    st.info("Please upload a CSV file to proceed.")
=======
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# Streamlit UI
st.title("Comprehensive Sales Analysis Dashboard")

# File upload option
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    try:
        # Load data
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
        st.write("## Data Preview")
        st.dataframe(df.head())

        # Convert date columns
        date_columns = ["Created Date", "DemoDate", "QuoteSentDate", "Next Action Date"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

        # Dashboard options
        analysis_option = st.selectbox(
            "Choose Analysis",
            [
                "Select",
                "Company Count by Order Stage",
                "Salesperson Performance Analysis",
                "Sales Funnel Analysis",
                "Average Duration Between Stages",
                "Key Sales Metrics"
            ]
        )

        # Analysis: Company Count by Order Stage
        if analysis_option == "Company Count by Order Stage":
            st.subheader("Company Count by Order Stage")
            if "Order Status" in df.columns and "Company" in df.columns:
                stage_summary = df.groupby("Order Status").agg(
                    Company_Count=("Company", "count")
                ).reset_index()

                st.subheader("Grouped Data by Order Status")
                st.dataframe(stage_summary)

                # Plot Bar Chart
                if not stage_summary.empty:
                    plt.figure(figsize=(12, 6))
                    barplot = sns.barplot(
                        x="Order Status",
                        y="Company_Count",
                        data=stage_summary,
                        color="skyblue"
                    )
                    plt.ylabel("Company Count", fontsize=12, color="blue")
                    plt.xlabel("Order Status (Stage)", fontsize=12)
                    plt.title("Company Count by Stage", fontsize=14)
                    plt.xticks(rotation=45, fontsize=10)

                    # Annotate bars
                    for p in barplot.patches:
                        plt.annotate(
                            format(p.get_height(), ".0f"),
                            (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha="center", va="center", fontsize=10, color="black", xytext=(0, 5),
                            textcoords="offset points"
                        )
                    st.pyplot(plt)
                else:
                    st.warning("No data available for this analysis.")

        # Analysis: Salesperson Performance
        elif analysis_option == "Salesperson Performance Analysis":
            st.subheader("Salesperson Performance Analysis")

            if all(col in df.columns for col in ["Created By", "Company", "Order Status"]):
                # Aggregate data
                salesperson_summary = df.groupby("Created By").agg(
                    Total_Leads=("Company", "count"),
                    Wins=("Order Status", lambda x: (x.str.contains("Win", na=False)).sum())
                ).reset_index()

                # Correct Win Rate Calculation
                salesperson_summary["Win Rate"] = salesperson_summary["Wins"] / salesperson_summary["Total_Leads"]
                salesperson_summary["Win Rate"] = salesperson_summary["Win Rate"].fillna(0) * 100  # Convert to %

                st.write("## Salesperson Summary")
                st.dataframe(salesperson_summary)

                # Plot Bar & Line Chart
                fig, ax1 = plt.subplots(figsize=(12, 6))

                # Bar plot for Wins
                sns.barplot(x="Created By", y="Wins", data=salesperson_summary, ax=ax1, color="skyblue")
                ax1.set_ylabel("Total Wins", fontsize=12, color="blue")
                ax1.set_xlabel("Salesperson", fontsize=12)
                ax1.tick_params(axis="x", rotation=45, labelsize=10)
                ax1.set_title("Total Wins and Win Rate by Salesperson", fontsize=14)

                # Annotate Wins
                for p in ax1.patches:
                    ax1.annotate(
                        format(p.get_height(), ".0f"),
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha="center", va="bottom", fontsize=10, color="black", xytext=(0, 5),
                        textcoords="offset points"
                    )

                # Secondary axis for Win Rate
                ax2 = ax1.twinx()
                win_rate_plot = sns.lineplot(
                    x="Created By",
                    y="Win Rate",
                    data=salesperson_summary,
                    ax=ax2,
                    color="red",
                    marker="o",
                    linewidth=2
                )
                ax2.set_ylabel("Win Rate (%)", fontsize=12, color="red")
                ax2.tick_params(axis="y", labelcolor="red")
                ax2.set_ylim(0, 100)  # Adjusted to show percentage scale

                # Annotate Win Rate values
                for i, txt in enumerate(salesperson_summary["Win Rate"]):
                    ax2.text(i, txt, f"{txt:.1f}%", ha="center", va="bottom", fontsize=10, color="red", fontweight="bold")

                plt.tight_layout()
                st.pyplot(fig)

        # Analysis: Sales Funnel
        elif analysis_option == "Sales Funnel Analysis":
            st.subheader("Sales Funnel Analysis")
            if "DemoStatus" in df.columns and "QuoteSentDate" in df.columns and "Order Status" in df.columns:
                total_leads = len(df)
                demo_completed = df["DemoStatus"].str.contains("Yes", na=False).sum()
                quote_sent = df["QuoteSentDate"].notnull().sum()
                won = df["Order Status"].str.contains("Win", na=False).sum()

                stages = ["Total Leads", "Demo Completed", "Quote Sent", "Won"]
                values = [total_leads, demo_completed, quote_sent, won]

                fig = go.Figure(go.Funnel(
                    y=stages,
                    x=values,
                    textinfo="value+percent initial",
                    marker={"color": ["blue", "lightblue", "skyblue", "dodgerblue"]}
                ))

                fig.update_layout(title="Sales Funnel Analysis", font=dict(size=16))
                st.plotly_chart(fig)

        # Analysis: Average Duration Between Stages
        elif analysis_option == "Average Duration Between Stages":
            st.subheader("Average Duration Between Stages")
            df["Time to Demo"] = (df["DemoDate"] - df["Created Date"]).dt.days
            df["Demo to Quote"] = (df["QuoteSentDate"] - df["DemoDate"]).dt.days
            df["Total Process Duration"] = (df["QuoteSentDate"] - df["Created Date"]).dt.days

            avg_time_to_demo = df["Time to Demo"].mean()
            avg_demo_to_quote = df["Demo to Quote"].mean()
            avg_total_process = df["Total Process Duration"].mean()

            stages = ["Time to Demo", "Demo to Quote", "Total Process Duration"]
            durations = [avg_time_to_demo, avg_demo_to_quote, avg_total_process]

            fig = go.Figure(data=[go.Bar(x=stages, y=durations, marker_color=["blue", "orange", "green"])])

            fig.update_layout(
                title="Average Duration Between Stages",
                xaxis_title="Stage",
                yaxis_title="Average Duration (days)",
                template="plotly_white"
            )

            st.plotly_chart(fig)

        # Analysis: Key Sales Metrics
        elif analysis_option == "Key Sales Metrics":
            st.subheader("Key Sales Metrics")
            total_leads = df.shape[0]
            win_leads = df[df["Order Status"].str.contains("Win", na=False, case=False)]
            win_rate = (len(win_leads) / total_leads) * 100
            active_leads = df[~df["Order Status"].str.contains("Win|Drop", na=False, case=False)].shape[0]

            st.write(f"**Total Leads:** {total_leads}")
            st.write(f"**Win Rate:** {win_rate:.2f}%")
            st.write(f"**Active Leads:** {active_leads}")

    except Exception as e:
        st.error(f"Error loading or processing the file: {e}")

else:
    st.info("Please upload a CSV file to proceed.")
>>>>>>> fe70c9b (Initial commit)
