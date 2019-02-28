%% myDTW
% simple test case signals
A = [1, 2, 2, 3, 4, 3, 2, 2]; 
B = [1, 2, 3, 4,4,2];

[row,M]=size(A); if (row > M) M=row; A=A'; end
[row,N]=size(B); if (row > N) N=row; B=B'; end
% Distance matrix calc
distMtx =(repmat(A',1,N)-repmat(B,M,1)).^2;
% distMtx = flip(distMtx,1);

image(distMtx);
cmap = contrast(distMtx);
% colormap(cmap); % 'copper' 'bone', 'gray'
imagesc(distMtx);

%% visualisation
    figure('Name','DTW - Distance matrix', 'NumberTitle','off');
    
    main1=subplot('position',[0.19 0.19 0.67 0.79]);
    heatmap(distMtx); 
    cmap = contrast(distMtx);
    colormap(cmap); % 'copper' 'bone', 'gray' imagesc(D);
       
    left1=subplot('position',[0.07 0.19 0.10 0.79]);
    plot(-A,M:-1:1,'-b');
    axis off

    bottom1=subplot('position',[0.19 0.07 0.67 0.10]);
    plot(B,'-r');
    axis off
%% Constructing the accumulation cost matrix
AccumMtx=zeros(size(distMtx));
AccumMtx(1,1)=distMtx(1,1);

for m=2:M
    AccumMtx(m,1)=distMtx(m,1)+AccumMtx(m-1,1);
end
for n=2:N
    AccumMtx(1,n)=distMtx(1,n)+AccumMtx(1,n-1);
end
for m=2:M
    for n=2:N
        AccumMtx(m,n)=distMtx(m,n)+min(AccumMtx(m-1,n),min(AccumMtx(m-1,n-1),AccumMtx(m,n-1))); % this double MIn construction improves in 10-fold the Speed-up. Thanks Sven Mensing
    end
end

Dist=AccumMtx(M,N);
n=N;
m=M;
k=1;
w=[M N];
while ((n+m)~=2)
    if (n-1)==0
        m=m-1;
    elseif (m-1)==0
        n=n-1;
    else 
      [values,number]=min([AccumMtx(m-1,n),AccumMtx(m,n-1),AccumMtx(m-1,n-1)]);
      switch number
      case 1
        m=m-1;
      case 2
        n=n-1;
      case 3
        m=m-1;
        n=n-1;
      end
  end
    k=k+1;
    w=[m n; w];  
end

% warped waves
Awarped=A(w(:,1));
Bwarped=B(w(:,2));
%% visualisation
    figure, 
        
    image(AccumMtx);
    hold on;
    plot(w(:,2),w(:,1),'r'); hold off
    
    figure('Name','DTW - Accumulation matrix', 'NumberTitle','off');
    
    main1=subplot('position',[0.19 0.19 0.67 0.79]);
    heatmap(AccumMtx); 
    cmap = contrast(AccumMtx);
    colormap(cmap); % 'copper' 'bone', 'gray' imagesc(D);
       
    left1=subplot('position',[0.07 0.19 0.10 0.79]);
    plot(-A,M:-1:1,'-b');
    axis off

    bottom1=subplot('position',[0.19 0.07 0.67 0.10]);
    plot(B,'-r');
    axis off

    figure, 
    subplot(211);
    plot(A);hold on
    plot(B);
    subplot(212);
    plot(Awarped);hold on
    plot(Bwarped);
%% Constraint on reference move
%% Constructing the accumulation cost matrix
AccumMtx=zeros(size(distMtx));
AccumMtx(1,1)=distMtx(1,1);

for m=2:M
    AccumMtx(m,1)=distMtx(m,1)+AccumMtx(m-1,1);
end
for n=2:N
    AccumMtx(1,n)=distMtx(1,n)+AccumMtx(1,n-1);
end
for m=2:M
    for n=2:N
        AccumMtx(m,n)=distMtx(m,n)+min(AccumMtx(m-1,n),min(AccumMtx(m-1,n-1),AccumMtx(m,n-1))); % this double MIn construction improves in 10-fold the Speed-up. Thanks Sven Mensing
    end
end

Dist=AccumMtx(M,N);
n=N;
m=M;
k=1;
w=[M N];
while ((n+m)~=2)
    if (n-1)==0
        m=m-1;
    elseif (m-1)==0
        n=n-1;
    else 
      [values,number]=min([AccumMtx(m-1,n),AccumMtx(m,n-1),AccumMtx(m-1,n-1)]);
      switch number
      case 1
        m=m-1;
%       case 2
%         n=n-1;
%       case 3
          otherwise
        m=m-1;
        n=n-1;
      end
  end
    k=k+1;
    w=[m n; w];  
end

% warped waves
Awarped=A(w(:,1));
Bwarped=B(w(:,2));
%% visualisation
    figure, 
        
    image(AccumMtx);
    hold on;
    plot(w(:,2),w(:,1),'r'); hold off
    
    figure('Name','DTW - Accumulation matrix', 'NumberTitle','off');
    
    main1=subplot('position',[0.19 0.19 0.67 0.79]);
    heatmap(AccumMtx); 
    cmap = contrast(AccumMtx);
    colormap(cmap); % 'copper' 'bone', 'gray' imagesc(D);
       
    left1=subplot('position',[0.07 0.19 0.10 0.79]);
    plot(-A,M:-1:1,'-b');
    axis off

    bottom1=subplot('position',[0.19 0.07 0.67 0.10]);
    plot(B,'-r');
    axis off

    figure, 
    subplot(211);
    plot(A);hold on
    plot(B);
    subplot(212);
    plot(Awarped);hold on
    plot(Bwarped);
    
%% Multiple signals
C = [1, 2, 3, 4, 3, 3, 2];
[row,O]=size(C); if (row > O) O=row; C=C'; end
% Distance matrix calc
distMtx2 =(repmat(A',1,O)-repmat(C,M,1)).^2;
% distMtx = flip(distMtx,1);
figure,
% heatmap(distMtx2);
% cmap = contrast(distMtx2);
% colormap(cmap); % 'copper' 'bone', 'gray'
 imagesc(distMtx);
%% visualisation
    figure('Name','DTW - Distance matrix2', 'NumberTitle','off');
    
    main1=subplot('position',[0.19 0.19 0.67 0.79]);
    heatmap(distMtx2); 
    cmap = contrast(distMtx2);
    colormap(cmap); % 'copper' 'bone', 'gray' imagesc(D);
       
    left1=subplot('position',[0.07 0.19 0.10 0.79]);
    plot(-A,M:-1:1,'-b');
    axis off

    bottom1=subplot('position',[0.19 0.07 0.67 0.10]);
    plot(C,'-r');
    axis off
%% Constructing the accumulation cost matrix
AccumMtx2=zeros(size(distMtx2));
AccumMtx2(1,1)=distMtx2(1,1);

for m=2:M
    AccumMtx2(m,1)=distMtx2(m,1)+AccumMtx2(m-1,1);
end
for o=2:O
    AccumMtx2(1,o)=distMtx2(1,o)+AccumMtx2(1,o-1);
end
for m=2:M
    for o=2:O
        AccumMtx2(m,o)=distMtx2(m,o)+min(AccumMtx2(m-1,o),min(AccumMtx2(m-1,o-1),AccumMtx2(m,o-1))); % this double MIn construction improves in 10-fold the Speed-up. Thanks Sven Mensing
    end
end

Dist2=AccumMtx2(M,O);
o=O;
m=M;
k=1;
w2=[M O];
while ((o+m)~=2)
    if (o-1)==0
        m=m-1;
    elseif (m-1)==0
        o=o-1;
    else 
      [values,number]=min([AccumMtx2(m-1,o),AccumMtx2(m,o-1),AccumMtx2(m-1,o-1)]);
      switch number
      case 1
        m=m-1;
%       case 2
%         n=n-1;
%       case 3
          otherwise
        m=m-1;
        o=o-1;
      end
  end
    k=k+1;
    w2=[m o; w2];  
end

% warped waves
Awarped=A(w2(:,1));
Cwarped=C(w2(:,2));
%% visualisation
    figure, 
        
    image(AccumMtx2);
    hold on;
    plot(w2(:,2),w2(:,1),'r'); hold off
    
    figure('Name','DTW - Accumulation matrix', 'NumberTitle','off');
    
    main1=subplot('position',[0.19 0.19 0.67 0.79]);
    heatmap(AccumMtx2); 
    cmap = contrast(AccumMtx2);
    colormap(cmap); % 'copper' 'bone', 'gray' imagesc(D);
       
    left1=subplot('position',[0.07 0.19 0.10 0.79]);
    plot(-A,M:-1:1,'-b');
    axis off

    bottom1=subplot('position',[0.19 0.07 0.67 0.10]);
    plot(C,'-r');
    axis off
%%
    figure, 
    subplot(211);
    plot(A);hold on
    plot(B);
    plot(C);
    subplot(212);
    plot(Awarped);hold on
    plot(Bwarped);   
    plot(Cwarped);
%% testing my myOneSidedDtw
[Dist,D,k,w,rw,tw]=myOneSidedDtw(A,B,1);
%%