#include <stdlib.h>
#include <stdio.h>

//'var0' indidcates default value of var

//Make span in seconds
double make0 = 242;

//Window time in days
double window = 913;

//default price
double price0 = 6032.4;

//Component speeds, 's' is slow, 'n' is normal, 'f' is fast, 'x' means removed
char belt0 = 's';
char table0 = 'f';
char larm0 = 'n';
char rarm0 = 'n';


int main(int argc, char **argv){
	
	//Extract variables
	double make = (double) atoi(argv[1]);
	char belt =  argv[2][0];
	char table = argv[3][0];
	char larm =  argv[4][0];
	char rarm =  argv[5][0];
	int a = argv[6][0];

	//Check for number of changes
	int g = 0;
	if(belt0 != belt) g = g+1;
	if(table0 != table) g = g+1;;
	if(larm0 != larm) g = g+1;
	if(rarm0 != rarm) g = g+1;
	
	//compute delay
	double delay = a*28 + g*56;

	//compute bom
	double b = 0;
	if(belt=='s') {b=b+510;} else if(belt=='n') {b=b+1029;} else if(belt=='f') {b=b+1744;}
	if(table=='s'){b=b+133;} else if(table=='n'){b=b+634;} else if(table=='f') {b=b+919;}
	if(larm=='s') {b=b+798;} else if(larm=='n') {b=b+1299;} else if(larm=='f') {b=b+1529;}
	if(rarm=='s') {b=b+798;} else if(rarm=='n') {b=b+1299;} else if(rarm=='f') {b=b+1529;}
	
	//compute financial characteristics
	double price = 1.2* (b + 1000);
	double volume = 1500 + 2*(price0 - price) + 50*(make0 - make);
	if(volume < 0){volume = 0;}
	else {volume = volume * (1 - ((3*window - delay)*delay/(2*window*window)) );} 
	double cost = b*volume  + 72000*a + 108000*g;
	double profit = price*volume - cost;
	
	printf("Delay (days) = %f \n", delay);
	printf("Price (euro) = %f \n", price);
	printf("Volume = %f \n", volume);
	printf("Costs (euro)= %f \n", cost);
	printf("Profit = %f \n", profit);
	return 0;
}
