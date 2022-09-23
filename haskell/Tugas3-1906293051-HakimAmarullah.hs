{-
Author  : Hakim Amarullah
NPM     : 1906293051
version : 1.0
updated : Fri 23/09/2022

Disclaimer: This code was not originally created by the specified author. Recreated for learning purposes.
-}

import Data.Char
import Data.List
-- Soal 1
curry3 :: ((a, b, c) -> d) -> a -> b -> c -> d
curry3 f a b c = f(a,b,c) 

uncurry3 :: (a -> b -> c -> d) -> (a, b, c) -> d
uncurry3 f = \(a,b,c) -> f a b c

addAllThree x y z = x + y + z
addAllThree' (x, y, z) = x + y + z

-- Soal 2
partialOnFirst :: a -> ((a, b) -> c) -> (b -> c)
partialOnFirst a f= \b -> f(a, b)

partialOnSecond :: b -> ((a, b) -> c) -> (a -> c)
partialOnSecond b f= \a -> f(a, b)

-- -- Soal 3
toTitles :: String -> String
toTitles str = zipWith upper (' ':str) str
   where
    upper a b | isSpace a && isLower b = toUpper b
              | otherwise = b
-- Soal 4
evenAverage :: (Integral a, Fractional b) => [a] -> Maybe b
evenAverage [] = Nothing
evenAverage l = evenAvr [x | x <- l, x `mod` 2 == 0]
            where
               evenAvr l
                       | genericLength l /= 0 = Just $ fromIntegral (sum l) / genericLength l
                       | otherwise            = Nothing

-- Soal 5
zipWith3s :: (a -> b -> c -> d) -> [a] -> [b] -> [c] -> [d]
zipWith3s f = zipW3 
       where
         zipW3 (a:as) (b:bs) (c:cs) = f a b c : zipW3 as bs cs
         zipW3 _ _ _                = []