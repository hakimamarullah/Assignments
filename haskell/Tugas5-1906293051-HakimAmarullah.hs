qsort [] = []
qsort (x:xs) = qsort small ++ (x: qsort bigger)
   where
      small = [y | y <- xs, y <= x]
      bigger = [y | y <- xs, y > x]

-- Soal 5
-- Improved by manually implementing using seq
-- This implementation is able to avoid stack overflow because seq make helper function get evaluated strictly.
doSum :: Num a => [a] -> a
doSum = helper 0
          where
            helper acc (y:ys) = let acc' = acc + y
                                in seq acc' $ helper acc' ys
            helper acc [] = acc

-- Soal 5 improved
doSum2 :: Num a => [a] -> a
doSum2 = foldr (+) 0