import pandas as pd
import plotly.express as px
import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch
import seaborn as sns
from dummydata import generate_dummy_passes

# Set page configuration
st.set_page_config(page_title="TMB FC", layout="wide", initial_sidebar_state="expanded")

# Load data
@st.cache_data
def load_data():

    # 1. Load data from excel
    excel_file = 'data/tmb_fc_data.xlsx'
    player_info = pd.read_excel(excel_file, sheet_name='player_info')
    goals = pd.read_excel(excel_file, sheet_name='goals')
    assists = pd.read_excel(excel_file, sheet_name='assists')
    club_info = pd.read_excel(excel_file, sheet_name='club_info')

    # create supporting tables
    df_pos_count = player_info.groupby(['primary_position'])['primary_position'].count() # Get the number of players in each position
    passes_data = generate_dummy_passes()

    return player_info, goals, assists, club_info, df_pos_count, passes_data

player_info, goals, assists, club_info, df_pos_count, passes_data = load_data()

# Set up Streamlit UI
def main():
    # Navigation bar
    st.sidebar.title("Navigation")
    pages = ["Team Lineup", "Player Statistics", "Club Overview"]
    page = st.sidebar.radio("Go to", pages)

    if page == "Team Lineup":

        col1, col2 = st.columns([1, 5])
        with col1:
            st.title("TMB FC")
        with col2:
            st.image("images/tmb_logo.png", width=140)

        with st.expander("Team Lineup", expanded=True, icon="⚽"):
            # create a dictionary for buttons
            button_players = dict()
            # Dynamically generate buttons for each player on the team.
            for pos in ['FWD','MID','DEF','GK']:
                with st.container(border=True):
                    st.subheader(pos)
                    if pos in df_pos_count.index:
                        filtered_players = player_info[player_info['primary_position']==pos]
                        filtered_players.reset_index(inplace=True, drop=True)
                        ncol = len(filtered_players)
                        cols = st.columns(ncol, vertical_alignment ="center")
                        for idx, row in filtered_players.iterrows():
                            with cols[idx]:
                                button_players[row['player_name']] = st.button(row['player_name'], type="primary")
        
        with st.expander("Player Summary", expanded=True, icon="🙎‍♂️"):
            if True in button_players.values():
                # Find the key corresponding to the value
                player = next((k for k, v in button_players.items() if v == True), None)

                # Generate Statistics based of the player button selected
                if button_players[player]:
                    generate_player_stats(player)
                    
            else:
                st.markdown("Select a player from the team lineup and view their summary.")


    if page == "Player Statistics":
        st.title("Player Statistics")

        # Select player
        player_names = player_info['player_name'].unique()
        selected_player = st.selectbox("Select a player", player_names)

        # Generate Statistics
        generate_player_stats(selected_player)

    if page == "Club Overview":
        club_overview_page()


def generate_player_stats(selected_player):
    """
    This function generates the statistics for an individual player
    """
    # Filter data for the selected player
    goals_player = goals[['Date', selected_player]].rename(columns={selected_player: 'Goals'})
    assists_player = assists[['Date', selected_player]].rename(columns={selected_player: 'Assists'})

    # Merge goals and assists data
    player_data = pd.merge(goals_player, assists_player, on='Date', how='outer').fillna(0)

    # Retrieve Metrics
    total_goals = int(player_data['Goals'].sum())
    total_assists = int(player_data['Assists'].sum())

    # Retrieve Info
    main_pos = player_info[player_info['player_name']==selected_player]['primary_position'].iloc[0]
    sec_pos = player_info[player_info['player_name']==selected_player]['secondary_position'].iloc[0]
    kit_num = player_info[player_info['player_name']==selected_player]['number'].iloc[0]

    # kit number can sometimes be a string value 'TBC'
    if isinstance(sec_pos, float):
        kit_num = str(int(kit_num))

    fav_club = player_info[player_info['player_name']==selected_player]['fav_club'].iloc[0]

    # Display player stats
    st.header(f"Summary of {selected_player}")

    col1, col2, _, _, _= st.columns(5)

    with col1:
        if isinstance(sec_pos, float): # if there is no sec position, it will return true.
            st.markdown(f"Field Position:<br>{main_pos}", unsafe_allow_html=True)
        else:
            st.markdown(f"Field Positions:<br>{main_pos} | {sec_pos}", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"Favourite Team:<br>{fav_club}", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Goals", total_goals, border=True)
    col2.metric("Assists", total_assists, border=True)
    col3.metric("Squad No.", kit_num, border=True)

    # Time series chart
    fig = px.line(
        player_data,
        x='Date',
        y=['Goals', 'Assists'],
        title=f"Goals and Assists Over Time for {selected_player}",
        labels={"value": "Count", "Date": "Match Date"},
    )
    st.plotly_chart(fig)

    st.markdown('***')

    ### Heatmap of Passes ###

    player_passes = passes_data[passes_data['player']==selected_player]
    fig ,ax = plt.subplots(figsize=(13.5,8))
    fig.set_facecolor('#22312b')
    ax.patch.set_facecolor('#22312b')

    #this is how we create the pitch
    pitch = Pitch(pitch_type='statsbomb', 
                pitch_color='#22312b', 
                line_color='#c7d5cc',
                )

    #Draw the pitch on the ax figure as well as invert the axis for this specific pitch
    pitch.draw(ax=ax)
    plt.gca().invert_yaxis()

    #Create the heatmap
    kde = sns.kdeplot(
            x=player_passes['x'],
            y=player_passes['y'],
            fill = True,
            shade_lowest=False,
            alpha=.5,
            n_levels=10,
            cmap = 'magma', ax=ax
    )

    #use a for loop to plot each pass
    # for x in range(len(df['x'])):
    #     if df['outcome'][x] == 'Successful':
    #         plt.plot((df['x'][x],df['endX'][x]),(df['y'][x],df['endY'][x]),color='green')
    #         plt.scatter(df['x'][x],df['y'][x],color='green')
    #     if df['outcome'][x] == 'Unsuccessful':
    #         plt.plot((df['x'][x],df['endX'][x]),(df['y'][x],df['endY'][x]),color='red')
    #         plt.scatter(df['x'][x],df['y'][x],color='red')
            
    plt.xlim(0,120)
    plt.ylim(0,80)

    plt.title(f"{selected_player}'s Heat Map From Recent Games",color='white',size=20)

    # heatmap = generate_heatmap(passes_data, selected_player)
    st.pyplot(fig)


def club_overview_page():

    club_name = club_info['team'].iloc[0]
    st.title(f"Club Overview: {club_name}")

    games_played = club_info['games_played'].iloc[0]
    win = club_info['win'].iloc[0]
    draw = club_info['draw'].iloc[0]
    loss = club_info['loss'].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("No. of games played", games_played, border=True)
    col2.metric("Wins", win, border=True)
    col3.metric("Draws", draw, border=True)
    col4.metric("Losses", loss, border=True)

    # Get all the goals scored
    df_players_only = goals.drop('Date', axis=1)
    total_goals = int(df_players_only.sum().sum())

    # Get all the assists made
    df_players_only = assists.drop('Date', axis=1)
    total_assists = int(df_players_only.sum().sum())

    # Get the count of players in the club
    num_players = int(len(player_info))

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Goals", total_goals, border=True)
    col2.metric("Total Assists", total_assists, border=True)
    col3.metric("No. of Players", num_players, border=True)

    # Filter data for the selected player
    # Calculate the total goals for each row (ignoring NaN values)
    all_goals, all_assists = goals.copy(), assists.copy()
    all_goals['Total Goals'] = all_goals.iloc[:, 1:-1].sum(axis=1)
    all_assists['Total Assists'] = all_assists.iloc[:, 1:-1].sum(axis=1)

    # reduce data
    all_goals = all_goals[['Date', 'Total Goals']]
    all_assists = all_assists[['Date', 'Total Assists']]

    # Merge goals and assists data
    all_data = pd.merge(all_goals, all_assists, on='Date', how='outer').fillna(0)

    # Time series chart
    fig = px.line(
        all_data,
        x='Date',
        y=['Total Goals', 'Total Assists'],
        title=f"Goals and Assists Over Time",
        labels={"value": "Count", "Date": "Match Date"},
    )
    st.plotly_chart(fig)


if __name__ == "__main__":
    main()
