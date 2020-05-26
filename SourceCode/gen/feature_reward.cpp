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

// add the logic to include negative score elements also if possible
// tool to compute all possible slices of a c program

int main()
	{
		fast

		cout<<"*************\nUSE THE DEBUG STATEMENTS TO ENTER 0/1 TO PRINT/NOT PRINT\nTHE REQUIRED VECTORS WHICH ARE HIGHLY USEFUL WHILE DEBUGGING\n"<<"************\n"<<endl;

		int potential_lines,j;
		int full_penalty=2,full_reward=2;
		int semi_penalty=1,semi_reward=1;
		int number_of_features=29;
		cout<<"Enter the number of potential lines: "<<endl;
		cin>>potential_lines;
		int feature[potential_lines][number_of_features],w[number_of_features];

		for(int i=0;i<number_of_features;i++)
			w[i] = 0;	// initialization

		
		int set_line_size=0;

		int flag;
		cout<<"Enter 1 to print the random feature vector of each potential line else 0: "<<endl;
		cin>>flag;

		if(flag)
			cout<<"Feature vector: "<<endl;
		// filling up the random feature vector for each potential line
		for(int i=0;i<potential_lines;i++)
		{
			for(j=0;j<number_of_features;j++)
			{
				// int k = rand()%2;
				feature[i][j] = rand()%2;
				// feature[i][j] = feature[i][j] & k;
				if(j==number_of_features-1 && feature[i][j])
					set_line_size++;

				if(j==number_of_features-2 && flag==1)	// to segregate the label aside while printing
					cout<<feature[i][j]<<" -> ";
				else if(flag==1)
					cout<<feature[i][j]<<" ";
			}
			if(flag==1)
				cout<<endl;
		}
		if(flag==1)
			cout<<endl;

		// calculating the optimal hyperparameter vector by giving rewards and penalties
		for(int i=0;i<potential_lines;i++)
		{
			if(feature[i][number_of_features-1]==1)		// if the label of the line is turned on
			{
				for(int j=0;j<number_of_features;j++)
				{
					if(feature[i][j]==1)
						w[j]+=full_reward;		// giving reward to the feature if the label is set
					else
						w[j]-=semi_penalty;		// giving semi penalty since this feature should ideally remain
				}								// unset as the label is set for this line
			}
			else
			{
				for(int j=0;j<number_of_features;j++)
				{
					if(feature[i][j]==1)
						w[j]-=full_penalty;		// giving negative reward since label is unset but the feature is present
					else
						w[j]+=semi_reward;	
				}	
			}
		}

		vector<pair<int,int> > score_vector;

		cout<<"Enter 1 to print the hyperparameter vector(w), else enter 0: "<<endl;
		cin>>flag;

		if(flag==1)
		{
			cout<<"Hyperparameter vector: "<<endl;
			for(int i=0;i<29;i++)
				cout<<w[i]<<" ";
			cout<<endl;
		}

		for(int i=0;i<potential_lines;i++)
		{
			// cout<<"Line "<<i+1<<" score: ";
			int score=0;
			for(int j=0;j<29;j++)
			{
				score += w[j]*feature[i][j];
			}
			// cout<<score<<endl;
			score_vector.pb(make_pair(score,i+1));
		}
		cout<<endl;
		sort(score_vector.begin(),score_vector.end(),greater<pair<int,int> >());
		vector<int> actual_slice;

		cout<<"Enter 1 to print the descending order of line scores with line number, else 0: "<<endl;
		cin>>flag;

		if(flag==1)
			cout<<"Descending order of line scores with line numbers: "<<endl;
		for(int i=0;i<potential_lines;i++)
			{
				if(flag==1)
					cout<<"("<<score_vector[i].first<<","<<score_vector[i].second<<")"<<endl;
				if(i<set_line_size)
					actual_slice.pb(score_vector[i].second);
			}
		if(flag==1)	
			cout<<endl;

		sort(actual_slice.begin(),actual_slice.end());

		cout<<endl<<"Actual Slice: (";
		for(int i=0;i<set_line_size;i++)
			{
				if(i<set_line_size-1)
					cout<<actual_slice[i]<<",";
				else
					cout<<actual_slice[i]<<")"<<endl;
			}
	
		double highest_score = score_vector[0].first;
		double current_score;
		vector<int> predicted_slice;
		
		for(int i=0;i<potential_lines;i++)
		{
			current_score = score_vector[i].first;
			if(current_score >= highest_score/2.0)
				predicted_slice.pb(score_vector[i].second);
			else
				break;
		}	

		sort(predicted_slice.begin(),predicted_slice.end());
		cout<<endl<<"predicted_slice: (";
		for(int i=0;i<predicted_slice.size();i++)
		{
			if(i!=0)
				cout<<","<<predicted_slice[i];
			else
				cout<<predicted_slice[i];
		}
		cout<<")"<<endl<<endl;
	
		cout<<"length of actual slice: "<<actual_slice.size()<<endl;
		cout<<"length of predicted slice: "<<predicted_slice.size()<<endl;

		int difference_elements[potential_lines+1];
		// used to find the elements included, excluded or garbage values in the predicted slice

		double actual_slice_size,inclusion_factor=0,exclusion_factor=0,garbage_factor=0;

		vector<int> included,excluded,garbage;

		actual_slice_size = actual_slice.size();

		for(int i=1;i<=potential_lines;i++)
		{
			difference_elements[i] = 0;
		}
		for(int i=0;i<actual_slice.size();i++)
		{
			difference_elements[actual_slice[i]]+=2;
		}
		for(int i=0;i<predicted_slice.size();i++)
		{
			difference_elements[predicted_slice[i]]++;
		}

		for(int i=1;i<=potential_lines;i++)
		{
			if(difference_elements[i]==3)
				{
					inclusion_factor += 1.0;
					included.pb(i);
				}
			else if(difference_elements[i]==2)
				{
					exclusion_factor += 1.0;
					excluded.pb(i);
				}
			else if(difference_elements[i]==1)
				{
					garbage_factor += 1.0;
					garbage.pb(i);
				}
		}

		// cout<<"actual slice size = "<<actual_slice_size<<endl;
		// cout<<"INCLUSION FACTOR = "<<inclusion_factor<<endl;
		cout<<"Inclusion factor = "<< inclusion_factor/actual_slice_size<<endl;
		cout<<"Exclusion factor = "<< exclusion_factor/actual_slice_size<<endl;
		cout<<"Garbage factor = "<< garbage_factor/actual_slice_size<<endl;

		cout<<"Included elements: {";
		for(int i=0;i<included.size();i++)
		{
			if(i!=0)
			{
				cout<<","<<included[i];
			}
			else
				cout<<included[i];
		}
		cout<<"}"<<endl;

		cout<<"Excluded elements: {";
		for(int i=0;i<excluded.size();i++)
		{
			if(i!=0)
			{
				cout<<","<<excluded[i];
			}
			else
				cout<<excluded[i];
		}
		cout<<"}"<<endl;

		cout<<"Garbage elements included in the predicted slice: {";
		for(int i=0;i<garbage.size();i++)
		{
			if(i!=0)
			{
				cout<<","<<garbage[i];
			}
			else
				cout<<garbage[i];
		}
		cout<<"}"<<endl;
		return 0;
	}