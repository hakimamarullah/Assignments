-- Soal 1
lengths :: [a] -> Int
lengths list = foldr (+) 0 (map (\_ -> 1) list)

-- Soal 2
-- Soal 2a map and fold
sumOfSquares1 :: Int -> Int
sumOfSquares1 n = foldr (+) 0 (map (\x -> x*x) [1..n])

sumOfSquares2 :: Int -> Int
sumOfSquares2 n = foldr (+) 0 [x*x | x <- [1..n]]

-- Soal 3
multipleOf5 :: [Int] -> Int
multipleOf5 =  (length . filter (\x -> mod x 5 == 0))

-- Soal 4
total :: (Int -> Int) -> (Int -> Int)
total f n= (sum . map f) [0..n]

-- Soal 5
reverse' :: [a] -> [a]
reverse' xs = foldr (\x g y -> g (x:y)) id xs []

-- Soal 6 penjelasan evaluasi

-- Soal 7
factors :: Int -> [Int]

