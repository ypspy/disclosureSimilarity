import delimited C:\data\financials\h2_variables.txt, clear
xtset v2 year
gen postxifrs = post*ifrs

xtreg score post ifrs postxifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first i.year, fe robust
ereturn list

su score post ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, detail
tab year
tabstat score post ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, by(year)
pwcorr score post ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, sig star(0.01)
