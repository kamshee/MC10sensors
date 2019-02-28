% myConvert_mp4toAvi_script
vidInName = 'C:\Users\adrory\Documents\myTestVideos\Drwg.mp4';
vidOutName = 'C:\Users\adrory\Documents\myTestVideos\Drwg.avi';

reader = VideoReader(vidInName);
writer = VideoWriter(vidOutName, 'Uncompressed AVI');

writer.FrameRate = reader.FrameRate;
open(writer);

% Read and write each frame.
while hasFrame(reader)
   img = readFrame(reader);
   resizedImg = imresize(img,0.25);
   writeVideo(writer,resizedImg);
end
[H,W,~] = size(resizedImg); 
fps = reader.FrameRate;
close(writer);

%%
videoPlayer = vision.VideoPlayer('Position', [100,100,W+20,H+20]);
videoFReader = vision.VideoFileReader(vidOutName);
while ~isDone(videoFReader)
videoFrame = videoFReader();
videoPlayer(videoFrame);
end
release(videoFReader);
release(videoPlayer);
%%
implay(vidOutName,fps);