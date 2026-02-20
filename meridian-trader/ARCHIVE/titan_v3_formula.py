''' 
Titan V3 Formula Module
Core logic for swing and cluster detection

Swing Detection:
    SWING_HIGH: Day where HIGH > HIGH of [2 days before] AND [2 days after]
    SWING_LOW: Day where LOW < LOW of [2 days before] AND [2 days after]

Cluster Detection:
    Multiple days with highs within 0.5% → resistance cluster
    Multiple days with lows within 0.5% → support cluster
    Zone = min to max of cluster

Significant levels are those levels (swing and clusters) that are unswiped.
''' 

import numpy as np
import pandas as pd


def detect_swings(df):
    """
    Detect swing highs and lows from OHLC data
    :param df: DataFrame with columns ['Date', 'High', 'Low']
    :return: DataFrame with added columns 'Swing_High' and 'Swing_Low'
    """
    df = df.copy()
    df['Swing_High'] = False
    df['Swing_Low']  = False

    for i in range(2, len(df) - 2):
        high = df.loc[df.index[i], 'High']
        lows = df.loc[df.index[i-2:i], 'High'].tolist() + df.loc[df.index[i+1:i+3], 'High'].tolist()
        if all(high > h for h in lows):
            df.at[df.index[i], 'Swing_High'] = True
        low = df.loc[df.index[i], 'Low']
        highs = df.loc[df.index[i-2:i], 'Low'].tolist() + df.loc[df.index[i+1:i+3], 'Low'].tolist()
        if all(low < l for l in highs):
            df.at[df.index[i], 'Swing_Low'] = True
    return df


def detect_clusters(levels, threshold=0.005):
    """
    Detect clusters from a list of levels.
    :param levels: List of levels (floats) 
    :param threshold: Percentage threshold (0.005 = 0.5%)
    :return: List of clusters, where each cluster is a tuple (min, max)
    """
    levels = sorted(levels)
    clusters = []
    cluster = [levels[0]]
    for level in levels[1:]:
        if abs(level - cluster[-1]) / cluster[-1] <= threshold:
            cluster.append(level)
        else:
            if len(cluster) > 1:
                clusters.append((min(cluster), max(cluster)))
            else:
                clusters.append((cluster[0], cluster[0]))
            cluster = [level]
    if cluster:
        if len(cluster) > 1:
            clusters.append((min(cluster), max(cluster)))
        else:
            clusters.append((cluster[0], cluster[0]))
    return clusters


def get_significant_levels(df):
    """
    Combine swing levels and cluster zones that are unswiped.
    :param df: DataFrame with swing detection
    :return: Dict with 'swing_highs', 'swing_lows', 'resistance_clusters', 'support_clusters'
    """
    # Get swing levels
    swing_highs = df[df['Swing_High']]['High'].tolist()
    swing_lows  = df[df['Swing_Low']]['Low'].tolist()

    # Combine levels for clustering, for resistance and support separately
    resistance_clusters = detect_clusters(swing_highs) if swing_highs else []
    support_clusters    = detect_clusters(swing_lows)  if swing_lows else []

    # Unswept levels, assume all levels provided are significant until swept (sweep logic handled later in system)
    return {
        'swing_highs': swing_highs,
        'swing_lows': swing_lows,
        'resistance_clusters': resistance_clusters,
        'support_clusters': support_clusters
    }


if __name__ == '__main__':
    # Example usage (assuming CSV input with Date, High, Low columns)
    df = pd.read_csv('sample_data.csv')
    df = detect_swings(df)
    levels = get_significant_levels(df)
    print('Detected Levels:')
    print(levels)
