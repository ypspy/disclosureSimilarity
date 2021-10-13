h1 <- read.csv("C:/data/h1.similarity_length.txt")

h1$rawscore <- 1 - h1$similarity

length2 <- h1$length * h1$length
length3 <- length2 * h1$length
length4 <- length3 * h1$length
length5 <- length4 * h1$length

fit <- lm(h1$rawscore ~ h1$length + length2 + length3 + length4 + length5)

summary(fit)

h1$score <- fitted(fit)

write.csv(h1,"C:/data/h1.score.txt", row.names = FALSE)
