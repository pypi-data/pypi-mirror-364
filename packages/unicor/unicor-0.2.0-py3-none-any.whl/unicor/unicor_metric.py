# -*- coding: utf-8 -*-
"""
Created on Fri May 24 14:19:25 2024

@author: JohnDoe2Go
"""
import pandas as pd
from skbio.stats.composition import clr, closure

def unicor_metric(features, target, method='pearson', transformation=None):
    """
    function that computes the unicor metric for a simple featureset without a hierarchy

    Parameters
    ----------
    features : pd.Dataframe
        continuous feature set, index is sample number, columns are the features.
    target : pd.Dataframe
        continuous target variable, one column with the data, index is the sample number.

    Returns
    -------
    metric : dictionary
        features and respective unicor metrics

    """
    ### check input
    ###########################################################################
    #check type
    if not isinstance(target, (pd.DataFrame, pd.Series)):
        raise TypeError("TypeError exception thrown. Expected pandas dataframe for target")
    if not isinstance(features, (pd.DataFrame)):
        raise TypeError("TypeError exception thrown. Expected pandas dataframe for features")
    #check dimensions
    if features.ndim != 2:  
        raise ValueError("ValueError exception thrown. Expected features to have two dimensions")
    if features.shape[0] != target.shape[0]:
        raise ValueError("ValueError exception thrown. Expected features and target to have the same number of samples")
    if method not in ['pearson', 'spearman']:
        raise ValueError("Unsupported method. Choose 'pearson' or 'spearman'.")
    if transformation not in ['clr', 'relative_abundance', None]:
        raise ValueError("Unsupported transformation. Choose 'clr' or 'relative_abundance'.")
    ###########################################################################
    
    
    ### clean zero columns/rows (features that are not present in any samples)
    ###########################################################################
    features = features.loc[:, (features != 0).any(axis=0)]
    ###########################################################################
    
    ### compute unicor metric for all features
    ###########################################################################
    table = target.merge(features, left_index=True, right_index=True) #merge features and target variable
    
    ### apply transformation (inline here as you wanted)
    ###########################################################################
    if transformation is None:
        transformed_features = table
    elif transformation == 'relative_abundance':
            transformed_features = table.div(table.sum(axis=1), axis=0)
    elif transformation == 'clr':
            features_pseudo = table + 1e-6
            clr_data = clr(closure(features_pseudo))
            transformed_features = pd.DataFrame(clr_data, index=table.index, columns=table.columns)
    else:
        raise ValueError(f"Unsupported transformation: {transformation}")
###########################################################################
    
    cor_matrix = transformed_features.corr(method=method) #get correlation matrix
    metric = {} #dictionary to save results to
    
    
    for feature in cor_matrix: #for each feature
        if feature in target.columns: #skip target varialbe
            continue
        else: 
            n = len(cor_matrix[feature])
            fc_corr = cor_matrix[feature].iloc[0] #feature-target correlation
            ff_corr = (cor_matrix[feature].iloc[1:].sum()-1)/(n-(2-(1e-6))) #feature-feature correlation (-own corr and -target variable corr + epsilon to prevent zero division)
            unicor = (0.5*abs(fc_corr)) - (0.5*ff_corr) #unicor metric computation
            metric[feature] = unicor #save in dictionary
    ###########################################################################
    return metric