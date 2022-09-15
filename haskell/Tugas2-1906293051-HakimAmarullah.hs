{-
Author  : Hakim Amarullah
NPM     : 1906293051
version : 1.0
updated : Thu 14/09/2022

Disclaimer: This code was not originally created by the specified author. Recreated for learning purposes.
-}

import Data.Char

-- Soal 1 Sum Of Squares
sumOfSquares :: [Integer] -> Integer
sumOfSquares = sum . map (\x -> x^2)

-- Soal 2 triangular
triangular :: Integer -> Integer
triangular n
           | n <= 0 = n
           | otherwise = n + triangular (n-1)

-- Soal 3 power
power :: Integer -> Integer -> Integer
power a b 
          | b < 0 = error "Only Positive Number"
          | b == 0 = 1
          | otherwise = a * power a (b-1)

-- -- Soal 4 Palindrome
isPalindrome :: String -> Bool
isPalindrome str = isPalindromeHelper $ (filter (\x -> x `elem` ['a'..'z'])) $ map toLower str
             where isPalindromeHelper str
                                      | length str < 2 = True
                                      | (head str) /= (last str) = False
                                      | otherwise = isPalindromeHelper $ init $ tail str 

-- Reference
-- https://stackoverflow.com/questions/47926501/haskell-removing-non-letter-characters-but-ignoring-white-spaces