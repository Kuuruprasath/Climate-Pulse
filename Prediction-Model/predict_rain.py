from random import randint

def predict_rain(id):
    """
    Input:
        id: clusterid (location)
    Output:
        prob_rain: probability of rain tomorrow on the selected location (cluster_id)
    """

    return randint(0,100)

def predict_rains(ids):
    """
    Input:
        ids: list of clusterid (locations)
    Output:
        prob_dict: dictionary containing clusterid and the probablity of raining tmr for that id
    """
    prob_dict = {}
    for id in ids:
        prob = predict_rain(id)
        prob_dict.update({id:prob})
    
    return prob_dict
