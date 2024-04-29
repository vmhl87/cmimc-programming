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
	string NE="\e[0m",GR="\e[32m",RE="\e[31m",CY="\e[36m",YL="\e[33m";
	if(argc<2){
		cout<<RE<<"Too few arguments\n"<<NE;
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
			if(x=='_')buf=-1;
			else if((x>='0'&&x<='9')||x=='U'||x=='D'||x=='R'||x=='L')
				buf=buf*10+x-'0';
			else{
				if(o==0)e.set[0]=buf;
				if(o==1)e.set[1]=buf;
				if(o==2)fil(buf,0,&e);
				if(o==3)fil(buf,1,&e);
				buf=0;++o;
				if(o==4)break;
			}
		}
		if(states.count(c))
			cout<<RE<<"Duplicate transformation "<<c.first<<','
				<<c.second<<NE<<'\n';
		else states[c]=e;
	}
	int radius=100;
	if(argc>4){
		radius=stoi(argv[4]);
		cout<<CY<<"Using radius "<<radius<<NE<<'\n';
	}
	++radius;
	int a[]={radius,radius},b[]={radius,radius},
		xbound[]={radius,radius},ybound[]={radius,radius};
	vector<vector<int>> board(radius<<1,vector<int>(radius<<1,0));
	if(argc>2){
		int buf[]={0,0,0},sign=1;
		string s=argv[2];s+=' ';
		int o=0;
		for(char x:s){
			if(x==','){
				buf[o]*=sign;sign=1;
				++o;
			}else if(x==' '){
				board[buf[0]+radius][buf[1]+radius]=buf[2];
				xbound[0]=(buf[0]+radius<xbound[0]?buf[0]+radius:xbound[0]);
				xbound[1]=(buf[0]+radius>xbound[1]?buf[0]+radius:xbound[1]);
				ybound[0]=(buf[1]+radius<ybound[0]?buf[1]+radius:ybound[0]);
				ybound[1]=(buf[1]+radius>ybound[1]?buf[1]+radius:ybound[1]);
				for(int i=0;i<3;++i)buf[i]=0;
				o=0;
			}else if(x=='-')sign=-1;
			else buf[o]=buf[o]*10+x-'0';
		}
	}
	int days=100000;
	if(argc>3){
		days=stoi(argv[3]);
		cout<<CY<<"Running on maximum "<<days<<" days\n"<<NE;
	}
	bool halt=0;
	while(days--){
		if(a[0]<0||a[0]>=(radius<<1)||a[1]<0||a[1]>=(radius<<1)){
			cout<<RE<<"Alice out of bounds - "<<a[0]-radius<<','
				<<a[1]-radius<<NE<<'\n';
			break;
		}
		if(b[0]<0||b[0]>=(radius<<1)||b[1]<0||b[1]>=(radius<<1)){
			cout<<RE<<"Bob out of bounds - "<<b[0]-radius
				<<','<<b[1]-radius<<NE<<'\n';
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
			cout<<RE<<"Missing rule "<<s.first<<','<<s.second<<NE<<'\n';
			break;
		}
	}
	--xbound[0];--ybound[0];
	++xbound[1];++ybound[1];
	if(xbound[1]>=radius<<1)xbound[1]=(radius<<1)-1;
	if(ybound[1]>=radius<<1)ybound[1]=(radius<<1)-1;
	if(xbound[0]<0)xbound[0]=0;
	if(ybound[0]<0)ybound[0]=0;
	if(1||halt)for(int i=ybound[1];i>=ybound[0];--i){
		for(int j=xbound[0];j<=xbound[1];++j){
			if(j==a[0]&&i==a[1])cout<<YL;
			else if(j==b[0]&&i==b[1])cout<<GR;
			if(board[j][i]==0){
				if(j==a[0]&&i==a[1])cout<<'x';
				else if(j==b[0]&&i==b[1])cout<<'x';
				else cout<<'_';
			}else cout<<board[j][i];
			cout<<NE;
		}
		cout<<'\n';
	}
}
