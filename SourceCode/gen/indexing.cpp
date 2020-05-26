#include<bits/stdc++.h>
#include<fstream>
using namespace std;
// using namespace std::chrono;
#define fast ios_base::sync_with_stdio(false);cin.tie(NULL);cout.tie(NULL);
typedef long long int ll;
typedef long int li;
typedef pair<int,int> ii;
typedef pair<ll,ll> pll;
typedef vector<int> vi;
typedef vector<ii> vpi;
#define For(a,b) for(ll i=a;i<b;i++)
#define Rev(b,a) for(ll i=b;i>=a;i--)
#define pb push_back
typedef vector<ll> vl;
typedef vector<pll> vpll;
int dirx[8] = {0,0,1,1,1,-1,-1,-1};
int diry[8] = {1,-1,0,1,-1,0,1,-1};
// auto start = high_resolution_clock::now();
// auto stop = high_resolution_clock::now();
// auto duration = duration_cast<microseconds>(stop-start);
// cout<<"execution time = "<<duration.count()<<endl;
// ofstream myfile("output.txt");
// ifstream infile("input.txt");

vector<string> c_file;
int linenum=0; // represents the index number
int i=0;	// represents the current line number of the iterator
int len;
bool line_break=false;

void multiline_comment()
{
	if(i>=len)
		return;

	string s;
	int initial_line = i;
	int comment_break_line;
	string temp_string;
	bool broken = false;

	while(i<len)
	{
		s = c_file[i];		
		for(int j=0;j<s.length();j++)
		{
			if(s[j]!=' ' && s[j]!='\t')
				temp_string += s[j];		// compressed string with no spaces or tabs
		}
		for(int j=0;j<temp_string.length();j++)
		{
			if(temp_string[j]=='*' && temp_string[j+1]=='/')
			{
				comment_break_line = i;
				broken = true;
				break;
			}
		}
		if(broken)
			break;
		i++;
	}
	// cout<<"comment break line number = "<<comment_break_line<<endl;
	// cout<<"break line number - "<<c_file[comment_break_line]<<endl;
	bool rare = false;

	// handle initial_line differently because it may or maynot be required to index
	s = c_file[initial_line];
	for(int j=0;j<s.length();j++)
		{
			if(s[j]!=' ' && s[j]!='\t')
				temp_string += s[j];		// compressed string with no spaces or tabs
		}

	if(initial_line == comment_break_line)
		rare = true;

	// BLOCK 8
	if(temp_string.length()<=3)
		{
			cout<<"BLOCK 8-"<<"  "<<s<<endl;	
		}

	else
		{
			int l = temp_string.length();
			if(rare)
			{
				// index this as after the multiline comment ends
				// there exist more than 1 character
				// so have to index this

				//BLOCK RARE-1
				if(temp_string[l-2]!='/' && temp_string[l-1]!='/')
				{
					cout<<linenum<<" "<<s<<endl;
					linenum++;
				}
				// BLOCK RARE 2
				else
				{
					if((temp_string[0]=='*' && temp_string[1]=='/' ) || 
						temp_string[0]=='{' && temp_string[1]=='*' && temp_string[2]=='/')
					{	
						cout<<"  "<<s<<endl;
					}

					else
					{
						cout<<linenum<<" "<<s<<endl;
						linenum++;
					}
				}
			}
			else
			{
				// BLOCK MLCPAT
				if((temp_string[0]=='/' && temp_string[1]=='*') || 
					(temp_string[0]=='{' && temp_string[1]=='/' && temp_string[2]=='*') )
				{
					// multiline comment starts at the begining of the line 
					// and doesnot break in the same line, since not rare
					// donot index this
					cout<<"  "<<s<<endl; 
				}
				// BLOCK MLCNPAT
				else
				{
					cout<<linenum<<" "<<s<<endl;
					linenum++;
				}
			}
		}
	// BLOCK WMLC
	for(int j=initial_line+1;j<comment_break_line;j++)
		cout<<"  "<<c_file[j]<<endl;

	if(!rare)
		{
			i = comment_break_line;
			line_break = true;
		}
	else
		i = initial_line+1;
}

int main()
	{
		fast
		// cout<<"Enter the file name: ";
		// string input_file_name;
		// cin>>input_file_name;
		// string final_file_path = "c_prog\\\\"+input_file_name;



		// final_file_path = "\""+final_file_path+"\"";
		// cout<<final_file_path<<endl;

		// freopen(final_file_path, "r", stdin);
		// string line;
		// if(infile.is_open())
		// {
		// 	cout<<"fine...."<<endl;
		// 	while ( getline (infile,line) )
		//     {
		//       cout << line << '\n';
		//     }
		//     infile.close();
		// }
		// else
		// {
		// 	cout<<"file doesnot exist..."<<endl;
		// }

		
		string s;
		
		while(getline(cin, s))
		{
			c_file.pb(s);
			// cout<<s<<endl;
		}
		// cout<<c_file.size()<<endl;
		len = c_file.size();
		

		//flag
		bool is_multiline = false;

		while(i<len)
		{
			s = c_file[i];
			string temp_string;
			for(int j=0;j<s.length();j++)
			{
				if(s[j]!=' ' && s[j]!='\t')
					temp_string += s[j];		// compressed string with no spaces or tabs
			}
			// cout<<temp_string<<endl;

			//BLOCK 1
			if(temp_string.length()==1 && (temp_string[0]=='{' || temp_string[0]=='}'))
			{
				// case when the line contains only '{' or '}' and spaces or tabs
				// donot index this line
				cout<<"  "<<s<<endl;
			}
			//BLOCK 2
			else if(temp_string.length()==0)
			{
				// case when its a blank line or contains only spaces or tabs
				// donot index this line
				cout<<"  "<<s<<endl;
			}
			// BLOCK 3
			else if(temp_string.length()>=2 && temp_string[0]=='/' && temp_string[1]=='/')
			{
				// single line comment case 
				// donot index this line
				cout<<"  "<<s<<endl;
			}
			//BLOCK 4
			else if(temp_string.length()>=3 && (temp_string[0]=='{' || temp_string[0]=='}') 
					&& temp_string[1]=='/' && temp_string[2]=='/') 
			{
				// single line comment case just after '{' or '}'
				// donot index this line
				cout<<"  "<<s<<endl;
			}

			else if(temp_string.length()>=2 && line_break)
			{
				int l = temp_string.length();
				// BLOCK 5
				if( (temp_string[l-2]=='*' && temp_string[l-1]=='/') || 
					(temp_string[l-1]=='}' && temp_string[l-2]=='/' && temp_string[l-3]=='*')
					)
					cout<<"  "<<s<<endl;
				// BLOCK 6
				else
					{
						cout<<linenum<<" "<<s<<endl;
						linenum++;
					}
			}	
			else
			{
				for(int k=0;k<temp_string.length()-1;k++)
				{
					if(temp_string[k]=='/' && temp_string[k+1]=='*')
					{
						is_multiline = true;
						multiline_comment();
						break;
					}
				}

				if(is_multiline)
				{
					is_multiline = false;
					continue;
				}
				// BLOCK 7
				else
				{	
					if(temp_string == "else" || temp_string == "else{")
					{
						cout<<"  "<<s<<endl;
					}
					else
					{	
						cout<<linenum<<" "<<s<<endl;
						linenum++;
					}
				}
			}
			line_break = false;
			i++;
		}


		return 0;
	}