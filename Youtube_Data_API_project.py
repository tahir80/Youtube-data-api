#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[2]:


api_key = "AIzaSyC9IQS-O5xgXapMEv9HC-1gfSyYAlX9gmI"


# In[3]:


channel_ids = ['UCoOae5nYA7VqaXzerajD0lg']


# In[20]:


#pip install isodate


# In[25]:


from googleapiclient.discovery import build
from dateutil import parser
import pandas as pd
from IPython.display import JSON 


# In[27]:


# Data viz packages
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# In[26]:


api_service_name = "youtube"
api_version = "v3"

# Get credentials and create an API client

youtube = build(api_service_name, api_version, developerKey=api_key)


# In[6]:


def get_channel_stats(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=','.join(channel_ids))
    response = request.execute() 
    
    for i in range(len(response['items'])):
        data = dict(channelName = response['items'][i]['snippet']['title'],
                    subscribers = response['items'][i]['statistics']['subscriberCount'],
                    views = response['items'][i]['statistics']['viewCount'],
                    totalVideos = response['items'][i]['statistics']['videoCount'],
                    playlistId = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        all_data.append(data)
    
    return pd.DataFrame(all_data)


# In[7]:


playlist_id = "UUoOae5nYA7VqaXzerajD0lg"


# In[8]:


def get_video_ids(youtube, playlist_id):
    
    video_ids = []
    
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults = 50
    )
    response = request.execute()
    
    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    while next_page_token is not None:
        request = youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId = playlist_id,
                    maxResults = 50,
                    pageToken = next_page_token)
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        
    return video_ids


# In[9]:


video_ids = get_video_ids(youtube, playlist_id)


# In[10]:


def get_video_details(youtube, video_ids):
        
    all_video_info = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute() 

        for video in response['items']:
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'favouriteCount', 'commentCount'],
                             'contentDetails': ['duration', 'definition', 'caption']
                            }

            video_info = {}
            video_info['video_id'] = video['id']

            # print(video_info)
            # print(stats_to_keep.keys())

            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v] = video[k][v]
                    except:
                        video_info[v] = None

            all_video_info.append(video_info)
            
    return pd.DataFrame(all_video_info)


# In[11]:


video_df = get_video_details(youtube, video_ids)


# In[12]:


video_df.isnull().any()


# In[13]:


video_df.dtypes


# In[14]:


numeric_cols = ['viewCount', 'likeCount', 'favouriteCount', 'commentCount']


# In[15]:


video_df[numeric_cols] = video_df[numeric_cols].apply(pd.to_numeric, errors='coerce')


# In[16]:


video_df.dtypes


# In[17]:


# Publish day in the week
video_df['publishedAt'] = video_df['publishedAt'].apply(lambda x: parser.parse(x)) 
video_df['pushblishDayName'] = video_df['publishedAt'].apply(lambda x: x.strftime("%A")) 


# In[18]:


video_df


# In[21]:


# convert duration to seconds
import isodate
video_df['durationSecs'] = video_df['duration'].apply(lambda x: isodate.parse_duration(x))
video_df['durationSecs'] = video_df['durationSecs'].astype('timedelta64[s]')


# In[22]:


video_df


# In[23]:


# Add tag count
video_df['tagCount'] = video_df['tags'].apply(lambda x: 0 if x is None else len(x))


# In[24]:


video_df


# In[33]:


ax = sns.barplot(x = 'title', y = 'viewCount', data = video_df.sort_values('viewCount', ascending=False)[0:9])
plot = ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos:'{:,.0f}'.format(x/1000) + 'K'))


# In[34]:


ax = sns.barplot(x = 'title', y = 'viewCount', data = video_df.sort_values('viewCount', ascending=True)[0:9])
plot = ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos:'{:,.0f}'.format(x/1000) + 'K'))


# 

# In[36]:


sns.violinplot(video_df['viewCount'])


# In[38]:


fig, ax = plt.subplots(1,2)
sns.scatterplot(data = video_df, x = 'commentCount', y = 'viewCount', ax = ax[0])
sns.scatterplot(data = video_df, x = 'likeCount', y = 'viewCount', ax = ax[1])
plt.subplots_adjust(wspace=0.5)


# In[49]:


# Increase the figure size
plt.figure(figsize=(10, 6))  # Adjust figsize as per your preference

# Plot the histogram with adjusted bins and color
sns.histplot(data=video_df, x='durationSecs', bins=50, color='blue')

# Set the x-axis limit to zoom in on frequencies up to 2500
plt.xlim(0, 2500)


# Display the plot
plt.show()


# In[ ]:




