#!/usr/bin/env python
# coding: utf-8


from sklearn.ensemble import RandomForestRegressor
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


# Either one of the MinMaxScaling or StandardScaling function can be used

scaler_min_max = MinMaxScaler()
scaler_standard = StandardScaler()
def MinMaxScaling(feature_matrix):
    global scaler_min_max
    scaler_min_max.fit(feature_matrix)
    return scaler_min_max.transform(feature_matrix)
def StandardScaling(feature_matrix):
    global scaler_standard
    scaler_standard.fit(feature_matrix)
    print('scaling shape',scaler_standard.mean_.shape)
    return scaler_standard.transform(feature_matrix)


# """##DREAMER dataset
# 1> Valence - features selected
# > best_features_list = ['ShannonRes_gamma','ShannonRes_beta','HjorthMob','HjorthComp','bandPwr_alpha','stdDev','ShannonRes_alpha','bandPwr_beta','rasm_beta','dasm_beta','dasm_alpha']
# 
# 2> Arousal - feature selected
# > best_features_list = ['ShannonRes_gamma','HjorthComp','ShannonRes_beta','dasm_alpha','rasm_alpha','HjorthMob','bandPwr_alpha','stdDev','bandPwr_beta']
# """


# now for incremental learning we need to segregate data of subjects
def segregate_data_of_subjects(feature_matrix,total_subjects,sfreq = 128):
    '''
    returns a dictionary which contains the samples data only corresponding to particular subjects of feature matrix
    '''
    # parameters :-
            # feature_matrix :- Vector containing the features mentioned above subject wise, to be used for cross validation
            # total_subjects :- Total number of subjects in the study
            # sfreq :- sampling frequency of the EEG data
    # returns :-
            # subject_indexes :- Subject wise features in a dictionary form

    total_samples = feature_matrix.shape[0]
    subject_indexes = {}
    samples_per_subject = total_samples//total_subjects
    for i in range(total_subjects):
        subject_name = 'subject_' + str(i+1)
        subject_indexes[subject_name] = feature_matrix[samples_per_subject*i:samples_per_subject*(i+1),:]
  
    return subject_indexes





# now defining a function which carries out the incremenatal learning algo
def training_phase(model,feature_matrix,Y,subject_indexes,number_of_subjects,total_subjects,rmse_score,test_subject):
    # parameters :-
            # model :- The training model to be used (SVR in this case)
            # featrue_matrix :- feature matrix obtained in the above function
            # Y :- The Valence and Arousal values as entered by the subjects
            # subject_indexes :-Subject wise features in a dictionary form
            # number_of_subjects :- Total number of subjects in the study
            # total_subjects :- Total number of subjects in the study
            # rmse_score :- RMSE of the previous iterations 
            # test_subject :- Cross validation test subject list

    # returns :-
            # rmse_score :- Array of rmse scores over the iterations, updated with the rmse score of the current iteration
            # test_subject :- Updated Cross validation test subject list
    no_of_features = feature_matrix.shape[1]
    X = np.empty((0,no_of_features))
    print('training on subject_no:',end = ' ')

    #create a feature matrix containing data upto subjects given by the number number_of_subjects
    #for eg if number of subject ==4 , data of first 4 subjects will be taken and a feature matrix made out of it to feed to the ml model
  
    for subject in range(number_of_subjects):
        print(subject+1,end = ' ')
        subject_name = 'subject_'+str(subject+1)
        subject_data = subject_indexes[subject_name]
        X = np.append(X,subject_data,axis=0)
    print(' ')

    #apply a MinMax scaling to the current iteration feature matrix
    X = MinMaxScaling(X)

    #now we also need to extract the valence arousal data for the corresponding subject
    y = np.empty((0))
    total_samples = feature_matrix.shape[0]
    samples_per_subject = total_samples//total_subjects
    for subject in range(number_of_subjects):
        y = Y[:samples_per_subject*(number_of_subjects)]

  
    print('shape of X is :',X.shape)
    print('shape of y is  :',y.shape)

    #shuffling data randomly to feed to model
    X,y = shuffle(X,y,random_state = 0)

    #doing a train test split of 80:20
    X_train,X_test,y_train,y_test = train_test_split(X,y,random_state=0,test_size=0.2)

    #training_model
    model = model.fit(X_train,y_train)

    #testing_model
    y_predict = model.predict(X_test)


    #calculating rmse values for valence and arousal using model fitted for current iteration
    y_rms = np.sqrt(mean_squared_error(y_test,y_predict))
    print('rms on y :',y_rms)
    print('')
    rmse_score.append(y_rms)
    test_subject.append(subject_name)

    return rmse_score,test_subject





def driver_code(save):
    
    # Function to load the features, then train the regressor and will give the validation and test plot


    #extracting file data corresponding to  valence features
    # best_features_list = ['ShannonRes_gamma','ShannonRes_beta','HjorthMob','HjorthComp','bandPwr_alpha','stdDev','ShannonRes_alpha','bandPwr_beta','rasm_beta','dasm_beta','dasm_alpha']
    feature_path = os.getcwd() + '/DREAMER/data_extracted/featuresDict/'
    
    ShannonRes_gamma_v = np.load(feature_path + 'ShannonRes_sub_bands_gamma_1_1.npz')
    ShannonRes_beta_v = np.load(feature_path + 'ShannonRes_sub_bands_beta_1_1.npz')
    HjorthMob_v = np.load(feature_path + 'Hjorth_mobilty_1_1.npz')
    HjorthCom_v = np.load(feature_path + 'Hjorth_complexity_1_1.npz')
    bandPwr_alpha_v = np.load(feature_path + 'bandPwr_alpha_1_1.npz')
    stdDev_v = np.load(feature_path + 'stdDev_1_1.npz')
    ShannonRes_alpha_v = np.load(feature_path + 'ShannonRes_sub_bands_alpha_1_1.npz')
    bandPwr_beta_v = np.load(feature_path + 'bandPwr_beta_1_1.npz')
    rasm_beta_v = np.load(feature_path + 'rasm_beta_1_1.npz')
    dasm_beta_v = np.load(feature_path + 'dasm_beta_1_1.npz')
    dasm_alpha_v = np.load(feature_path + 'dasm_alpha_1_1.npz')


    # creating a feature matrix out of all feature data for valence
    feature_matrix_valence = np.empty((0,188370))
    feature_matrix_valence = np.append(feature_matrix_valence,ShannonRes_gamma_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,ShannonRes_beta_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,HjorthMob_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,HjorthCom_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,bandPwr_alpha_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,stdDev_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,ShannonRes_alpha_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,bandPwr_beta_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,rasm_beta_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,dasm_beta_v['features'],axis =0)
    feature_matrix_valence = np.append(feature_matrix_valence,dasm_alpha_v['features'],axis =0)
    feature_matrix_valence = feature_matrix_valence.T #  feature matrix becomes of shape 188370 x 84 i.e (samples X features per sample)

    #remove NaN features
    if np.isnan(feature_matrix_valence).any():
        feature_matrix_valence = np.nan_to_num(feature_matrix_valence,nan=0)

    #set datatype of feature matrix
    feature_matrix_valence = feature_matrix_valence.astype(np.float32)

    # extracting valence  values for each sample
    Y_val = HjorthMob_v['Y'][:,0]#all features have same valnece labels
  

  
    #extracting file data corresponding to  arousal features
    # > best_features_list = ['ShannonRes_gamma','HjorthComp','ShannonRes_beta','dasm_alpha','rasm_alpha','HjorthMob','bandPwr_alpha','stdDev','bandPwr_beta']
    ShannonRes_gamma_a = np.load(feature_path + 'ShannonRes_sub_bands_gamma_1_1.npz')
    HjorthCom_a = np.load(feature_path + 'Hjorth_complexity_1_1.npz')
    ShannonRes_beta_a = np.load(feature_path + 'ShannonRes_sub_bands_beta_1_1.npz')
    dasm_alpha_a = np.load(feature_path + 'dasm_alpha_1_1.npz')
    rasm_alpha_a = np.load(feature_path + 'rasm_alpha_1_1.npz')
    HjorthMob_a = np.load(feature_path + 'Hjorth_mobilty_1_1.npz')
    bandPwr_alpha_a = np.load(feature_path + 'bandPwr_alpha_1_1.npz')
    stdDev_a = np.load(feature_path + 'stdDev_1_1.npz')
    bandPwr_beta_a = np.load(feature_path + 'bandPwr_beta_1_1.npz')
  
    #creating feature matrix for all feature data for arousal
    feature_matrix_arousal = np.empty((0,188370))
    feature_matrix_arousal = np.append(feature_matrix_arousal,ShannonRes_gamma_a['features'],axis = 0)
    feature_matrix_arousal = np.append(feature_matrix_arousal,HjorthCom_a['features'],axis = 0)
    feature_matrix_arousal = np.append(feature_matrix_arousal,ShannonRes_beta_a['features'],axis = 0)
    feature_matrix_arousal = np.append(feature_matrix_arousal,dasm_alpha_a['features'],axis = 0)
    feature_matrix_arousal = np.append(feature_matrix_arousal,rasm_alpha_a['features'],axis = 0)
    feature_matrix_arousal = np.append(feature_matrix_arousal,HjorthMob_a['features'],axis = 0)
    feature_matrix_arousal = np.append(feature_matrix_arousal,bandPwr_alpha_a['features'],axis = 0)
    feature_matrix_arousal = np.append(feature_matrix_arousal,stdDev_a['features'],axis = 0)
    feature_matrix_arousal = np.append(feature_matrix_arousal,bandPwr_beta_a['features'],axis = 0)
    feature_matrix_arousal = feature_matrix_arousal.T

    #remove NaN features
    if np.isnan(feature_matrix_arousal).any():
        feature_matrix_arousal = np.nan_to_num(feature_matrix_arousal,nan=0)

    #set datatype of feature matrix
    feature_matrix_arousal = feature_matrix_arousal.astype(np.float32)

    #transpose feature matrix to prepare X
    # X = pd.DataFrame(featureMatrix.T)
    #replace infinity with NaN value and fill it with zero
    # X = X.replace([np.inf, -np.inf], np.nan)
    # X = X.fillna(0)
    # X = X.astype(np.float32)

    #extracting arousal values for
    Y_aro = HjorthMob_a['Y'][:,1]#all features have same arousal labels

    model = RandomForestRegressor()#initializing support vector regressor for training

    #running incremental learning loop for valence
    print('')
    print('Incremental training for valence')
    print('')
    test_subject = []
    rmse_val = []
    subject_indexes_valence = segregate_data_of_subjects(feature_matrix_valence,23,128)
    i = 1
    while i <= 23:
        rmse_val,test_subject= training_phase(model,feature_matrix_valence,Y_val,subject_indexes_valence,i,23,rmse_val,test_subject)
        i+=1

    #running incremental learning loop for arousal
    print('')
    print('Incremental training for arousal ')
    print(' ')
  
    test_subject = []
    rmse_aro = []
    subject_indexes_arousal = segregate_data_of_subjects(feature_matrix_arousal,23,128)
    i=1
    while i<=23:
        rmse_aro,test_subject = training_phase(model,feature_matrix_arousal,Y_aro,subject_indexes_arousal,i,23,rmse_aro,test_subject)
        i+=1

  
    fig,axe = plt.subplots(1,1,figsize = (40,20))
    axe.plot(test_subject,rmse_val,color='r',label = 'rms valence')
    axe.plot(test_subject,rmse_aro,color = 'g',label = 'rms arousal')
    axe.set_xlabel('trained upto subject')
    axe.set_ylabel('rmse')
    axe.set_title('support vector regressor')
    axe.legend(loc='upper right')
    df = pd.DataFrame([rmse_val,rmse_aro],columns = test_subject,index = ['valence rms','arousal rms'])
    print(df)

    if save == 'y':
        plt.savefig(os.getcwd() + '/dreamer_incremental_learning.svg',format = "svg")
        df.to_csv(os.getcwd() + '/dreamer_incremental_learning.csv')


if __name__ == '__main__':
    driver_code(save = 'y')

