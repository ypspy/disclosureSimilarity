import delimited C:\data\car\h1_variables.txt, clear
xtset x10 year

xtreg car_val score filelate car_e_val lnasset roa leverage ocf modified gc i.year i.ksic_y, fe robust
ereturn list

reghdfe car_val score filelate car_e_val lnasset roa leverage ocf modified gc, absorb(ksic_y year x10) vce(cluster x10)

su car_val score filelate car_e_val lnasset modified gc, detail
tab year
tabstat car_val score filelate car_e_val lnasset roa leverage ocf modified gc, by(year)
pwcorr car_val score filelate car_e_val lnasset roa leverage ocf modified gc, sig star(0.01)

qui reg  car_val score filelate car_e_val lnasset roa leverage ocf modified gc
vif
