#Helper fcns for Data Preprocessing
import numpy as np
import pandas as pd
import pywt
import pathlib
import pickle #to save files
from itertools import product
from scipy.stats import skew, kurtosis, entropy
from scipy.signal import butter, welch, filtfilt, resample
import math
# import nolds
from sklearn import preprocessing

def fivesensorfeatures(actdictaccgyr):
    """
    Extract features from 5 sensors using accelerometer and gyroscope data.
    :param actdictaccgyr is one subject's raw data in dataframe format
    """
    locations = ['sacrum', 'distal_lateral_shank_right', 'distal_lateral_shank_left',
                 'posterior_forearm_right', 'posterior_forearm_left']
    fivesensordf = pd.DataFrame()
    for task in actdictaccgyr.keys():
        for location in locations:
            print('task ',task,' and location ',location)
            clip_data = gen_clips_merged(actdictaccgyr,task,location,clipsize=10000,verbose=True)
            feature_extraction131(clip_data)
            tempdf = aggregateAcc(clip_data)

            ## add task and location as a column
            tempdf.insert(0, 'task', task)
            tempdf.insert(1, 'location', location)

            fivesensordf = pd.concat([fivesensordf,tempdf], ignore_index=True)
            
    return fivesensordf

def allsensorfeatures(actdictaccgyr):
    """
    Extract features from all sensors using accelerometer data only.
    :param actdictaccgyr is one subject's raw data in dataframe format
    """
    locations = ['tibialis_anterior_left', 'gastrocnemius_right', 'sacrum', 'distal_lateral_shank_right', 
             'tibialis_anterior_right', 'posterior_forearm_right', 'bicep_right', 'rectus_femoris_left', 
             'biceps_femoris_right', 'posterior_forearm_left', 'biceps_femoris_left', 'gastrocnemius_left', 
             'bicep_left', 'medial_chest', 'distal_lateral_shank_left', 'rectus_femoris_right']
    allsensordf = pd.DataFrame()
    for task in actdictaccgyr.keys():
        for location in locations:
            print('task ',task,' and location ',location)
            clip_data = gen_clips_merged(actdictaccgyr,task,location,clipsize=10000,verbose=True)
            
            feature_extraction131(clip_data)
            tempdf = aggregateAcc(clip_data)

            ## add task and location as a column
            tempdf.insert(0, 'task', task)
            tempdf.insert(1, 'location', location)

            allsensordf = pd.concat([allsensordf,tempdf], ignore_index=True)
            
    return allsensordf

# aggregates acc and gyro features, combines trial
# Need to loop through all task and locations and make one dataframe
def aggregateAccGyroTrial(clip_data):
    """Take a clip of task/location with extracted ACC/GYR features, 
    and merge all trials into one dataframe.
    
    :param clip_data 
    """
    df = pd.DataFrame()
    for trial in clip_data.keys():
        
        try: acc_df = clip_data[trial]['accel']['features']
        except: 
            print('no accel data in trial ',trial)
            acc_df = pd.DataFrame()
            continue
        try: gyr_df = clip_data[trial]['gyro']['features']
        except: 
            print('no gyro data in trial ',trial)
            gyr_df = pd.DataFrame()
            continue

        trialdf = pd.concat([acc_df, gyr_df], axis=1)
        
        trialdf.insert(0, 'trial', trial)
        
        df = pd.concat([df,trialdf], ignore_index=True) # 0 prob by default

    return df

# aggregates only acc features, combines trials
# Need to loop through all task and locations and make one dataframe
def aggregateAcc(clip_data):
    """Take a clip of task/location with extracted ACC features only, 
    and merge all trials into one dataframe.
    
    :param clip_data 
    """
    df = pd.DataFrame()
    for trial in clip_data.keys():
        
        try: acc_df = clip_data[trial]['accel']['features']
        except: 
            print('no accel data in trial ',trial)
            acc_df = pd.DataFrame()
            continue
            
        acc_df.insert(0, 'trial', trial)
        df = pd.concat([df,acc_df], ignore_index=True) # 0 prob by default

    return df

def featuretest(clip_data):
    """
    Extract features from a simple clip of a single trial and sensor
    Input: simple clip without trial or sensor dict keys
    Output: feature matrix from all clips from given subject and scores for each clip
    Column names separate for acc and gyro data.
    """
    
    features_list = ['meanX','meanY','meanZ','rangeX','rangeY','rangeZ','iqrX','iqrY','iqrZ',
                     'stddev_X','stddev_Y','stddev_Z','skewX','skewY','skewZ','kurtX','kurtY','kurtZ',
                     'hist1_X','hist2_X','hist3_X','hist4_X',
                     'hist1_Y','hist2_Y','hist3_Y','hist4_Y',
                     'hist1_Z','hist2_Z','hist3_Z','hist4_Z',
                     #Moments of derivative: mean, SD, skew, kurtosis
                     'mean_derivative_x','mean_derivative_y','mean_derivative_z',
                     'std_derivative_x','std_derivative_y','std_derivative_z',
                     'skew_derivative_x','skew_derivative_y','skew_derivative_z',
                     'kurt_derivative_x','kurt_derivative_y','kurt_derivative_z',
                     'mean_squared_norm','sum_stddev',
                     'xcorr_XY','xcorr_XZ','xcorr_YZ',
                     'crossprod_raw_xy','crossprod_raw_xz','crossprod_raw_yz',
                     'crossprod_norm_xy','crossprod_norm_xz','crossprod_norm_yz',
                     'abs_crossprod_raw_xy','abs_crossprod_raw_xz','abs_crossprod_raw_yz',
                     'abs_crossprod_norm_xy','abs_crossprod_norm_xz','abs_crossprod_norm_yz',
                     'PSD_mean_X','PSD_mean_Y','PSD_mean_Z',
                     'PSD_std_X','PSD_std_Y','PSD_std_Z',
                     'PSD_skew_X','PSD_skew_Y','PSD_skew_Z',
                     'PSD_kur_X','PSD_kur_Y','PSD_kur_Z',
                     # mean power 20 bins
                     # x axis
                     'meanpower_bin1_x','meanpower_bin2_x','meanpower_bin3_x','meanpower_bin4_x',
                     'meanpower_bin5_x','meanpower_bin6_x','meanpower_bin7_x','meanpower_bin8_x',
                     'meanpower_bin9_x','meanpower_bin10_x','meanpower_bin11_x','meanpower_bin12_x',
                     'meanpower_bin13_x','meanpower_bin14_x','meanpower_bin15_x','meanpower_bin16_x',
                     'meanpower_bin17_x','meanpower_bin18_x','meanpower_bin19_x','meanpower_bin20_x',
                     # y axis
                     'meanpower_bin1_y','meanpower_bin2_y','meanpower_bin3_y','meanpower_bin4_y',
                     'meanpower_bin5_y','meanpower_bin6_y','meanpower_bin7_y','meanpower_bin8_y',
                     'meanpower_bin9_y','meanpower_bin10_y','meanpower_bin11_y','meanpower_bin12_y',
                     'meanpower_bin13_y','meanpower_bin14_y','meanpower_bin15_y','meanpower_bin16_y',
                     'meanpower_bin17_y','meanpower_bin18_y','meanpower_bin19_y','meanpower_bin20_y',
                     # z axis
                     'meanpower_bin1_z','meanpower_bin2_z','meanpower_bin3_z','meanpower_bin4_z',
                     'meanpower_bin5_z','meanpower_bin6_z','meanpower_bin7_z','meanpower_bin8_z',
                     'meanpower_bin9_z','meanpower_bin10_z','meanpower_bin11_z','meanpower_bin12_z',
                     'meanpower_bin13_z','meanpower_bin14_z','meanpower_bin15_z','meanpower_bin16_z',
                     'meanpower_bin17_z','meanpower_bin18_z','meanpower_bin19_z','meanpower_bin20_z',]


    #cycle through all clips for current trial and save dataframe of features for current trial and sensor
    features = []

    rawdata = clip_data

    #range on each axis
    min_xyz = np.min(rawdata,axis=0)
    max_xyz = np.max(rawdata,axis=0)
    r = np.asarray(max_xyz-min_xyz)

    #Moments on each axis - mean, std dev, skew, kurtosis
    mean = np.asarray(np.mean(rawdata,axis=0))
    # np.std default ddof=0 as default so changed to 1 to match matlab
    std = np.asarray(np.std(rawdata,axis=0, ddof=1))
    sk = skew(rawdata)
    # kurtosis has difference of +3 with matlab feature, thus the offset
    kurt = kurtosis(rawdata)+3

    #Cross-correlation between axes pairs
    xcorr_xy = np.corrcoef(rawdata.iloc[:,0],rawdata.iloc[:,1])[0][1]
    xcorr_xz = np.corrcoef(rawdata.iloc[:,0],rawdata.iloc[:,2])[0][1]
    xcorr_yz = np.corrcoef(rawdata.iloc[:,1],rawdata.iloc[:,2])[0][1]
    xcorr = np.array([xcorr_xy, xcorr_xz, xcorr_yz])

    # interquartile range
    iqrange = iqr(rawdata,axis=0)
    
    # histogram of z-score values
    hist = rawdata-np.mean(rawdata)/np.std(rawdata,ddof=1)
    hist_z_scores_x = np.histogram(hist.iloc[:,0],bins=4, range=(-2,2))
    hist_z_scores_y = np.histogram(hist.iloc[:,1], bins=4, range=(-2,2))
    hist_z_scores_z = np.histogram(hist.iloc[:,2], bins=4, range=(-2,2))
    
    hist_z_scores = np.concatenate((hist_z_scores_x[0], hist_z_scores_y[0], hist_z_scores_z[0]), axis=None)

    # derivative - for 3 axis
    derivative = np.diff(rawdata, axis=0)
    # mean of derivative
    mean_derivative = np.mean(derivative,axis=0)
    # std dev of derivative
    std_derivative = np.std(derivative,axis=0)
    # skewness of derivative
    skew_derivative = skew(derivative,axis=0)
    # kurtosis of derivative
        # added offset +3
    kurt_derivative = kurtosis(derivative,axis=0)+3
    moments_of_derivative = np.concatenate((mean_derivative,std_derivative,skew_derivative,kurt_derivative), axis=None)

    # sum of xyz std dev
    sum_stddev = np.array([np.sum(std)])

    # mean of the squared norm
    mean_squared_norm = np.array([np.mean(np.mean(np.square(rawdata)))])

    # normalize values (divided by acc norm) to get cross products
    # The norm should sum across xyz axis at each instance of time
    normdenominator = np.ones((len(rawdata.columns),1))*np.array(np.sqrt(np.sum(np.square(rawdata),axis=1)))
    norm = rawdata/normdenominator.T
    
    # cross products with raw and norm data
    crossprod_norm_xy = np.nanmean(norm.iloc[:,0]*norm.iloc[:,1])
    crossprod_norm_xz = np.nanmean(norm.iloc[:,0]*norm.iloc[:,2])
    crossprod_norm_yz = np.nanmean(norm.iloc[:,1]*norm.iloc[:,2])
    abs_crossprod_norm_xy = np.abs(crossprod_norm_xy)
    abs_crossprod_norm_xz = np.abs(crossprod_norm_xz)
    abs_crossprod_norm_yz = np.abs(crossprod_norm_yz)
    crossprod_raw_xy = np.nanmean(rawdata.iloc[:,0]*rawdata.iloc[:,1])
    crossprod_raw_xz = np.nanmean(rawdata.iloc[:,0]*rawdata.iloc[:,2])
    crossprod_raw_yz = np.nanmean(rawdata.iloc[:,1]*rawdata.iloc[:,2])
    abs_crossprod_raw_xy = np.abs(crossprod_raw_xy)
    abs_crossprod_raw_xz = np.abs(crossprod_raw_xz)
    abs_crossprod_raw_yz = np.abs(crossprod_raw_yz)
    crossprod = np.array([crossprod_raw_xy, crossprod_raw_xz, crossprod_raw_yz,
                          crossprod_norm_xy, crossprod_norm_xz, crossprod_norm_yz,
                          abs_crossprod_raw_xy, abs_crossprod_raw_xz, abs_crossprod_raw_yz,
                          abs_crossprod_norm_xy, abs_crossprod_norm_xz, abs_crossprod_norm_yz])
    
    # High pass filter before passing to PSD (to compare with Matlab process)
    rawdata = HPfilter_testclip(rawdata)
    
    # power spectral density (PSD)
# changed fm=0, to fm=1 like Andrew's code
    Pxx = power_spectra_welch_axis(rawdata,fm=0,fM=10)
    #moments of PSD
    Pxx_moments = np.array([np.nanmean(Pxx.iloc[:,0].values),np.nanmean(Pxx.iloc[:,1].values),np.nanmean(Pxx.iloc[:,2].values),
            np.nanstd(Pxx.iloc[:,0].values),np.nanstd(Pxx.iloc[:,1].values),np.nanstd(Pxx.iloc[:,2].values),
            skew(Pxx.iloc[:,0].values),skew(Pxx.iloc[:,1].values),skew(Pxx.iloc[:,2].values),
            kurtosis(Pxx.iloc[:,0].values),kurtosis(Pxx.iloc[:,1].values),kurtosis(Pxx.iloc[:,2].values)])
########################
    # Mean power in 0.5 Hz bins between 0 and 10 Hz (x, y, z)
    binedges = np.arange(0,10.5,0.5)
    powerbin_df = Pxx.groupby(pd.cut(Pxx.index, bins=binedges)).mean().fillna(0)
    powerbinarray = np.concatenate((powerbin_df.iloc[:,0],powerbin_df.iloc[:,1],powerbin_df.iloc[:,2]), axis=None)

#     # Andrew's mean PSD binning code
#     #power spectra averaged within bins
#     fm = 1; fM = 10; nbins = 10 #frequency bins
# # figure x=Pxx ?
#     Fs = np.mean(1/(np.diff(Pxx.index)/1000)) # sampling rate in clip
#     n = Pxx.size
#     timestep = 1/Fs
#     bin1 = int(timestep*n*fm)
#     bin2 = int(timestep*n*fM)
#     bins = np.linspace(bin1,bin2,nbins,dtype=int) #sample indices
#     deltab = int(0.5*np.diff(bins)[0]) #half the size of bin (in samples)
#     Pxxm = []
#     for i in bins:
#         start = int(max(i-deltab,bins[0]))
#         end = int(min(i+deltab,bins[-1]))
#         Pxxm.append(np.mean(Pxx[start:end]))
#     Pxxm = np.asarray(Pxxm)
# #     plt.plot(bins/(timestep*n),Pxxm)
#     powerbinarray = Pxxm
########################################
    #Assemble features in array
    X = np.concatenate((mean,r,iqrange,std,sk,kurt,hist_z_scores,moments_of_derivative,
                        mean_squared_norm,sum_stddev,xcorr,crossprod,Pxx_moments,powerbinarray))
    features.append(X)
    
    F = np.asarray(features) #feature matrix for all clips from current trial

    features = pd.DataFrame(data=F,columns=features_list,dtype='float32')

    return features

def feature_extraction131(clip_data):
    """
    Extract features from both sensors (accel and gyro) for current clips and trials
    Input: dictionary of clips from each subject
    Output: feature matrix from all clips from given subject and scores for each clip
    Column names separate for acc and gyro data.
    """
    
    features_list = ['meanX','meanY','meanZ','rangeX','rangeY','rangeZ','iqrX','iqrY','iqrZ',
                     'stddev_X','stddev_Y','stddev_Z','skewX','skewY','skewZ','kurtX','kurtY','kurtZ',
                     'hist1_X','hist2_X','hist3_X','hist4_X',
                     'hist1_Y','hist2_Y','hist3_Y','hist4_Y',
                     'hist1_Z','hist2_Z','hist3_Z','hist4_Z',
                     #Moments of derivative: mean, SD, skew, kurtosis
                     'mean_derivative_x','mean_derivative_y','mean_derivative_z',
                     'std_derivative_x','std_derivative_y','std_derivative_z',
                     'skew_derivative_x','skew_derivative_y','skew_derivative_z',
                     'kurt_derivative_x','kurt_derivative_y','kurt_derivative_z',
                     'mean_squared_norm','sum_stddev',
                     'xcorr_XY','xcorr_XZ','xcorr_YZ',
                     'crossprod_raw_xy','crossprod_raw_xz','crossprod_raw_yz',
                     'crossprod_norm_xy','crossprod_norm_xz','crossprod_norm_yz',
                     'abs_crossprod_raw_xy','abs_crossprod_raw_xz','abs_crossprod_raw_yz',
                     'abs_crossprod_norm_xy','abs_crossprod_norm_xz','abs_crossprod_norm_yz',
                     'PSD_mean_X','PSD_mean_Y','PSD_mean_Z',
                     'PSD_std_X','PSD_std_Y','PSD_std_Z',
                     'PSD_skew_X','PSD_skew_Y','PSD_skew_Z',
                     'PSD_kur_X','PSD_kur_Y','PSD_kur_Z',
                     # mean power 20 bins
                     # x axis
                     'meanpower_bin1_x','meanpower_bin2_x','meanpower_bin3_x','meanpower_bin4_x',
                     'meanpower_bin5_x','meanpower_bin6_x','meanpower_bin7_x','meanpower_bin8_x',
                     'meanpower_bin9_x','meanpower_bin10_x','meanpower_bin11_x','meanpower_bin12_x',
                     'meanpower_bin13_x','meanpower_bin14_x','meanpower_bin15_x','meanpower_bin16_x',
                     'meanpower_bin17_x','meanpower_bin18_x','meanpower_bin19_x','meanpower_bin20_x',
                     # y axis
                     'meanpower_bin1_y','meanpower_bin2_y','meanpower_bin3_y','meanpower_bin4_y',
                     'meanpower_bin5_y','meanpower_bin6_y','meanpower_bin7_y','meanpower_bin8_y',
                     'meanpower_bin9_y','meanpower_bin10_y','meanpower_bin11_y','meanpower_bin12_y',
                     'meanpower_bin13_y','meanpower_bin14_y','meanpower_bin15_y','meanpower_bin16_y',
                     'meanpower_bin17_y','meanpower_bin18_y','meanpower_bin19_y','meanpower_bin20_y',
                     # z axis
                     'meanpower_bin1_z','meanpower_bin2_z','meanpower_bin3_z','meanpower_bin4_z',
                     'meanpower_bin5_z','meanpower_bin6_z','meanpower_bin7_z','meanpower_bin8_z',
                     'meanpower_bin9_z','meanpower_bin10_z','meanpower_bin11_z','meanpower_bin12_z',
                     'meanpower_bin13_z','meanpower_bin14_z','meanpower_bin15_z','meanpower_bin16_z',
                     'meanpower_bin17_z','meanpower_bin18_z','meanpower_bin19_z','meanpower_bin20_z',]
    acclist = [s + '_acc' for s in features_list]
    gyrlist = [s + '_gyr' for s in features_list]

    for trial in clip_data.keys():

        for sensor in clip_data[trial].keys():

            #cycle through all clips for current trial and save dataframe of features for current trial and sensor
            features = []
            for c in range(len(clip_data[trial][sensor]['data'])):
                rawdata = clip_data[trial][sensor]['data'][c]

                ######################
                # Time domain features
                ######################
                #range on each axis
                min_xyz = np.min(rawdata,axis=0)
                max_xyz = np.max(rawdata,axis=0)
                r = np.asarray(max_xyz-min_xyz)

                #Moments on each axis - mean, std dev, skew, kurtosis
                mean = np.asarray(np.mean(rawdata,axis=0))
                std = np.asarray(np.std(rawdata,axis=0))
                sk = skew(rawdata)
                kurt = kurtosis(rawdata)

                #Cross-correlation between axes pairs
                xcorr_xy = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,1],mode='same')
                xcorr_xz = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,2],mode='same')
                xcorr_yz = np.correlate(rawdata.iloc[:,1],rawdata.iloc[:,2],mode='same')
                xcorr = np.array([xcorr_xy, xcorr_xz, xcorr_yz])

################
# Added features
################
# after adding new features...
# check names in features_list at top
# and concatenate at end

                # interquartile range
                iqr = iqr(rawdata,axis=0)
                # histogram of z-score values
                hist_z_scores_x = np.histogram(zscore(rawdata.iloc[:,0],axis=0), bins=4, range=(-2,2))
                hist_z_scores_y = np.histogram(zscore(rawdata.iloc[:,1],axis=0), bins=4, range=(-2,2))
                hist_z_scores_z = np.histogram(zscore(rawdata.iloc[:,2],axis=0), bins=4, range=(-2,2))
                hist_z_scores = np.array([hist_z_scores_x, hist_z_scores_y, hist_z_scores_z])
                
# Derivative vs differences (matlab code uses differences instead of derivative)
#                 differences = np.diff(rawdata,axis=0)
#                 # mean of differences
#                 mean_diff = np.asarray(np.mean(differences,axis=0))
#                 # std dev of differences
#                 std_diff = np.asarray(np.std(differences,axis=0))
#                 # skewness of differences
#                 skew_diff = skew(differences)
#                 # kurtosis of differences
#                 kurt_diff = kurtosis(differences)
                ##############################
                # derivative - for 3 axis
#                 derivative = difference/32
                derivativex = np.gradient(rawdata.iloc[:,0],32)
                derivativey = np.gradient(rawdata.iloc[:,1],32)
                derivativez = np.gradient(rawdata.iloc[:,2],32)
                derivative = np.array([derivativex,derivativey,derivativez])
                # derivative = np.gradient(rawdata, 32)
                # mean of derivative
                mean_derivative = np.mean(derivative,axis=1)
                # std dev of derivative
                std_derivative = np.std(derivative,axis=1)
                # skewness of derivative
                skew_derivative = skew(derivative,axis=1)
                # kurtosis of derivative
                kurt_derivative = kurtosis(derivative,axis=1)
                moments_of_derivative = np.array([mean_derivative,std_derivative,skew_derivative,kurt_derivative])
                
                # sum of xyz std dev
                sum_stddev = np.std(rawdata.iloc[:,0] + np.std(rawdata.iloc[:,1]) + np.std(rawdata.iloc[:,2]))
                
                # mean of the squared norm
# How should I get the Euclidiean norm? Check element squared...
#                 mean_of_squares = np.mean(np.mean(rawdata**2,axis=0)) # from matlab
# Is degree of freedom n (for mean) or (n-1)?
# Should be 1 feature
                norm = np.sqrt(np.square(rawdata).sum(axis=1))
                mean_squared_norm = np.mean(norm**2,axis=0)
    

#                 # normalize values (divided by acc norm) to get cross products
#                 norm = rawdata / np.linalg.norm(rawdata) # rawdata / np.linalg.norm(rawdata)
                # norm = rawdata/np.abs(np.sum(rawdata))
                crossprod_norm_xy = np.nanmean(norm.iloc[:,0])*norm.iloc[:,1]
                crossprod_norm_xz = np.nanmean(norm.iloc[:,0])*norm.iloc[:,2]
                crossprod_norm_yz = np.nanmean(norm.iloc[:,1])*norm.iloc[:,2]
                abs_crossprod_norm_xy = np.abs(crossprod_norm_xy)
                abs_crossprod_norm_xz = np.abs(crossprod_norm_xz)
                abs_crossprod_norm_yz = np.abs(crossprod_norm_yz)
                crossprod_raw_xy = np.nanmean(rawdata.iloc[:,0])*rawdata.iloc[:,1]
                crossprod_raw_xz = np.nanmean(rawdata.iloc[:,0])*rawdata.iloc[:,2]
                crossprod_raw_yz = np.nanmean(rawdata.iloc[:,1])*rawdata.iloc[:,2]
                abs_crossprod_raw_xy = np.abs(crossprod_raw_xy)
                abs_crossprod_raw_xz = np.abs(crossprod_raw_xz)
                abs_crossprod_raw_yz = np.abs(crossprod_raw_yz)
                crossprod = np.array([crossprod_raw_xy, crossprod_raw_xz, crossprod_raw_yz,
                                      crossprod_norm_xy, crossprod_norm_xz, crossprod_norm_yz,
                                      abs_crossprod_raw_xy, abs_crossprod_raw_xz, abs_crossprod_raw_yz,
                                      abs_crossprod_norm_xy, abs_crossprod_norm_xz, abs_crossprod_norm_yz])
                
                # sum of xyz std dev
                sum_stddev = np.std(rawdata.iloc[:,0] + np.std(rawdata.iloc[:,1]) + np.std(rawdata.iloc[:,2]))
                
# What is this? Omit?               
#                 # Linear fit
#                 slope_xy = np.polyfit(rawdata.iloc[:,0],rawdata.iloc[:,1],1)[0]
#                 slope_xz = np.polyfit(rawdata.iloc[:,0],rawdata.iloc[:,2],1)[0]
#                 slope_yz = np.polyfit(rawdata.iloc[:,1],rawdata.iloc[:,2],1)[0]

                #Dominant freq and relative magnitude (on acc magnitude)
                Pxx = power_spectra_welch_axis(rawdata,fm=0,fM=10)
                #moments of PSD
                Pxx_moments = np.array([np.nanmean(Pxx.iloc[0].values),np.nanmean(Pxx.iloc[1].values),np.nanmean(Pxx.iloc[2].values),
                                        np.nanstd(Pxx.iloc[0].values),np.nanstd(Pxx.iloc[1].values),np.nanstd(Pxx.iloc[2].values),
                                        skew(Pxx.iloc[0].values),skew(Pxx.iloc[1].values),skew(Pxx.iloc[2].values),
                                        kurtosis(Pxx.iloc[0].values),kurtosis(Pxx.iloc[1].values),kurtosis(Pxx.iloc[2].values)])
                # Mean power in 0.5 Hz bins between 0 and 10 Hz (x, y, z)
                binedges = np.arange(0,10.5,0.5)
                powerbin_df = Pxx.groupby(pd.cut(Pxx.index, bins=binedges)).mean().fillna(0)
                powerbinarray = np.asarray((powerbin_df.iloc[:,0],powerbin_df.iloc[:,1],powerbin_df.iloc[:,2]))
#####################################
############## End of added features
#####################################

                #Assemble features in array
# make sure all the columns add up and are labeled
                X = np.concatenate((mean,r,iqr,std,sk,kurt,hist_z_scores,moments_of_derivative,mean_squared_norm,sum_stddev,
                                    xcorr,crossprod,Pxx_moments,powerbinarray))
                features.append(X)

            F = np.asarray(features) #feature matrix for all clips from current trial
        #     clip_data['features'] = pd.DataFrame(data=F,columns=features_list,dtype='float32')
            if sensor == 'accel': columns_list = acclist
            else: columns_list = gyrlist
            try:
                clip_data[trial][sensor]['features'] = pd.DataFrame(data=F,columns=columns_list,dtype='float32')
            except:
                print('Empty data in feature_extraction131')
                continue
#     return clip_data #not necessary

def power_spectra_welch_axis(rawdata,fm,fM):
    """Compute PSD on each axis then combine into a dataframe"""
    x = rawdata.iloc[:,0]
    y = rawdata.iloc[:,1]
    z = rawdata.iloc[:,2]
    # number of samples in clip
    n = len(x)
    # sampling rate in clip
    Fs = np.mean(1/(np.diff(x.index)/1000))
    
    # adjusted params to match frequency using scipy.welch with matlab.pwelch
#     fx,Pxx_denX = welch(x,fs=30,nperseg=256,detrend=False)
#     fy,Pxx_denY = welch(y,fs=30,nperseg=256,detrend=False)
#     fz,Pxx_denZ = welch(z,fs=30,nperseg=256,detrend=False)
    # added param: detrend=False
    fx,Pxx_denX = welch(x,Fs,nperseg=min(256,n),detrend=False)
    fy,Pxx_denY = welch(y,Fs,nperseg=min(256,n),detrend=False)
    fz,Pxx_denZ = welch(z,Fs,nperseg=min(256,n),detrend=False)
    
    #return PSD in desired interval of freq
    inds = (fx<=fM)&(fx>=fm)
    f=fx[inds]
    Pxx_denX=Pxx_denX[inds]
    Pxx_denY=Pxx_denY[inds]
    Pxx_denZ=Pxx_denZ[inds]
    Pxx_den = {'PSD_X':Pxx_denX,'PSD_Y':Pxx_denY,'PSD_Z':Pxx_denY}
    Pxxdf = pd.DataFrame(data=Pxx_den,index=f)

    return Pxxdf

def power_spectra_welch(rawdata,fm,fM):
    """
    PSD on magnitude using Welch method
    Compute PSD on signal magnitude
    Returns 1 column
    """
    x = rawdata.iloc[:,-1]
    n = len(x) #number of samples in clip
    Fs = np.mean(1/(np.diff(x.index)/1000)) #sampling rate in clip
    f,Pxx_den = welch(x,Fs,nperseg=min(256,n))
    #return PSD in desired interval of freq
    inds = (f<=fM)&(f>=fm)
    f=f[inds]
    Pxx_den=Pxx_den[inds]
    Pxxdf = pd.DataFrame(data=Pxx_den,index=f,columns=['PSD_magnitude'])

    return Pxxdf

def HPfilter(act_dict,task,loc,cutoff=0.75,ftype='highpass'):
    """
    Highpass (or lowpass) filter data. HP to remove gravity (offset - limb orientation) from accelerometer 
    data from each visit (trial)
    
    Input: Activity dictionary, cutoff freq [Hz], task, sensor location and type of filter 
    (highpass or lowpass).
    """
    sensor = 'accel'
    for trial in act_dict[task].keys():
        rawdata = act_dict[task][trial][loc][sensor]
        if rawdata.empty is True: #skip if no data for current sensor
            continue
        idx = rawdata.index
        idx = idx-idx[0]
        rawdata.index = idx
        x = rawdata.values
        Fs = np.mean(1/(np.diff(rawdata.index)/1000)) #sampling rate
        #filter design
        cutoff_norm = cutoff/(0.5*Fs)
        #     b,a = butter(4,cutoff_norm,btype=ftype,analog=False)
# Matlab: change params to N=2, cutoff_norm= (prev 0.046875, cutoff=0.75)
        b,a = butter(2,cutoff_norm,btype=ftype,analog=False)
        #filter data
        xfilt = filtfilt(b,a,x,axis=0)
        rawdatafilt = pd.DataFrame(data=xfilt,index=rawdata.index,columns=rawdata.columns)
        act_dict[task][trial][loc][sensor] = rawdatafilt
        
def HPfilter_testclip(clip_data,cutoff=0.75,ftype='highpass'):
    """
    Highpass (or lowpass) filter data. HP to remove gravity (offset - limb orientation) from accelerometer 
    data from each visit (trial)
    
    Input: Testclip, cutoff freq [Hz], task, sensor location and type of filter 
    (highpass or lowpass).
    """
    rawdata = clip_data
#     if rawdata.empty is True: #skip if no data for current sensor
#         continue
    idx = rawdata.index
    idx = idx-idx[0]
    rawdata.index = idx
    x = rawdata.values
    Fs = np.mean(1/(np.diff(rawdata.index)/1000)) #sampling rate
    #filter design
    cutoff_norm = cutoff/(0.5*Fs)
#     b,a = butter(4,cutoff_norm,btype=ftype,analog=False)
# Matlab: change params to N=2, cutoff_norm= (prev 0.046875, cutoff=0.75)
    b,a = butter(2,cutoff_norm,btype=ftype,analog=False)
    #filter data
    xfilt = filtfilt(b,a,x,axis=0)
    rawdatafilt = pd.DataFrame(data=xfilt,index=rawdata.index,columns=rawdata.columns)
    clip_data = rawdatafilt
    return clip_data

# this one for low pass.
def filterdata(rawdata,ftype='highpass',cutoff=0.75,cutoff_bp=[3,8],order=4):

    if not rawdata.empty:
        idx = rawdata.index
        idx = idx-idx[0]
        rawdata.index = idx
        x = rawdata.values
        #print(np.unique(np.diff(rawdata.index)))
        Fs = np.mean(1/(np.diff(rawdata.index)/1000)) #sampling rate
        if ftype != 'bandpass':
            #filter design
            cutoff_norm = cutoff/(0.5*Fs)
            b,a = butter(4,cutoff_norm,btype=ftype,analog=False)
        else:
            #filter design
            cutoff_low_norm = cutoff_bp[0]/(0.5*Fs)
            cutoff_high_norm = cutoff_bp[1]/(0.5*Fs)
            b,a = butter(order,[cutoff_low_norm,cutoff_high_norm],btype='bandpass',analog=False)

        #filter data
        xfilt = filtfilt(b,a,x,axis=0)
        rawdatafilt = pd.DataFrame(data=xfilt,index=rawdata.index,columns=rawdata.columns)
        return rawdatafilt
    
# Used for PD - tremor
def BPfilter(act_dict,task,loc,cutoff_low=3,cutoff_high=8,order=4):
    """
    bandpass filter data (analysis of Tremor)
    input: Activity dictionary, min,max freq [Hz], task and sensor location to filter
    """
    
    sensor = 'accel'
    for trial in act_dict[task].keys():
        rawdata = act_dict[task][trial][loc][sensor]
        idx = rawdata.index
        idx = idx-idx[0]
        rawdata.index = idx
        x = rawdata.values
        Fs = np.mean(1/(np.diff(rawdata.index)/1000)) #sampling rate
        #filter design
        cutoff_low_norm = cutoff_low/(0.5*Fs)
        cutoff_high_norm = cutoff_high/(0.5*Fs)
        b,a = butter(order,[cutoff_low_norm,cutoff_high_norm],btype='bandpass',analog=False)
        #filter data
        xfilt = filtfilt(b,a,x,axis=0)
        rawdatafilt = pd.DataFrame(data=xfilt,index=rawdata.index,columns=rawdata.columns)
        act_dict[task][trial][loc][sensor] = rawdatafilt
        
############
# create function to merge all clips together
############
def gen_clips_merged(act_dict,task,location,clipsize=10000,overlap=0.9,verbose=False,startTS=0,endTS=1,
              len_tol=0.95,resample=False):
    """
    Extract clips and merge into 1 clip for accelerometer and gyro data (allows selecting start and end fraction)
    len_tol is the % of the intended clipsize below which clip is not used
    
    :param clipsize 10000 = 10 sec
    :param overlap=0.9 for 90% overlap b/n clips
    :param len_tol=1.0, want complete 10 sec clips
    
    """
    
    clip_data = {} #the dictionary with clips

    for trial in act_dict[task].keys():
        clip_data[trial] = {}

        for s in ['accel','gyro']:

            if verbose:
                print(task,' sensortype = %s - trial %d'%(s,trial))
            #create clips and store in a list
            rawdata = act_dict[task][trial][location][s]
            if rawdata.empty is True: #skip if no data for current sensor
                continue
            #reindex time (relative to start)
            idx = rawdata.index
            idx = idx-idx[0]
            rawdata.index = idx
            #choose to create clips only on a fraction of the data (0<[startTS,endTS]<1)
            if (startTS > 0) | (endTS < 1):
                rawdata = rawdata.iloc[round(startTS*len(rawdata)):round(endTS*len(rawdata)),:]
                #reindex time (relative to start)
                idx = rawdata.index
                idx = idx-idx[0]
                rawdata.index = idx
            #create clips data
            deltat = np.median(np.diff(rawdata.index))
            clips = []
            #use entire recording
            if clipsize == 0:
                clips.append(rawdata)
            #take clips
            else:
                idx = np.arange(0,rawdata.index[-1],clipsize*(1-overlap))
                for i in idx:
                    c = rawdata[(rawdata.index>=i) & (rawdata.index<i+clipsize)]
                    #keep/append clips that are 10 sec, else discard those that don't meet length
                    #tolerance
                    ## clip length tolerance > 9.5 sec
                    if len(c) > len_tol*int(clipsize/deltat):
                        # try concat instead of append to make one list
                        # check index, if increases like 0, 32, 64, etc then great, otherwise
                        # reindex c before extending?
                        clips.append(c)

            # merge all clips into one
            # cycle through each list element, reindex
            if len(clips)>1:
#                 finalclip = []
                for x in range(len(clips)):
                    if x==0:
                        clips.append(clips[0])
                    else:
                        # reindex
                        idx2 = clips[x].index
                        idx2 = idx2-idx2[0]+32+clips[x-1].index[-1]
                        clips[x].index = idx2
                        # merge into list of dataframes
                        clips.append(clips[x])
    
            # merge into one dataframe
            try:
                oneclip = pd.concat(clips)
            except:
                print('Check len_tol in gen_clips_merged function.')
            # reset clips
            clips = []
            clips.append(oneclip)
    
            #store clip length
            #store the length of each clip
            clip_len = [clips[c].index[-1]-clips[c].index[0] for c in range(len(clips))] 
            #assemble in dict
            clip_data[trial][s] = {'data':clips, 'clip_len':clip_len}

    return clip_data

def gen_clips(act_dict,task,location,clipsize=10000,overlap=0.9,verbose=False,startTS=0,endTS=1,
              len_tol=1.0,resample=False):
    """
    Extract separate clips for accelerometer and gyro data (allows selecting start and end fraction)
    len_tol is the % of the intended clipsize below which clip is not used
    
    :param clipsize 10000 = 10 sec
    :param overlap=0.9 for 90% overlap b/n clips
    :param len_tol=1.0, want complete 10 sec clips
    
    Default arg changes before modification:
    - clipsize=5000
    - overlap=0
    - len_tol=0.8
    """
    
    clip_data = {} #the dictionary with clips

    for trial in act_dict[task].keys():
        clip_data[trial] = {}

        for s in ['accel','gyro']:

            if verbose:
                print(task,' sensortype = %s - trial %d'%(s,trial))
            #create clips and store in a list
            rawdata = act_dict[task][trial][location][s]
            if rawdata.empty is True: #skip if no data for current sensor
                continue
            #reindex time (relative to start)
            idx = rawdata.index
            idx = idx-idx[0]
            rawdata.index = idx
            #choose to create clips only on a fraction of the data (0<[startTS,endTS]<1)
            if (startTS > 0) | (endTS < 1):
                rawdata = rawdata.iloc[round(startTS*len(rawdata)):round(endTS*len(rawdata)),:]
                #reindex time (relative to start)
                idx = rawdata.index
                idx = idx-idx[0]
                rawdata.index = idx
            #create clips data
            deltat = np.median(np.diff(rawdata.index))
            clips = []
            #use entire recording
            if clipsize == 0:
                clips.append(rawdata)
            #take clips
            else:
                idx = np.arange(0,rawdata.index[-1],clipsize*(1-overlap))
                for i in idx:
                    c = rawdata[(rawdata.index>=i) & (rawdata.index<i+clipsize)]
                    #keep/append clips that are 10 sec, else discard those that don't meet length
                    #tolerance
                    ## changed > to >= so it will keep clip>=10 sec
                    if len(c) >= len_tol*int(clipsize/deltat):
                        clips.append(c)

            #store clip length
            #store the length of each clip
            clip_len = [clips[c].index[-1]-clips[c].index[0] for c in range(len(clips))] 
            #assemble in dict
            clip_data[trial][s] = {'data':clips, 'clip_len':clip_len}

    return clip_data

# try making 74 feature list of acc and gyro feat
def feature_extraction_accgyro(clip_data):
    """
    Extract features from both sensors (accel and gyro) for current clips and trials
    Input: dictionary of clips from each subject
    Output: feature matrix from all clips from given subject and scores for each clip
    """
    
    features_list = ['RMSX','RMSY','RMSZ','rangeX','rangeY','rangeZ','meanX','meanY','meanZ','varX','varY','varZ',
                    'skewX','skewY','skewZ','kurtX','kurtY','kurtZ','xcor_peakXY','xcorr_peakXZ','xcorr_peakYZ',
                    'xcorr_lagXY','xcorr_lagXZ','xcorr_lagYZ','Dom_freq','Pdom_rel','PSD_mean','PSD_std','PSD_skew',
                    'PSD_kur','jerk_mean','jerk_std','jerk_skew','jerk_kur','Sen_X','Sen_Y','Sen_Z']
#                     ,'RMS_mag','range_mag',
#                     'mean_mag','var_mag','skew_mag','kurt_mag','Sen_mag']
    acclist = [s + '_acc' for s in features_list]
    gyrlist = [s + '_gyr' for s in features_list]

    for trial in clip_data.keys():

        for sensor in clip_data[trial].keys():

            #cycle through all clips for current trial and save dataframe of features for current trial and sensor
            features = []
            for c in range(len(clip_data[trial][sensor]['data'])):
                rawdata = clip_data[trial][sensor]['data'][c]
            
                #acceleration magnitude
                rawdata_wmag = rawdata.copy()
                rawdata_wmag['Accel_Mag']=np.sqrt((rawdata**2).sum(axis=1))

                #extract features on current clip

                #Root mean square of signal on each axis
                N = len(rawdata)
                RMS = 1/N*np.sqrt(np.asarray(np.sum(rawdata**2,axis=0)))

        #         RMS_mag = 1/N*np.sqrt(np.sum(rawdata_wmag['Accel_Mag']**2,axis=0))

                #range on each axis
                min_xyz = np.min(rawdata,axis=0)
                max_xyz = np.max(rawdata,axis=0)
                r = np.asarray(max_xyz-min_xyz)

        #         r_mag = np.max(rawdata_wmag['Accel_Mag']) - np.min(rawdata_wmag['Accel_Mag'])

                #Moments on each axis
                mean = np.asarray(np.mean(rawdata,axis=0))
                var = np.asarray(np.std(rawdata,axis=0))
                sk = skew(rawdata)
                kurt = kurtosis(rawdata)

        #         mean_mag = np.mean(rawdata_wmag['Accel_Mag'])
        #         var_mag = np.std(rawdata_wmag['Accel_Mag'])
        #         sk_mag = skew(rawdata_wmag['Accel_Mag'])
        #         kurt_mag = kurtosis(rawdata_wmag['Accel_Mag'])

                #Cross-correlation between axes pairs
                xcorr_xy = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,1],mode='same')
                # xcorr_xy = xcorr_xy/np.abs(np.sum(xcorr_xy)) #normalize values
                xcorr_peak_xy = np.max(xcorr_xy)
                xcorr_lag_xy = (np.argmax(xcorr_xy))/len(xcorr_xy) #normalized lag

                xcorr_xz = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,2],mode='same')
                # xcorr_xz = xcorr_xz/np.abs(np.sum(xcorr_xz)) #normalize values
                xcorr_peak_xz = np.max(xcorr_xz)
                xcorr_lag_xz = (np.argmax(xcorr_xz))/len(xcorr_xz)

                xcorr_yz = np.correlate(rawdata.iloc[:,1],rawdata.iloc[:,2],mode='same')
                # xcorr_yz = xcorr_yz/np.abs(np.sum(xcorr_yz)) #normalize values
                xcorr_peak_yz = np.max(xcorr_yz)
                xcorr_lag_yz = (np.argmax(xcorr_yz))/len(xcorr_yz)

                #pack xcorr features
                xcorr_peak = np.array([xcorr_peak_xy,xcorr_peak_xz,xcorr_peak_yz])
                xcorr_lag = np.array([xcorr_lag_xy,xcorr_lag_xz,xcorr_lag_yz])

                #Dominant freq and relative magnitude (on acc magnitude)
                Pxx = power_spectra_welch(rawdata_wmag,fm=0,fM=10)
                domfreq = np.asarray([Pxx.iloc[:,-1].idxmax()])
                Pdom_rel = Pxx.loc[domfreq].iloc[:,-1].values/Pxx.iloc[:,-1].sum() #power at dominant freq rel to total

                #moments of PSD
                Pxx_moments = np.array([np.nanmean(Pxx.values),np.nanstd(Pxx.values),skew(Pxx.values),kurtosis(Pxx.values)])

                #moments of jerk magnitude
                jerk = rawdata_wmag['Accel_Mag'].diff().values
                jerk_moments = np.array([np.nanmean(jerk),np.nanstd(jerk),skew(jerk[~np.isnan(jerk)]),kurtosis(jerk[~np.isnan(jerk)])])

                #sample entropy raw data (magnitude) and FFT
                sH_raw = []; sH_fft = []

                for a in range(3):
                    x = rawdata.iloc[:,a]
                    n = len(x) #number of samples in clip
                    Fs = np.mean(1/(np.diff(x.index)/1000)) #sampling rate in clip
                    sH_raw.append(nolds.sampen(x)) #samp entr raw data
                    #for now disable SH on fft
                    # f,Pxx_den = welch(x,Fs,nperseg=min(256,n/4))
                    # sH_fft.append(nolds.sampen(Pxx_den)) #samp entr fft

                sH_mag = nolds.sampen(rawdata_wmag['Accel_Mag'])

                #Assemble features in array
        #         Y = np.array([RMS_mag,r_mag,mean_mag,var_mag,sk_mag,kurt_mag,sH_mag])
                X = np.concatenate((RMS,r,mean,var,sk,kurt,xcorr_peak,xcorr_lag,domfreq,Pdom_rel,Pxx_moments,jerk_moments,sH_raw)) #,Y))
                features.append(X)

            F = np.asarray(features) #feature matrix for all clips from current trial
        #     clip_data['features'] = pd.DataFrame(data=F,columns=features_list,dtype='float32')
        
            # add condition of sensor
            if sensor == 'accel':
                column_list=acclist
                clip_data[trial]['features'] = pd.DataFrame(data=F,columns=column_list,dtype='float32')
            else:
                column_list=gyrlist
                # Need to concat on columns
                df_to_append = pd.DataFrame(data=F,columns=column_list,dtype='float32')
                clip_data[trial]['features'] = pd.concat([clip_data[trial]['features'], df_to_append],ignore_index=True,axis=1)
                # option 2 just change feature names to gyr
                clip_data[trial]['features'] = df_to_append = pd.DataFrame(data=F,columns=column_list,dtype='float32')

#     return clip_data #not necessary

# used function 
def feature_extraction(clip_data):
    """
    Extract features from both sensors (accel and gyro) for current clips and trials
    Input: dictionary of clips from each subject
    Output: feature matrix from all clips from given subject and scores for each clip
    """
    
    features_list = ['RMSX','RMSY','RMSZ','rangeX','rangeY','rangeZ','meanX','meanY','meanZ','varX','varY','varZ',
                    'skewX','skewY','skewZ','kurtX','kurtY','kurtZ','xcor_peakXY','xcorr_peakXZ','xcorr_peakYZ',
                    'xcorr_lagXY','xcorr_lagXZ','xcorr_lagYZ','Dom_freq','Pdom_rel','PSD_mean','PSD_std','PSD_skew',
                    'PSD_kur','jerk_mean','jerk_std','jerk_skew','jerk_kur','Sen_X','Sen_Y','Sen_Z']
#                     ,'RMS_mag','range_mag',
#                     'mean_mag','var_mag','skew_mag','kurt_mag','Sen_mag']

    for trial in clip_data.keys():

        for sensor in clip_data[trial].keys():

            #cycle through all clips for current trial and save dataframe of features for current trial and sensor
            features = []
            for c in range(len(clip_data[trial][sensor]['data'])):
                rawdata = clip_data[trial][sensor]['data'][c]
            
                #acceleration magnitude
                rawdata_wmag = rawdata.copy()
                rawdata_wmag['Accel_Mag']=np.sqrt((rawdata**2).sum(axis=1))

                #extract features on current clip

                #Root mean square of signal on each axis
                N = len(rawdata)
                RMS = 1/N*np.sqrt(np.asarray(np.sum(rawdata**2,axis=0)))

        #         RMS_mag = 1/N*np.sqrt(np.sum(rawdata_wmag['Accel_Mag']**2,axis=0))

                #range on each axis
                min_xyz = np.min(rawdata,axis=0)
                max_xyz = np.max(rawdata,axis=0)
                r = np.asarray(max_xyz-min_xyz)

        #         r_mag = np.max(rawdata_wmag['Accel_Mag']) - np.min(rawdata_wmag['Accel_Mag'])

                #Moments on each axis
                mean = np.asarray(np.mean(rawdata,axis=0))
                var = np.asarray(np.std(rawdata,axis=0))
                sk = skew(rawdata)
                kurt = kurtosis(rawdata)

        #         mean_mag = np.mean(rawdata_wmag['Accel_Mag'])
        #         var_mag = np.std(rawdata_wmag['Accel_Mag'])
        #         sk_mag = skew(rawdata_wmag['Accel_Mag'])
        #         kurt_mag = kurtosis(rawdata_wmag['Accel_Mag'])

                #Cross-correlation between axes pairs
                xcorr_xy = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,1],mode='same')
                # xcorr_xy = xcorr_xy/np.abs(np.sum(xcorr_xy)) #normalize values
                xcorr_peak_xy = np.max(xcorr_xy)
                xcorr_lag_xy = (np.argmax(xcorr_xy))/len(xcorr_xy) #normalized lag

                xcorr_xz = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,2],mode='same')
                # xcorr_xz = xcorr_xz/np.abs(np.sum(xcorr_xz)) #normalize values
                xcorr_peak_xz = np.max(xcorr_xz)
                xcorr_lag_xz = (np.argmax(xcorr_xz))/len(xcorr_xz)

                xcorr_yz = np.correlate(rawdata.iloc[:,1],rawdata.iloc[:,2],mode='same')
                # xcorr_yz = xcorr_yz/np.abs(np.sum(xcorr_yz)) #normalize values
                xcorr_peak_yz = np.max(xcorr_yz)
                xcorr_lag_yz = (np.argmax(xcorr_yz))/len(xcorr_yz)

                #pack xcorr features
                xcorr_peak = np.array([xcorr_peak_xy,xcorr_peak_xz,xcorr_peak_yz])
                xcorr_lag = np.array([xcorr_lag_xy,xcorr_lag_xz,xcorr_lag_yz])

                #Dominant freq and relative magnitude (on acc magnitude)
                Pxx = power_spectra_welch(rawdata_wmag,fm=0,fM=10)
                domfreq = np.asarray([Pxx.iloc[:,-1].idxmax()])
                Pdom_rel = Pxx.loc[domfreq].iloc[:,-1].values/Pxx.iloc[:,-1].sum() #power at dominant freq rel to total

                #moments of PSD
                Pxx_moments = np.array([np.nanmean(Pxx.values),np.nanstd(Pxx.values),skew(Pxx.values),kurtosis(Pxx.values)])

                #moments of jerk magnitude
                jerk = rawdata_wmag['Accel_Mag'].diff().values
                jerk_moments = np.array([np.nanmean(jerk),np.nanstd(jerk),skew(jerk[~np.isnan(jerk)]),kurtosis(jerk[~np.isnan(jerk)])])

                #sample entropy raw data (magnitude) and FFT
                sH_raw = []; sH_fft = []

                for a in range(3):
                    x = rawdata.iloc[:,a]
                    n = len(x) #number of samples in clip
                    Fs = np.mean(1/(np.diff(x.index)/1000)) #sampling rate in clip
                    sH_raw.append(nolds.sampen(x)) #samp entr raw data
                    #for now disable SH on fft
                    # f,Pxx_den = welch(x,Fs,nperseg=min(256,n/4))
                    # sH_fft.append(nolds.sampen(Pxx_den)) #samp entr fft

                sH_mag = nolds.sampen(rawdata_wmag['Accel_Mag'])

                #Assemble features in array
        #         Y = np.array([RMS_mag,r_mag,mean_mag,var_mag,sk_mag,kurt_mag,sH_mag])
                X = np.concatenate((RMS,r,mean,var,sk,kurt,xcorr_peak,xcorr_lag,domfreq,Pdom_rel,Pxx_moments,jerk_moments,sH_raw)) #,Y))
                features.append(X)

            F = np.asarray(features) #feature matrix for all clips from current trial
        #     clip_data['features'] = pd.DataFrame(data=F,columns=features_list,dtype='float32')
            clip_data[trial][sensor]['features'] = pd.DataFrame(data=F,columns=features_list,dtype='float32')

#     return clip_data #not necessary

# This was modified for PD study feature extraction
# different col names for acc and gyro
def feature_extraction2(clip_data):
    """
    Extract features from both sensors (accel and gyro) for current clips and trials
    Input: dictionary of clips from each subject
    Output: feature matrix from all clips from given subject and scores for each clip
    """
    
    features_list = ['RMSX','RMSY','RMSZ','rangeX','rangeY','rangeZ','meanX','meanY','meanZ','varX','varY','varZ',
                    'skewX','skewY','skewZ','kurtX','kurtY','kurtZ','xcor_peakXY','xcorr_peakXZ','xcorr_peakYZ',
                    'xcorr_lagXY','xcorr_lagXZ','xcorr_lagYZ','Dom_freq','Pdom_rel','PSD_mean','PSD_std','PSD_skew',
                    'PSD_kur','jerk_mean','jerk_std','jerk_skew','jerk_kur','Sen_X','Sen_Y','Sen_Z']
#                     ,'RMS_mag','range_mag',
#                     'mean_mag','var_mag','skew_mag','kurt_mag','Sen_mag']
    acclist = [s + '_acc' for s in features_list]
    gyrlist = [s + '_gyr' for s in features_list]

    for trial in clip_data.keys():

        for sensor in clip_data[trial].keys():

            #cycle through all clips for current trial and save dataframe of features for current trial and sensor
            features = []
            for c in range(len(clip_data[trial][sensor]['data'])):
                rawdata = clip_data[trial][sensor]['data'][c]
            
                #acceleration magnitude
                rawdata_wmag = rawdata.copy()
                rawdata_wmag['Accel_Mag']=np.sqrt((rawdata**2).sum(axis=1))

                #extract features on current clip

                #Root mean square of signal on each axis
                N = len(rawdata)
                RMS = 1/N*np.sqrt(np.asarray(np.sum(rawdata**2,axis=0)))

        #         RMS_mag = 1/N*np.sqrt(np.sum(rawdata_wmag['Accel_Mag']**2,axis=0))

                #range on each axis
                min_xyz = np.min(rawdata,axis=0)
                max_xyz = np.max(rawdata,axis=0)
                r = np.asarray(max_xyz-min_xyz)

        #         r_mag = np.max(rawdata_wmag['Accel_Mag']) - np.min(rawdata_wmag['Accel_Mag'])

                #Moments on each axis
                mean = np.asarray(np.mean(rawdata,axis=0))
                var = np.asarray(np.std(rawdata,axis=0))
                sk = skew(rawdata)
                kurt = kurtosis(rawdata)

        #         mean_mag = np.mean(rawdata_wmag['Accel_Mag'])
        #         var_mag = np.std(rawdata_wmag['Accel_Mag'])
        #         sk_mag = skew(rawdata_wmag['Accel_Mag'])
        #         kurt_mag = kurtosis(rawdata_wmag['Accel_Mag'])

                #Cross-correlation between axes pairs
                xcorr_xy = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,1],mode='same')
                # xcorr_xy = xcorr_xy/np.abs(np.sum(xcorr_xy)) #normalize values
                xcorr_peak_xy = np.max(xcorr_xy)
                xcorr_lag_xy = (np.argmax(xcorr_xy))/len(xcorr_xy) #normalized lag

                xcorr_xz = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,2],mode='same')
                # xcorr_xz = xcorr_xz/np.abs(np.sum(xcorr_xz)) #normalize values
                xcorr_peak_xz = np.max(xcorr_xz)
                xcorr_lag_xz = (np.argmax(xcorr_xz))/len(xcorr_xz)

                xcorr_yz = np.correlate(rawdata.iloc[:,1],rawdata.iloc[:,2],mode='same')
                # xcorr_yz = xcorr_yz/np.abs(np.sum(xcorr_yz)) #normalize values
                xcorr_peak_yz = np.max(xcorr_yz)
                xcorr_lag_yz = (np.argmax(xcorr_yz))/len(xcorr_yz)

                #pack xcorr features
                xcorr_peak = np.array([xcorr_peak_xy,xcorr_peak_xz,xcorr_peak_yz])
                xcorr_lag = np.array([xcorr_lag_xy,xcorr_lag_xz,xcorr_lag_yz])

                #Dominant freq and relative magnitude (on acc magnitude)
                Pxx = power_spectra_welch(rawdata_wmag,fm=0,fM=10)
                domfreq = np.asarray([Pxx.iloc[:,-1].idxmax()])
                Pdom_rel = Pxx.loc[domfreq].iloc[:,-1].values/Pxx.iloc[:,-1].sum() #power at dominant freq rel to total

                #moments of PSD
                Pxx_moments = np.array([np.nanmean(Pxx.values),np.nanstd(Pxx.values),skew(Pxx.values),kurtosis(Pxx.values)])

                #moments of jerk magnitude
                jerk = rawdata_wmag['Accel_Mag'].diff().values
                jerk_moments = np.array([np.nanmean(jerk),np.nanstd(jerk),skew(jerk[~np.isnan(jerk)]),kurtosis(jerk[~np.isnan(jerk)])])

                #sample entropy raw data (magnitude) and FFT
                sH_raw = []; sH_fft = []

                for a in range(3):
                    x = rawdata.iloc[:,a]
                    n = len(x) #number of samples in clip
                    Fs = np.mean(1/(np.diff(x.index)/1000)) #sampling rate in clip
                    sH_raw.append(nolds.sampen(x)) #samp entr raw data
                    #for now disable SH on fft
                    # f,Pxx_den = welch(x,Fs,nperseg=min(256,n/4))
                    # sH_fft.append(nolds.sampen(Pxx_den)) #samp entr fft

                sH_mag = nolds.sampen(rawdata_wmag['Accel_Mag'])

                #Assemble features in array
        #         Y = np.array([RMS_mag,r_mag,mean_mag,var_mag,sk_mag,kurt_mag,sH_mag])
                X = np.concatenate((RMS,r,mean,var,sk,kurt,xcorr_peak,xcorr_lag,domfreq,Pdom_rel,Pxx_moments,jerk_moments,sH_raw)) #,Y))
                features.append(X)

            F = np.asarray(features) #feature matrix for all clips from current trial
        #     clip_data['features'] = pd.DataFrame(data=F,columns=features_list,dtype='float32')
            if sensor == 'accel': columns_list = acclist
            else: columns_list = gyrlist
            try:
                clip_data[trial][sensor]['features'] = pd.DataFrame(data=F,columns=columns_list,dtype='float32')
            except:
                print('Empty data in feature_extraction2')
                continue
#     return clip_data #not necessary

def feature_extraction_reduced(clip_data):

    features_list = ['RMSX','RMSY','RMSZ','rangeX','rangeY','rangeZ','meanX','meanY','meanZ','varX','varY','varZ',
                    'skewX','skewY','skewZ','kurtX','kurtY','kurtZ','xcor_peakXY','xcorr_peakXZ','xcorr_peakYZ',
                    'xcorr_lagXY','xcorr_lagXZ','xcorr_lagYZ','Dom_freq','Pdom_rel','PSD_mean','PSD_std','PSD_skew',
                    'PSD_kur','jerk_mean','jerk_std','jerk_skew','jerk_kur']


    #cycle through all clips for current trial and save dataframe of features for current trial and sensor
    features = []
    for c in range(len(clip_data['data'])):
        rawdata = clip_data['data'][c]
        #acceleration magnitude
        rawdata_wmag = rawdata.copy()
        rawdata_wmag['Accel_Mag']=np.sqrt((rawdata**2).sum(axis=1))

        #extract features on current clip

        #Root mean square of signal on each axis
        N = len(rawdata)
        RMS = 1/N*np.sqrt(np.asarray(np.sum(rawdata**2,axis=0)))

        #range on each axis
        min_xyz = np.min(rawdata,axis=0)
        max_xyz = np.max(rawdata,axis=0)
        r = np.asarray(max_xyz-min_xyz)

  

        #Moments on each axis
        mean = np.asarray(np.mean(rawdata,axis=0))
        var = np.asarray(np.std(rawdata,axis=0))
        sk = skew(rawdata)
        kurt = kurtosis(rawdata)


        #Cross-correlation between axes pairs
        xcorr_xy = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,1],mode='same')
        # xcorr_xy = xcorr_xy/np.abs(np.sum(xcorr_xy)) #normalize values
        xcorr_peak_xy = np.max(xcorr_xy)
        xcorr_lag_xy = (np.argmax(xcorr_xy))/len(xcorr_xy) #normalized lag

        xcorr_xz = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,2],mode='same')
        # xcorr_xz = xcorr_xz/np.abs(np.sum(xcorr_xz)) #normalize values
        xcorr_peak_xz = np.max(xcorr_xz)
        xcorr_lag_xz = (np.argmax(xcorr_xz))/len(xcorr_xz)

        xcorr_yz = np.correlate(rawdata.iloc[:,1],rawdata.iloc[:,2],mode='same')
        # xcorr_yz = xcorr_yz/np.abs(np.sum(xcorr_yz)) #normalize values
        xcorr_peak_yz = np.max(xcorr_yz)
        xcorr_lag_yz = (np.argmax(xcorr_yz))/len(xcorr_yz)

        #pack xcorr features
        xcorr_peak = np.array([xcorr_peak_xy,xcorr_peak_xz,xcorr_peak_yz])
        xcorr_lag = np.array([xcorr_lag_xy,xcorr_lag_xz,xcorr_lag_yz])

        #Dominant freq and relative magnitude (on acc magnitude)
        Pxx = power_spectra_welch(rawdata_wmag,fm=0,fM=10)
        domfreq = np.asarray([Pxx.iloc[:,-1].idxmax()])
        Pdom_rel = Pxx.loc[domfreq].iloc[:,-1].values/Pxx.iloc[:,-1].sum() #power at dominant freq rel to total

        #moments of PSD
        Pxx_moments = np.array([np.nanmean(Pxx.values),np.nanstd(Pxx.values),skew(Pxx.values),kurtosis(Pxx.values)])

        #moments of jerk magnitude
        jerk = rawdata_wmag['Accel_Mag'].diff().values
        jerk_moments = np.array([np.nanmean(jerk),np.nanstd(jerk),skew(jerk[~np.isnan(jerk)]),kurtosis(jerk[~np.isnan(jerk)])])


        #Assemble features in array
        X = np.concatenate((RMS,r,mean,var,sk,kurt,xcorr_peak,xcorr_lag,domfreq,Pdom_rel,Pxx_moments,jerk_moments))
        features.append(X)

    F = np.asarray(features) #feature matrix for all clips from current trial
    clip_data['features'] = pd.DataFrame(data=F,columns=features_list,dtype='float32')

    
def reduced_feature_extraction_from_1_clip(a_clip_of_data):

    features_list = ['RMSX','RMSY','RMSZ','rangeX','rangeY','rangeZ','meanX','meanY','meanZ','varX','varY','varZ',
                    'skewX','skewY','skewZ','kurtX','kurtY','kurtZ','xcor_peakXY','xcorr_peakXZ','xcorr_peakYZ',
                    'xcorr_lagXY','xcorr_lagXZ','xcorr_lagYZ','Dom_freq','Pdom_rel','PSD_mean','PSD_std','PSD_skew',
                    'PSD_kur','jerk_mean','jerk_std','jerk_skew','jerk_kur']


    #cycle through all clips for current trial and save dataframe of features for current trial and sensor
    
    rawdata = a_clip_of_data
    #acceleration magnitude
    rawdata_wmag = rawdata.copy()
    rawdata_wmag['Accel_Mag']=np.sqrt((rawdata**2).sum(axis=1))

    #extract features on current clip

    #Root mean square of signal on each axis
    N = len(rawdata)
    RMS = 1/N*np.sqrt(np.asarray(np.sum(rawdata**2,axis=0)))

    #range on each axis
    min_xyz = np.min(rawdata,axis=0)
    max_xyz = np.max(rawdata,axis=0)
    r = np.asarray(max_xyz-min_xyz)

  
    #Moments on each axis
    mean = np.asarray(np.mean(rawdata,axis=0))
    var = np.asarray(np.std(rawdata,axis=0))
    sk = skew(rawdata)
    kurt = kurtosis(rawdata)


    #Cross-correlation between axes pairs
    xcorr_xy = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,1],mode='same')
    # xcorr_xy = xcorr_xy/np.abs(np.sum(xcorr_xy)) #normalize values
    xcorr_peak_xy = np.max(xcorr_xy)
    xcorr_lag_xy = (np.argmax(xcorr_xy))/len(xcorr_xy) #normalized lag

    xcorr_xz = np.correlate(rawdata.iloc[:,0],rawdata.iloc[:,2],mode='same')
    # xcorr_xz = xcorr_xz/np.abs(np.sum(xcorr_xz)) #normalize values
    xcorr_peak_xz = np.max(xcorr_xz)
    xcorr_lag_xz = (np.argmax(xcorr_xz))/len(xcorr_xz)

    xcorr_yz = np.correlate(rawdata.iloc[:,1],rawdata.iloc[:,2],mode='same')
    # xcorr_yz = xcorr_yz/np.abs(np.sum(xcorr_yz)) #normalize values
    xcorr_peak_yz = np.max(xcorr_yz)
    xcorr_lag_yz = (np.argmax(xcorr_yz))/len(xcorr_yz)

    #pack xcorr features
    xcorr_peak = np.array([xcorr_peak_xy,xcorr_peak_xz,xcorr_peak_yz])
    xcorr_lag = np.array([xcorr_lag_xy,xcorr_lag_xz,xcorr_lag_yz])

    #Dominant freq and relative magnitude (on acc magnitude)
    Pxx = power_spectra_welch(rawdata_wmag,fm=0,fM=10)
    domfreq = np.asarray([Pxx.iloc[:,-1].idxmax()]) #broken
    Pdom_rel = Pxx.loc[domfreq].iloc[:,-1].values/Pxx.iloc[:,-1].sum() #power at dominant freq rel to total

    #moments of PSD
    Pxx_moments = np.array([np.nanmean(Pxx.values),np.nanstd(Pxx.values),skew(Pxx.values),kurtosis(Pxx.values)])

    #moments of jerk magnitude
    jerk = rawdata_wmag['Accel_Mag'].diff().values
    jerk_moments = np.array([np.nanmean(jerk),np.nanstd(jerk),skew(jerk[~np.isnan(jerk)]),kurtosis(jerk[~np.isnan(jerk)])])


        #Assemble features in array
    X = np.concatenate((RMS,r,mean,var,sk,kurt,xcorr_peak,xcorr_lag,domfreq,Pdom_rel,Pxx_moments,jerk_moments))

    return X


