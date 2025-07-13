import pandas as pd
import os
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

Log_file = 'C:/Users/tekchart01/Desktop/tekchart/reports/STATS/analysis_log.txt' 
# Creating Log Text file
def log_message(message, log_to_file=False):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    if log_to_file:
        with open(Log_file, "a", encoding="utf-8") as log_f:
            log_f.write(log_entry + "\n")


folder = "C:/Users/tekchart01/Desktop/tekchart/bhavcopy/bhavcopy_cash"

# Load all CSV files into a DataFrame
csv_files = [file for file in os.listdir(folder) if file.endswith('.csv')]
df_list = []
for file in csv_files:
    try:
        df = pd.read_csv(os.path.join(folder, file))
        df_list.append(df)
    except Exception as e:
        log_message(f"Error reading file {file}: {e}", log_to_file=True)

main_df = pd.concat(df_list, ignore_index=True)

# Clean column names and filter "EQ" series
main_df.columns = main_df.columns.str.strip()
main_df["SERIES"] = main_df["SERIES"].str.strip()
main_df = main_df[main_df["SERIES"] == "EQ"].dropna()

try:
    # Convert columns to appropriate data types
    main_df['DELIV_QTY'] = pd.to_numeric(main_df['DELIV_QTY'], errors='coerce').fillna(0).astype(int)
    main_df['DELIV_PER'] = pd.to_numeric(main_df['DELIV_PER'], errors='coerce').fillna(0).astype(float)

    # Convert DATE1 to datetime format
    main_df['DATE1'] = pd.to_datetime(main_df['DATE1'].str.strip(), errors='coerce', dayfirst=True)
except Exception as e:
    log_message(f"Error converting columns: {e}", log_to_file=True)
    exit()

# Ensure there are valid dates
if main_df['DATE1'].isna().all():
    log_message("No valid dates found in the dataset.", log_to_file=True)
    exit()

# Get today's date and find the nearest available date
today = pd.Timestamp.today().normalize()
available_dates = main_df['DATE1'].dropna().sort_values().unique()

if len(available_dates) == 0:
    log_message("No available dates in the dataset.", log_to_file=True)
    exit()

nearest_date = min(available_dates, key=lambda x: abs(x - today))

# Filter records for the last 30 days from the nearest available date
start_date = nearest_date - pd.Timedelta(days=30)
main_df = main_df[(main_df['DATE1'] >= start_date) & (main_df['DATE1'] <= nearest_date)]
main_df['DATE1'] = main_df['DATE1'].dt.strftime('%Y-%m-%d')

date = datetime.today().strftime("%d-%b-%Y")

# Print unique dates if there are any
if not main_df.empty:
    log_message(f"Successfully acquired 1 month of data from {date}.", log_to_file=True)
else:
    log_message("No records found in the last 30 days.", log_to_file=True)

figures = []
sector_delivery_data = {}

directory = "C:/Users/tekchart01/Desktop/tekchart/lookups/LOOKUP"
pdf_filename = "C:/Users/tekchart01/Desktop/tekchart/reports/STATS/Market_Sector_Analysis.pdf"
try:
    with PdfPages(pdf_filename) as pdf:

        # PLOT 1: Group by DATE1 and sum NO_OF_TRADES
        datewise_trades = main_df.groupby('DATE1')['NO_OF_TRADES'].sum().reset_index()
        datewise_trades.columns = ['DATE1','NO_OF_TRADES']
        fig1 = plt.figure(figsize=(20, 10))
        plt.plot(datewise_trades['DATE1'], datewise_trades['NO_OF_TRADES'], marker='o', linestyle='-', color='b', label="Total Trades")

        # Formatting the chart
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Total Trades", fontsize=12)
        plt.title("Total Trades Over Time", fontsize=14)
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.grid(True, linewidth=0.5)
        plt.legend(fontsize=10)
        plt.tight_layout()

        datewise_trades['NO_OF_TRADES'] = datewise_trades['NO_OF_TRADES'] / 10**6 

        # Create table data
        table_data = [datewise_trades['DATE1'].tolist(), datewise_trades['NO_OF_TRADES'].tolist()]  
        row_labels = ["Date", "Total Trades"] 

        table = plt.table(cellText=table_data, rowLabels=row_labels, cellLoc='center', loc='bottom', fontsize = 13, bbox=[0.05, -0.35, 0.99, 0.2])

        # Adjust layout to accommodate table
        plt.subplots_adjust(bottom=0.05)

        # Save plot to PDF
        pdf.savefig(fig1, bbox_inches='tight')
        plt.close(fig1)


        # PLOT 2:Group by DATE1 and sum of TURNOVER_LACS
        datewise_turnover = main_df.groupby('DATE1')['TURNOVER_LACS'].sum().reset_index()
        datewise_turnover.columns = ['DATE1','TURNOVER_LACS']

        # Plot the line chart
        fig2 = plt.figure(figsize=(20, 10))
        plt.plot(datewise_turnover['DATE1'], datewise_turnover['TURNOVER_LACS'], marker='o', linestyle='-', color='r', label="Total Turnover (in lakhs)")

        # Formatting the chart
        plt.xlabel("Date", fontsize=15)
        plt.ylabel("Total Trunover", fontsize=15)
        plt.title("Total Trunover Over Time", fontsize=18)
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.grid(True, linewidth=0.5)
        plt.legend(fontsize=12)
        plt.tight_layout()

        datewise_turnover['TURNOVER_LACS'] = datewise_turnover['TURNOVER_LACS'] / 10**6 

        # Create table data
        table_data = [datewise_turnover['DATE1'].tolist(),[f"{x:.4f}" for x in datewise_turnover['TURNOVER_LACS']]]  
        row_labels = ["Date", "TTL_Turnover"] 

        # Add table below the plot
        table = plt.table(cellText=table_data, rowLabels=row_labels, cellLoc='center', loc='bottom', fontsize = 12, bbox=[0.05, -0.35, 0.99, 0.2])

        # Adjust layout to accommodate table
        plt.subplots_adjust(bottom=0.1)

        # Save plot to PDF
        pdf.savefig(fig2, bbox_inches='tight')
        plt.close(fig2)


        # PLOT 3: Group by DATE1 and sum of Total Traded Quantity and Delivery Quantity
        # Aggregate data
        datewise_data = main_df.groupby('DATE1').agg({'TTL_TRD_QNTY': 'sum', 'DELIV_QTY': 'sum'}).reset_index()

        # Create the figure and axis
        fig3, ax1 = plt.subplots(figsize=(20, 10))

        # Plot TTL_TRD_QNTY on the primary y-axis
        ax1.plot(datewise_data['DATE1'], datewise_data['TTL_TRD_QNTY'], marker='o', linestyle='-', color='m', label="Total Traded Quantity")
        ax1.set_xlabel("Date", fontsize=12)
        ax1.set_ylabel("Total Traded Quantity", fontsize=12, color='m')
        ax1.tick_params(axis='y', labelcolor='m')
        ax1.set_xticks(datewise_data['DATE1'])
        ax1.set_xticklabels(datewise_data['DATE1'], rotation=45, ha='right', fontsize=10)
        ax1.grid(True, linewidth=0.5)

        # Create a secondary y-axis
        ax2 = ax1.twinx()
        ax2.plot(datewise_data['DATE1'], datewise_data['DELIV_QTY'], marker='o', linestyle='-', color='g', label="Total Delivery Quantity")
        ax2.set_ylabel("Delivery Quantity", fontsize=12, color='g')
        ax2.tick_params(axis='y', labelcolor='g')

        # Add legends
        fig3.legend(loc="upper left", bbox_to_anchor=(0.035,0.96),fontsize=10)
        plt.title("Total Traded Quantity and Delivery Quantity Over Time", fontsize=14)
        plt.tight_layout()

        datewise_data['TTL_TRD_QNTY'] = datewise_data['TTL_TRD_QNTY'] / 10**6 
        datewise_data['DELIV_QTY'] = datewise_data['DELIV_QTY'] / 10**6

        # Create table data
        table_data = [datewise_data['DATE1'].tolist(),[f"{x:.4f}" for x in datewise_data['TTL_TRD_QNTY']],[f"{x:.4f}" for x in datewise_data['DELIV_QTY']]]  
        row_labels = ["Date","TTL_TRD_QNTY","DELIV_QTY"] 

        # Add table below the plot
        table = plt.table(cellText=table_data, rowLabels=row_labels, cellLoc='center', loc='bottom', fontsize = 12, bbox=[0, -0.35, 0.99, 0.2])

        # Adjust layout to accommodate table
        plt.subplots_adjust(bottom=0.05)

        # Save plot to PDF
        pdf.savefig(fig3, bbox_inches='tight')
        plt.close(fig3)


        # PLOT 4: Group by DATE1 and calculating Overall Market Delivery
        datewise_deliv = main_df.groupby('DATE1').agg({'DELIV_PER': 'sum', 'NO_OF_TRADES': 'count'}).reset_index()
        datewise_deliv['DELIV'] = datewise_deliv['DELIV_PER'] / datewise_deliv['NO_OF_TRADES']

        # Drop the now unnecessary columns
        datewise_deliv = datewise_deliv[['DATE1', 'DELIV']]


        fig4 = plt.figure(figsize=(20, 10))
        plt.plot(datewise_deliv['DATE1'], datewise_deliv['DELIV'], marker='o', linestyle='-', color='c', label="Ttl_Deliv / Ttl_Trades")

        # Formatting the chart
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Delivery", fontsize=12)
        plt.title("Overall Market Delivery", fontsize=14)
        plt.xticks(rotation=45) 
        plt.grid(True, linewidth=0.5)
        plt.legend(fontsize=10)
        plt.tight_layout()

        # datewise_turnover['TURNOVER_LACS'] = datewise_turnover['TURNOVER_LACS'] / 10**6 

        # Create table data
        table_data = [datewise_deliv['DATE1'].tolist(),[f"{x:.4f}" for x in datewise_deliv['DELIV']]]  
        row_labels = ["Date", "MKT_DELIV"] 

        # Add table below the plot
        table = plt.table(cellText=table_data, rowLabels=row_labels, cellLoc='center', loc='bottom', fontsize = 12, bbox=[0.05, -0.35, 0.99, 0.2])

        # Adjust layout to accommodate table
        plt.subplots_adjust(bottom=0.05)

        # Save plot to PDF
        pdf.savefig(fig4, bbox_inches='tight')
        plt.close(fig4)  


        # Loop over all NIFTY different indexes
        for file in os.listdir(directory):
            if file.endswith(".csv"):
                sector_name = os.path.splitext(file)[0].replace("NIFTY", "").upper()  # e.g., Bank, Commodities
                csv_path = os.path.join(directory, file)

                # Read sector file and merge
                df_merge = pd.read_csv(csv_path)
                df = main_df.merge(df_merge, on='SYMBOL', how='right')
                avg_df = df.groupby('DATE1')[['TTL_TRD_QNTY', 'DELIV_QTY', 'CLOSE_PRICE']].mean().reset_index()
                sector_delivery_data[sector_name] = avg_df

         # Plot for average delivery quantity of all nifty sectors
        sns.set(style="whitegrid")

        plt.figure(figsize=(30, 15))
        ax = plt.gca()

        # Assign a color palette but override specific sectors to white
        palette = sns.color_palette("Paired", n_colors=len(sector_delivery_data))
        white_sectors = {'COMMODITIES', 'SERVICE', 'CONSUMPTION', 'MEDIA', 'CPSE', 'MNC'}
        sector_color_map = {}
        for idx, sector in enumerate(sector_delivery_data):
            if sector in white_sectors:
                sector_color_map[sector] = 'white'
            else:
                sector_color_map[sector] = palette[idx]

        # Collect all unique dates across sectors for consistent X-axis
        all_dates = sorted(set(date for df in sector_delivery_data.values() for date in df['DATE1']))
        
        # Plot delivery quantity lines for each sector
        for sector, df_deliv in sector_delivery_data.items():
            x = df_deliv['DATE1']
            y = df_deliv['DELIV_QTY']
            color = sector_color_map[sector]

            # Plot line for different sector
            plt.plot(x, y, label=sector, linewidth=3, color=color, marker='s')

            # Determine start and end positions for adding sector labels
            start_index = all_dates.index(x.iloc[0])
            end_index = all_dates.index(x.iloc[-1])
            if start_index > 0:
                start_pos = all_dates[start_index - 1]
            else:
                start_pos = x.iloc[0]   # start_pos = all_dates[start_index - 1] if start_index > 0 else x.iloc[0]

            if end_index < len(all_dates) - 1:
                end_pos = all_dates[end_index + 1]
            else:
                end_pos = x.iloc[-1]   # end_pos = all_dates[end_index + 1] if end_index < len(all_dates) - 1 else x.iloc[-1]

            # Add text at the start
            plt.text(start_pos, y.iloc[0], sector, fontsize=14, color=color, verticalalignment='bottom', horizontalalignment='right', style = 'italic')
            # Add text after the line ends
            plt.text(end_pos, y.iloc[-1], sector, fontsize=14, color=color, verticalalignment='bottom', horizontalalignment='left', style = 'italic')

        # Create plot
        plt.xlabel('Date', fontsize=16)
        plt.ylabel('Average Delivery Quantity', fontsize=16)
        plt.title('Average Delivery Quantity Over Time by Sectors', fontsize=16, weight='bold')
        plt.xticks(ticks=range(len(all_dates)), labels=all_dates, rotation=45, fontsize=15)
        plt.yticks(fontsize=15)
        plt.grid(True, linewidth=0.5)
        plt.legend(fontsize=14)

        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # Plot individual sector with dual y-axis and data table
        for sector_name, avg_df in sector_delivery_data.items():
            # Convert date and also store as string for evenly spaced X-axis labels
            avg_df['DATE1'] = pd.to_datetime(avg_df['DATE1'])
            avg_df['DATE_STR'] = avg_df['DATE1'].dt.strftime('%Y-%m-%d')

            # Create plot for each sector    
            fig, ax1 = plt.subplots(figsize=(20, 10))

            x_labels = avg_df['DATE_STR']
            # Plot total traded and delivery quantity on left Y-axis
            ax1.plot(x_labels, avg_df['TTL_TRD_QNTY'], label='Avg. Total Traded Quantity', marker='o', color='r')
            ax1.plot(x_labels, avg_df['DELIV_QTY'], label='Avg. Delivery Quantity', marker='d', color='m')

            ax1.set_xlabel('Date', fontsize=12)
            ax1.set_ylabel('Average Quantity', fontsize=12)
            ax1.tick_params(axis='y')

            # Evenly spaced categorical X-axis
            ax1.set_xticks(x_labels)
            ax1.set_xticklabels(x_labels, rotation=45, ha='right')

            ax1.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)
            ax1.legend(loc='upper left', fontsize=12)

            # Plot close price on right Y-axis
            ax2 = ax1.twinx()
            ax2.plot(x_labels, avg_df['CLOSE_PRICE'], label='Avg. Close Price', color='g', linestyle='--', marker='s')
            ax2.set_ylabel('Average Close Price', fontsize=12)
            ax2.tick_params(axis='y')
            ax2.grid(False)

            plt.title(f'NIFTY {sector_name} SECTOR Analysis', fontsize=14)
            fig.tight_layout()

            # Add data table
            table_data = [
                x_labels.tolist(),
                [f"{x:.2f}" for x in avg_df['TTL_TRD_QNTY']],
                [f"{x:.2f}" for x in avg_df['DELIV_QTY']],
                [f"{x:.2f}" for x in avg_df['CLOSE_PRICE']]
            ]
            row_labels = ["Date", "AVG_TTL_TRD_QNTY", "AVG_DELIV_QTY", "AVG_CLOSE_PRICE"]

            plt.table(cellText=table_data, rowLabels=row_labels, cellLoc='center', loc='bottom',
                    fontsize=12, bbox=[0.05, -0.35, 0.99, 0.2])
            plt.subplots_adjust(top=0.88, bottom=0.05)

            # Saving
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    log_message("Market Sector analysis generated successfully.", log_to_file=True)
except Exception as e:
    log_message(f"Error generating PDF report: {e}", log_to_file=True)
    exit()