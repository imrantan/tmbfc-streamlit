import pandas as pd
import random
# import matplotlib.pyplot as plt
# from mplsoccer.pitch import Pitch
# import seaborn as sns

# Read in the data. Use this real data as a baseline to create dummy data.
df = pd.read_csv('data/messibetis.csv')
df = df[['player','x','y','outcome','endX','endY']]

# Get all the player names
excel_file = 'data/tmb_fc_data.xlsx'
player_info = pd.read_excel(excel_file, sheet_name='player_info')
player_pos = player_info[['player_name','primary_position']]

def generate_dummy_passes():
    """
    Generates coordinates for dummy passes
    """
    all_players_passes = pd.DataFrame()

    for _, row in player_pos.iterrows():
        if row['primary_position']=='FWD':
            df_temp = df.copy()
            # Change the player name
            df_temp['player'] = row['player_name']

            # Randomise coordinates
            df_temp['x'] = df_temp['x'].apply(lambda i: random.randint(-10, 10)+i if i<100 and i>10 else random.randint(1, 100))
            df_temp['y'] = df_temp['y'].apply(lambda i: random.randint(-10, 10)+i if i<100 and i>10 else random.randint(1, 100))
            df_temp['endX'] = df_temp['endX'].apply(lambda i: random.randint(-10, 10)+i if i<100 and i>10 else random.randint(1, 100))
            df_temp['endY'] = df_temp['endY'].apply(lambda i: random.randint(-10, 10)+i if i<100 and i>10 else random.randint(1, 100))
        
        if row['primary_position']=='MID':
            df_temp = df.copy()
            # Change the player name
            df_temp['player'] = row['player_name']

            # Randomise coordinates
            df_temp['x'] = df_temp['x'].apply(lambda i: random.randint(-20, -5)+i if i>20 else random.randint(1, 90))
            df_temp['y'] = df_temp['y'].apply(lambda i: random.randint(-20, -5)+i if i>20 else random.randint(1, 90))
            df_temp['endX'] = df_temp['endX'].apply(lambda i: random.randint(-20, -5)+i if i>20 else random.randint(1, 90))
            df_temp['endY'] = df_temp['endY'].apply(lambda i: random.randint(-20, -5)+i if i>10 else random.randint(1, 90))

        if row['primary_position']=='DEF':
            df_temp = df.copy()
            # Change the player name
            df_temp['player'] = row['player_name']

            # Randomise coordinates
            df_temp['x'] = df_temp['x'].apply(lambda i: random.randint(-40, -20)+i if i>40 else random.randint(1, 65))
            df_temp['y'] = df_temp['y'].apply(lambda i: random.randint(-40, -20)+i if i>40 else random.randint(1, 65))
            df_temp['endX'] = df_temp['endX'].apply(lambda i: random.randint(-40, -20)+i if i>40 else random.randint(1, 65))
            df_temp['endY'] = df_temp['endY'].apply(lambda i: random.randint(-40, -20)+i if i>40 else random.randint(1, 65))

        if row['primary_position']=='GK':
            df_temp = df.copy()
            # Change the player name
            df_temp['player'] = row['player_name']

            # Randomise coordinates
            df_temp['x'] = df_temp['x'].apply(lambda i: random.randint(-40, -20)+i if i>10 else random.randint(1, 65))
            df_temp['y'] = df_temp['y'].apply(lambda i: random.randint(-40, -20)+i if i>40 else random.randint(1, 65))
            df_temp['endX'] = df_temp['endX'].apply(lambda i: random.randint(-40, -20)+i if i>40 else random.randint(1, 65))
            df_temp['endY'] = df_temp['endY'].apply(lambda i: random.randint(-40, -20)+i if i>40 else random.randint(1, 65))


        # Randomise outcome
        pass_percentage = random.randint(10, 50)
        df_temp['outcome'] = df_temp['outcome'].apply(lambda i: "Successful" if random.randint(1, 100)>=pass_percentage else "Unsuccessful")

        all_players_passes = pd.concat([all_players_passes,df_temp])


    # Adjust the coordinates to fit the heatmap
    all_players_passes['x'] = all_players_passes['x']*1.2
    all_players_passes['y'] = all_players_passes['y']*.8
    all_players_passes['endX'] = all_players_passes['endX']*1.2
    all_players_passes['endY'] = all_players_passes['endY']*.8

    return all_players_passes


# def generate_heatmap(df_input, player_name):
#     df = df_input[df_input['player']==player_name]
#     fig ,ax = plt.subplots(figsize=(13.5,8))
#     fig.set_facecolor('#22312b')
#     ax.patch.set_facecolor('#22312b')

#     #this is how we create the pitch
#     pitch = Pitch(pitch_type='statsbomb', 
#                 pitch_color='#22312b', 
#                 line_color='#c7d5cc',
#                 )

#     #Draw the pitch on the ax figure as well as invert the axis for this specific pitch
#     pitch.draw(ax=ax)
#     plt.gca().invert_yaxis()

#     #Create the heatmap
#     kde = sns.kdeplot(
#             x=df['x'],
#             y=df['y'],
#             fill = True,
#             shade_lowest=False,
#             alpha=.5,
#             n_levels=10,
#             cmap = 'magma', ax=ax
#     )

#     #use a for loop to plot each pass
#     # for x in range(len(df['x'])):
#     #     if df['outcome'][x] == 'Successful':
#     #         plt.plot((df['x'][x],df['endX'][x]),(df['y'][x],df['endY'][x]),color='green')
#     #         plt.scatter(df['x'][x],df['y'][x],color='green')
#     #     if df['outcome'][x] == 'Unsuccessful':
#     #         plt.plot((df['x'][x],df['endX'][x]),(df['y'][x],df['endY'][x]),color='red')
#     #         plt.scatter(df['x'][x],df['y'][x],color='red')
            
#     plt.xlim(0,120)
#     plt.ylim(0,80)

#     plt.title('Player Heat Map From Recent Games',color='white',size=20)



