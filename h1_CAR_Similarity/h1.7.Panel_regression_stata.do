import delimited C:\data\car\h1_variables.txt, clear
xtset x10 year

reghdfe car_val score filelate car_e_val lnasset roa leverage ocf modified gc, absorb(ksic_y year) vce(cluster x10)
reg car_val score filelate car_e_val lnasset roa leverage ocf modified gc i.ksic_y i.year, vce(cluster x10)

reghdfe car_val score filelate car_e_val lnasset roa leverage ocf modified gc if ifrs == 1, absorb(ksic_y year) vce(cluster x10)
reghdfe car_val score filelate car_e_val lnasset roa leverage ocf modified gc if ifrs == 0, absorb(ksic_y year) vce(cluster x10)

reghdfe car_val score filelate car_e_val lnasset roa leverage ocf modified gc, absorb(x10 year) vce(cluster x10)

su car_val score filelate car_e_val lnasset roa leverage ocf modified gc, detail
tab year
tabstat car_val score filelate car_e_val lnasset roa leverage ocf modified gc, by(year)
pwcorr car_val score filelate car_e_val lnasset roa leverage ocf modified gc, sig star(0.01)

qui reg  car_val score filelate car_e_val lnasset roa leverage ocf modified gc
vif
