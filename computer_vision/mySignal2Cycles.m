function [cyclesData,cyclesDataMean] = mySignal2Cycles(signal,cycleLocs,dataLength)
numSigDimensions = ndims(signal);
if numSigDimensions < 3
    signal(:,:,1) = signal;
end
numCycles = size(cycleLocs,2)-1;
cyclesData =  zeros(numCycles,dataLength,numSigDimensions);
figure,
for signalDimenstionInd = 1:numSigDimensions
    for cycleInd = 1:numCycles
        nData = cycleLocs(cycleInd+1)-cycleLocs(cycleInd);
        cyclesData(cycleInd,:,signalDimenstionInd) = interp1(1:nData,...
            signal(signalDimenstionInd,cycleLocs(cycleInd):cycleLocs(cycleInd+1)-1),...
            linspace(1, nData, dataLength), 'linear') ;
    end
    
    singleDimenstionCycleData = cyclesData(:,:,signalDimenstionInd);
    cyclesDataMean = mean(singleDimenstionCycleData,1);
    subplot(2,numSigDimensions,signalDimenstionInd),
    plot(singleDimenstionCycleData'); hold on
    plot(cyclesDataMean,'linewidth',3); hold off;
    
    subplot(2,numSigDimensions,signalDimenstionInd+numSigDimensions),
    imagesc(singleDimenstionCycleData);
end    

