from random import randint
import sys
sys.path.append('../Backend/Conversions')
import convertt

def predict_rain(suburb):
    """
    Predict the probability of raining tomorrow for one location
    
    Input:
        id: clusterid (location)
    Output:
        prob_rain: probability of rain tomorrow on the selected location (cluster_id)
    """

    return randint(0,100)

def predict_rains(suburblist):
    """
    Predict the probability of raining tomorrow for multiple locations

    Input:
        ids: list of clusterid (locations)
    Output:
        prob_dict: dictionary containing clusterid and the probablity of raining tmr for that id
    """
    prob_dict = {}
    for suburb in suburblist:
        prob = predict_rain(id)
        prob_dict.update({suburb:prob})
    
    return prob_dict