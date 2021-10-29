import delimited C:\data\car\h1_variables.txt, clear
xtset x10 year

xtreg car_val score filelate car_e_val lnasset modified gc i.year, fe robust
ereturn list

su car_val score filelate car_e_val lnasset modified gc, detail
tab year
tabstat car_val score filelate car_e_val lnasset modified gc, by(year)
pwcorr car_val score filelate car_e_val lnasset modified gc, sig star(0.01)
