{-
Author  : Hakim Amarullah
NPM     : 1906293051
version : 1.0
updated : Thu 09/08/2022

Disclaimer: This code was not originally created by the specified author. Recreated for learning purposes.
-}


--Soal 1 Area of Circle
circleA :: Double -> Double
circleA r = 3.14 * r^2

--Soal 2 isTriangle
isTriangle :: Int -> Int -> Int -> Bool
isTriangle  a b c
            | (a + b > c) && (a + c > b) && (b + c > a) = True
            | otherwise = False

--Soal 3 list summation
listSum :: Num a => [a] -> a
listSum [] = 0
listSum (x:xs) = x + listSum xs

--Soal 4 sum of list of circle area
listSumArea :: [Double] -> Double
listSumArea [] = 0
listSumArea (x:xs) = x + listSumArea xs

--Soal 5 reverse list
reverseList :: [a] -> [a]
reverseList l = rev l []
       where
        rev []     a = a
        rev (x:xs) a = rev xs (x:a)

--Soal 6 quicksort descending
quicksort :: (Ord a) => [a] -> [a]
quicksort [] = []
quicksort (x:xs) =
    let 
     biggerSorted = quicksort [a | a <- xs, a > x]
     smallerSorted = quicksort [a | a <- xs, a <= x]
    in
     biggerSorted ++ [x] ++ smallerSorted
