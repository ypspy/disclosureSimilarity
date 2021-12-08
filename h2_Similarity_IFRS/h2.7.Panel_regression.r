library(plm)

Panel <- read.csv("C:/data/financials/h2_variables.txt")

fixed <- plm(score ~ post + ifrs + post:ifrs + adopt + dROA + dCURRENT
             + dDEBTDUE + dLEVERAGE + dFCF + merger + split + big + first
             + factor(KSIC)
             , data=Panel, index=c("X10", "year")
             , effect = "twoway" 
             , model="within")

summary(fixed)

library(fixest)