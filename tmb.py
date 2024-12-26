import pandas as pd
import plotly.express as px
import streamlit as st
from st_social_media_links import SocialMediaIcons
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch
import seaborn as sns
import random
from dummydata import generate_dummy_passes

# Set page configuration
st.set_page_config(page_title="TMB FC", layout="wide", initial_sidebar_state="collapsed")

# Load data
@st.cache_data(ttl=86400) # cached expires every 24hrs
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
    pages = ["Home", "Team Lineup", "Player Statistics", "Club Overview", "Media"]
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
            # create a dict of quotes to use about the different positions in football
            positions_quotes = {'FWD': ['They spend most of the game doing nothing 🙃', 
                                        "They won't come back to defend 😿", "Glory hunters 😼"],
                                'MID': ['Their job is to manufacture and execute goal scoring opportunities for themselves or their teammates 🤖',
                                        "Sorry, but we don't play tiki taka 😹",
                                        'Pressure is for tyres! 😎'],
                                'DEF': ["They clean up everyone else’s mess and still get blamed 🤣",
                                        "They're better than Harry Maguire 😗",
                                        'Just park the bus 🚌'],
                                'GK': ["He's a keeper 😉", "The hardest position in the team 💀",
                                       "Why didn't you save that? 🙄"]}
            # Dynamically generate buttons for each player on the team.
            for pos in ['FWD','MID','DEF','GK']:
                with st.container(border=True):
                    st.subheader(pos)
                    st.write(f'*{random.choice(positions_quotes[pos])}*') # pick a random quote
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
                    generate_player_stats(player, page)
                    
            else:
                st.markdown("Select a player from the team lineup and view their summary.")

    if page == "Player Statistics":
        st.title("Player Statistics")

        # Select player
        player_names = player_info['player_name'].unique()
        selected_player = st.selectbox("Select a player", player_names)

        # Generate Statistics
        generate_player_stats(selected_player, page)

    if page == "Club Overview":
        club_overview_page()

    if page == "Media":
        st.markdown("**Check out more of our videos on Youtube, Tiktok & Instagram!**")
        # Add video
        with st.container(border=True):
            VIDEO_URL = "https://www.youtube.com/watch?v=-elKH4hiRz4"
            st.video(VIDEO_URL)
            st.divider()
            VIDEO_URL = "https://www.youtube.com/watch?v=SnlPQPLB1yk"
            st.video(VIDEO_URL)
        st.markdown('***')        
        social_media()

    if page == "Home":
        home_page()


def generate_player_stats(selected_player, page):
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
    player_rating = player_info[player_info['player_name']==selected_player]['player_rating'].iloc[0]
    player_desc = player_info[player_info['player_name']==selected_player]['description'].iloc[0]
    comparison_to_real_players = player_info[player_info['player_name']==selected_player]['comparison_to_real_players'].iloc[0]

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

    # Add fun facts
    with st.container(border=True):
        st.markdown('**Player description:**')
        st.write(player_desc)
        st.write(f'*Comparable players: {comparison_to_real_players}*')

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
    fig.set_facecolor('#1C1C1C')
    ax.patch.set_facecolor('#1C1C1C')

    #this is how we create the pitch
    pitch = Pitch(pitch_type='statsbomb', 
                pitch_color='#4ccf4c', 
                line_color='#eeffee',
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

    plt.xlim(0,120)
    plt.ylim(0,80)
    # plt.title(f"{selected_player}'s Heat Map From Recent Games",color='white',size=20)

    st.markdown(f"**{selected_player}'s Heat Map From Recent Games**")
    
    if page == "Player Statistics":
        st.write("*Green - Successful passes. Red - Unsuccessful passes.*")
        # use a for loop to plot each pass
        for x in range(len(player_passes['x'])):
            if player_passes['outcome'][x] == 'Successful':
                plt.plot((player_passes['x'][x],player_passes['endX'][x]),(player_passes['y'][x],player_passes['endY'][x]),color='green')
                plt.scatter(player_passes['x'][x],player_passes['y'][x],color='green')
            if player_passes['outcome'][x] == 'Unsuccessful':
                plt.plot((player_passes['x'][x],player_passes['endX'][x]),(player_passes['y'][x],player_passes['endY'][x]),color='red')
                plt.scatter(player_passes['x'][x],player_passes['y'][x],color='red')
        
    st.pyplot(fig)

def melt_and_rank(data):
    """
    To help to transform the goals and assists data and rank the players.
    """
    # Melting the DataFrame
    df = pd.melt(data, id_vars=["Date"], var_name="Name", value_name="Value")
    # Group by 'Name' and sum the 'Value' column
    df = df.groupby("Name", as_index=False)["Value"].sum()
    # Sort by total goals in descending order. Top 5 only.
    df = df.sort_values(by="Value", ascending=False).head(5)
    return df

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

    with st.expander(label='View goals & assists across matches', expanded=True):
        # Time series chart
        fig = px.line(
            all_data,
            x='Date',
            y=['Total Goals', 'Total Assists'],
            title=f"Goals and Assists Over Time",
            labels={"value": "Count", "Date": "Match Date"},
        )
        st.plotly_chart(fig)
    
    with st.expander(label='View top player contributions', expanded=True):

        top_scorers = melt_and_rank(goals)
        top_assisters = melt_and_rank(assists)

        col1, col2 = st.columns(2)

        with col1:
            # Plot horizontal bar chart using Plotly
            fig = px.bar(
                top_scorers,
                x="Value",  # Total goals
                y="Name",  # Player names
                orientation="h",  # Horizontal orientation
                title="Top 5 Players with Goals",
                labels={"Value": "Total Goals", "Name": "Player"},
                # color="Value",  # Color by total goals
                # color_continuous_scale="YlOrBr"  # Yellow to brown color scale
            )
            # Update layout for better visualization
            fig.update_layout(
                xaxis_title="Total Goals",
                yaxis_title="Player",
                yaxis=dict(categoryorder="total ascending"),  # Sort y-axis by total goals
                template="plotly_dark"  # Dark theme
            )

            fig.update_traces(marker_color='#00ff80')

            # Display in Streamlit
            st.plotly_chart(fig)

        with col2:
            # Plot horizontal bar chart using Plotly
            fig = px.bar(
                top_assisters,
                x="Value",  # Total goals
                y="Name",  # Player names
                orientation="h",  # Horizontal orientation
                title="Top 5 Players with Assists",
                labels={"Value": "Total Assists", "Name": "Player"},
                # color="Value",
                # color_continuous_scale="YlOrBr"
            )
            # Update layout for better visualization
            fig.update_layout(
                xaxis_title="Total Assists",
                yaxis_title="Player",
                yaxis=dict(categoryorder="total ascending"),  # Sort y-axis by total goals
                template="plotly_dark"  # Dark theme
            )

            fig.update_traces(marker_color='#00ff80')

            # Display in Streamlit
            st.plotly_chart(fig)

def social_media():
    social_media_links = [
    "https://www.youtube.com/@TMBFootballTV",
    "https://www.instagram.com/tmbfootballtv/",
    "https://www.tiktok.com/@tmbfootballtv?_t=8sWmr46Q86T&_r=1"
    ]
    social_media_icons = SocialMediaIcons(social_media_links)
    social_media_icons.render()

def home_page():
    """
    This function creates the content for the "Home" page.
    """
    st.title("Welcome to TMB FC")

    # Team Logo and Name
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("images/tmb_logo.png", width=140)  # Make sure the path is correct
    with col2:
        st.subheader("TMB FC: A Brief Introduction")

    # Team Summary and History
    st.markdown("""
        TMB FC is a passionate and dedicated football club founded in 2023. 
        We are committed to developing talented players and fostering a strong sense of community.

        For example:
        *   Founded in 2023 by twins Khalis & Danish and their group of friends who shared a love for the beautiful game.
        *   We compete in the TMB League and are known for our attacking style of play.
        *   Our mission is to provide a positive and supportive environment for players of all ages and abilities.
    """)

    # How to Use the App
    st.subheader("Navigating the Site")
    st.markdown("""
        Use the sidebar on the left to explore different sections of the app:

        *   **Team Lineup:** View the current team roster, player positions, and fun facts about each player. Click on a player's button to view their individual statistics and a heatmap of their passes.
        *   **Player Statistics:** Explore detailed statistics for each player, including goals, assists, and performance over time. Select a player from the dropdown menu to view their information.
        *   **Club Overview:** Get an overview of the club's performance, including games played, wins, losses, draws, total goals, assists, and the number of players. You can also see a graph of the club's goals and assists over time.
        *   **Media:** Check out our latest videos and connect with us on our social media platforms.

    """)

    st.subheader("Follow Us")
    social_media()


if __name__ == "__main__":
    main()
