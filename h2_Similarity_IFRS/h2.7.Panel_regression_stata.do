import delimited C:\data\financials\h2_variables.txt, clear
xtset v2 year

xtreg score post ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first i.year i.ksic, fe robust
ereturn list

reghdfe score post ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, absorb(year v2 ksic) vce(cluster v2)

su score post ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, detail
tab year
tabstat score post ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, by(year)
pwcorr score post ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, sig star(0.01)

qui reg score post ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first
vif
