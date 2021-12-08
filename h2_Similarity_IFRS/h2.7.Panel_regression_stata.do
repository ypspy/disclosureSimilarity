import delimited C:\data\financials\h2_variables.txt, clear
xtset v2 year

// xtreg에서 two-way fixed effects // https://www.stata.com/statalist/archive/2010-05/msg00447.html

// xtreg score voluntary ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first i.ksic i.year, fe vce(cluster v2)
reghdfe score voluntary ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, absorb(ksic year) vce(cluster v2)

// xtreg score voluntary ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first i.year, fe vce(cluster v2)
reghdfe score voluntary ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, absorb(v2 year) vce(cluster v2)

su score voluntary ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, detail
tab year
tabstat score voluntary ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, by(year)
pwcorr score voluntary ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, sig star(0.01)

qui reg score voluntary ifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first
vif
