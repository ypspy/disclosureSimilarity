library(plyr)

h1 <- read.csv("C:/data2/voluntary_6_h2.similarity_length.txt")

h1$rawscore <- 1 - h1$similarity
h1$length <- as.double(h1$length)

length2 <- h1$length * h1$length
length3 <- length2 * h1$length
length4 <- length3 * h1$length
length5 <- length4 * h1$length

fit <- lm(h1$rawscore ~ h1$length + length2 + length3 + length4 + length5)

summary(fit)

h1$rawscoreHat <- fitted(fit)

h1$score <- h1$rawscore - h1$rawscoreHat
h1$len <- round_any(h1$length, 1000, f = ceiling)

write.csv(h1,"C:/data2/voluntary.h2.score.txt", row.names = FALSE)
