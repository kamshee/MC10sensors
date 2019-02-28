%% Data Science group meeting 4 Oct 2018
%% Feature Standardization
function Z = standardizeFeatures(X)
% Standardizes input features (also called Z-score normalization).
% Feature is rescaled to have properties of normal distribution
% \mu = 0 and \sigma = 1, where \mu is the mean and \sigma the standard
% variation. 
% Note: Mean centering does not affect covariance matrix. 
% Better for clustering, t-tests, ANOVA, Linear regression, LDA,
% Gaussian naive Bayes, decision trees
% **Caution: Should be applied to training set only, \mu and \sigma
% retained and then applied to test set**
%% Implements
% 
% $z = \frac{x-\mu}{\sigma}$
% 
% Inputs:
%           X:             1 x N array of features
%
% Output: 
%           Z:             1 x N array of standardised features
%
% Ami Drory 2018

%% Min-Max Scaling
function X_norm = minMaxNormalisation(X)
% Data is rescaled to a fixed range - 0 to 1 
% Often called rescaling. 
% End up with smaller standard deviation, whch can suppress effect of
% outliers. Better for SVM, KNN, image intensity
% Note: Scaling does affect the covariance matrix. Better for SVM, KNN
%% Implements
% 
% $X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}$
% 
% Inputs:
%           X:             1 x N array of features
%
% Output: 
%           X_norm:        1 x N array of rescaled features
%
% Ami Drory 2018
%% Mean normalisation
function X_norm = meanNormalisaion(X)
% Data is rescaled to a fixed range -1 to 1
% Often called rescaling. 
% End up with smaller standard deviation, whch can suppress effect of
% outliers. Better for SVM, KNN, image intensity
% Note: Scaling does affect the covariance matrix. Better for SVM, KNN
%% Implements
% 
% $X_{norm} = \frac{X - \bar{X}}{X_{max} - X_{min}}$
% 
% Inputs:
%           X:             1 x N array of features
%
% Output: 
%           X_norm:        1 x N array of mean normalised features
%
% Ami Drory 2018
