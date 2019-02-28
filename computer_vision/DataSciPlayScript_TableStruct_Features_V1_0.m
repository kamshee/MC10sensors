%% Data Science Playground - Table data structure and features v1.0
%% DataSciPlayScript_TableStruct_Features_V1_0.m
% Ami Drory 5 Oct 2018
clear all
inPath = '\\FS2.smpp.local\RTO\CIS-PD Study\ComputerVision';
addpath(inPath);

%% load table structure
load('PD_DrawingVideo_table.mat');
% to look at the table double click on Participants variable in your
% workspace

%% How to create a similar table for your purposes
% example table labelling
PD = {true;true}; % Binary disease state pos/neg, Y = PD +ve
SubjectID = {'ciscid4';'ciscid5'}; % Subject ID
Cycle = [3;2]; % Testing Cycle
DrwgFilePath = {'	\ciscid4\cycle3';'C:\Users\adrory\Documents\myTestVideos'}; % Path to drawing video
Frames = [1 -1;1 -1]; % Start and end frame , -1 indicates end of file
myParticipants = table(PD, SubjectID, Cycle,DrwgFilePath,Frames); % Create data table
%% To add a new participant
testSubjectId100 = {false,'newSubjectID',6,'Y:\CIS-PD Videos\ciscid100\cycle6',[1 -1]};
myParticipants = [myParticipants;testSubjectId100];
%% To save table to current path
%  save('myFileName.mat','myParticipants'); Please be careful not to
%  overwrite my original table with features
%% extract features and inspect
fhofoFeatures = Participants.FhofoFeatures;
figure;
hold on;
cellfun(@plot,fhofoFeatures); % inspect
%% delete leading zeros from signal
noZerosFeatures = cell(size(fhofoFeatures));
zeroMeanFeatures = noZerosFeatures;
for k = 1:size(fhofoFeatures,1)
    nonZeroInd = find(fhofoFeatures{k,1},~0,'first'); %works on one cell
    noZerosFeatures{k,1} = fhofoFeatures{k,1}(1,nonZeroInd:end);
end
% inspect
figure;
hold on;
cellfun(@plot,noZerosFeatures);
%% extract feature vector for one subject
SubjectInd = 1;
featureVect = Participants.FhofoFeatures{1};
%% add feature to your new table 
newFeatures = cell(size(myParticipants,1),1);
myParticipants.BestFeatures = newFeatures;
myParticipants.BestFeatures{SubjectInd} = featureVect;

%% Dynamic Time Warping
dtw(noZerosFeatures{1,1},noZerosFeatures{2,1});
%% Plot warping path
figure(1)
[~,xi1,yi1] = dtw(noZerosFeatures{1,1},noZerosFeatures{2,1});
plot(xi1,yi1);

%% mean normalisation and feature scaling - zero mean \miu=0
% IMPORTANT: for some ML approaches normalisation requires unit length
% variance

for k = 1:size(fhofoFeatures,1)
    normalized_Features{k,1} = (noZerosFeatures{k,1}-mean(noZerosFeatures{k,1}))/range(noZerosFeatures{k,1},2);
end
figure;
hold on;
cellfun(@plot,normalized_Features);

%% out of curiosity, if you want to know what these features are
% Fuzzy histogram of oriented optical flow
inVidPath = [inPath,'\results\'];
addpath(inVidPath);
vidFileName = 'ciscid4_cycle5_HOF.avi';
VidFileIn = [inVidPath,vidFileName];
implay(VidFileIn); % maximise window and click play





