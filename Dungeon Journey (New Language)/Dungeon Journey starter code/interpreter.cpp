#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>
using namespace std;

struct state{
	int set[2];
	int xs[2];
	int ys[2];
};

void fil(int b,int p,state *e){
	if(b==-1){
		e->xs[p]=0;
		e->ys[p]=0;
	}else if(b=='U'-'0'){
		e->xs[p]=0;
		e->ys[p]=-1;
	}else if(b=='D'-'0'){
		e->xs[p]=0;
		e->ys[p]=1;
	}else if(b=='L'-'0'){
		e->xs[p]=-1;
		e->ys[p]=0;
	}else if(b=='R'-'0'){
		e->xs[p]=1;
		e->ys[p]=0;
	}
}

int main(int argc,char *argv[]){
	if(argc<2){
		cout<<"Too few arguments\n";
		return 0;
	}
	fstream sol(argv[1]);
	map<pair<int,int>,state> states;
	string s;
	while(getline(sol,s)){
		if(!s.size()||s[0]=='%')continue;
		s+=',';
		pair<int,int> c;
		state e;bool k=1;
		int buf=0,o=0;
		for(char x:s){
			if(k){
				if(x==' '){
					c.second=buf;
					buf=0;k=0;
					continue;
				}
				if(x==','){
					c.first=buf;
					buf=0;
					continue;
				}
				buf=buf*10+x-'0';
				continue;
			}
			if(x==','){
				if(o==0)e.set[0]=buf;
				if(o==1)e.set[1]=buf;
				if(o==2)fil(buf,0,&e);
				if(o==3)fil(buf,1,&e);
				buf=0;++o;
				continue;
			}
			if(x=='_')buf=-1;
			else buf=buf*10+x-'0';
		}
		if(states.count(c))
			cout<<"Duplicate transformation "<<c.first<<','<<c.second<<'\n';
		else states[c]=e;
	}
	int radius=100;
	if(argc>3){
		radius=stoi(argv[3]);
		cout<<"Using radius "<<radius<<'\n';
	}
	++radius;
	vector<vector<int>> board(radius<<1,vector<int>(radius<<1,0));
	if(argc>2){
		int buf[]={0,0,0};
		string s=argv[2];s+=' ';
		int o=0;
		for(char x:s){
			if(x==',')++o;
			else if(x==' '){
				board[buf[0]+radius][buf[1]+radius]=buf[2];
				for(int i=0;i<3;++i)buf[i]=0;
				o=0;
			}else buf[o]=buf[o]*10+x-'0';
		}
	}
	int days=10000;
	if(argc>4){
		days=stoi(argv[4]);
		cout<<"Running on maximum "<<days<<" days\n";
	}
	int a[]={radius,radius},b[]={radius,radius},
		xbound[]={radius,radius},ybound[]={radius,radius};
	bool halt=0;
	while(days--){
		if(a[0]<0||a[0]>=radius<<1){
			cout<<"Alice out of bounds - "<<a[0]-radius<<','<<a[1]-radius<<'\n';
			break;
		}
		if(b[0]<0||b[0]>=radius<<1){
			cout<<"Bob out of bounds - "<<b[0]-radius<<','<<b[1]-radius<<'\n';
			break;
		}
		pair<int,int> s=make_pair(board[a[0]][a[1]],board[b[0]][b[1]]);
		if(states.count(s)){
			state x=states[s];
			if(x.set[1]+1)board[b[0]][b[1]]=x.set[1];
			if(x.set[0]+1)board[a[0]][a[1]]=x.set[0];
			a[0]+=x.xs[0];a[1]+=x.ys[0];
			b[0]+=x.xs[1];b[1]+=x.ys[1];
			if(x.set[1]<0&&x.set[0]<0&&x.xs[0]==0&&x.xs[1]==0&&
					x.ys[0]==0&&x.ys[1]==0){halt=1;break;}
			xbound[0]=(a[0]<xbound[0]?a[0]:xbound[0]);
			xbound[1]=(a[0]>xbound[1]?a[0]:xbound[1]);
			ybound[0]=(a[1]<ybound[0]?a[1]:ybound[0]);
			ybound[1]=(a[1]>ybound[1]?a[1]:ybound[1]);
			xbound[0]=(b[0]<xbound[0]?b[0]:xbound[0]);
			xbound[1]=(b[0]>xbound[1]?b[0]:xbound[1]);
			ybound[0]=(b[1]<ybound[0]?b[1]:ybound[0]);
			ybound[1]=(b[1]>ybound[1]?b[1]:ybound[1]);
		}else{
			cout<<"Missing rule "<<s.first<<','<<s.second<<'\n';
			break;
		}
	}
	if(xbound[1]>=radius<<1)xbound[1]=radius<<1-1;
	if(ybound[1]>=radius<<1)ybound[1]=radius<<1-1;
	if(xbound[0]<0)xbound[0]=0;
	if(ybound[0]<0)ybound[0]=0;
	if(1||halt)for(int i=ybound[1];i>=ybound[0];--i){
		for(int j=xbound[0];j<=xbound[1];++j){
			if(board[j][i]==0)cout<<'_';
			else cout<<board[j][i];
		}
		cout<<'\n';
	}
}
