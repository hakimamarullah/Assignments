import re
from typing import final
from bsbi import BSBIIndex
from compression import VBEPostings
import math

######## >>>>> 3 IR metrics: RBP p = 0.8, DCG, dan AP
class Constant:
  TFIDF = 'TF-IDF'
  OKAPIBM25 = 'OKAPIBM25'

def rbp(ranking, p = 0.8):
  """ menghitung search effectiveness metric score dengan 
      Rank Biased Precision (RBP)

      Parameters
      ----------
      ranking: List[int]
         vektor biner seperti [1, 0, 1, 1, 1, 0]
         gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
         Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                 di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                 di rank-6 tidak relevan
        
      Returns
      -------
      Float
        score RBP
  """
  score = 0.
  for i in range(1, len(ranking) + 1):
    pos = i - 1
    score += ranking[pos] * (p ** (i - 1))
  return (1 - p) * score

def dcg(ranking):
  """ menghitung search effectiveness metric score dengan 
      Discounted Cumulative Gain

      Parameters
      ----------
      ranking: List[int]
         vektor biner seperti [1, 0, 1, 1, 1, 0]
         gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
         Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                 di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                 di rank-6 tidak relevan
        
      Returns
      -------
      Float
        score DCG
  """
  scores = 0.
  for i in range(1, len(ranking) + 1):
    pos = i - 1
    scores += ranking[pos] / math.log2(pos + 2)
  return scores

def precision(ranking):
  return sum(ranking) / len(ranking)

def ap(ranking):
  """ menghitung search effectiveness metric score dengan 
      Average Precision

      Parameters
      ----------
      ranking: List[int]
         vektor biner seperti [1, 0, 1, 1, 1, 0]
         gold standard relevansi dari dokumen di rank 1, 2, 3, dst.
         Contoh: [1, 0, 1, 1, 1, 0] berarti dokumen di rank-1 relevan,
                 di rank-2 tidak relevan, di rank-3,4,5 relevan, dan
                 di rank-6 tidak relevan
        
      Returns
      -------
      Float
        score AP
  """
  scores = 0.
  R = sum(ranking)
  for i in range(1, len(ranking) + 1):
    pos = i - 1
    scores += (precision(ranking[:i])) * ranking[pos]
  return scores / R

######## >>>>> memuat qrels

def load_qrels(qrel_file = "qrels.txt", max_q_id = 30, max_doc_id = 1033):
  """ memuat query relevance judgment (qrels) 
      dalam format dictionary of dictionary
      qrels[query id][document id]

      dimana, misal, qrels["Q3"][12] = 1 artinya Doc 12
      relevan dengan Q3; dan qrels["Q3"][10] = 0 artinya
      Doc 10 tidak relevan dengan Q3.

  """
  qrels = {"Q" + str(i) : {i:0 for i in range(1, max_doc_id + 1)} \
                 for i in range(1, max_q_id + 1)}
  with open(qrel_file) as file:
    for line in file:
      parts = line.strip().split()
      qid = parts[0]
      did = int(parts[1])
      qrels[qid][did] = 1
  return qrels

######## >>>>> EVALUASI !

def eval(qrels, query_file = "queries.txt",k1=1.6, b=0.75, scoring= Constant.TFIDF, k = 1000):
  """ 
    loop ke semua 30 query, hitung score di setiap query,
    lalu hitung MEAN SCORE over those 30 queries.
    untuk setiap query, kembalikan top-1000 documents
  """
  BSBI_instance = BSBIIndex(data_dir = 'collection', \
                          postings_encoding = VBEPostings, \
                          output_dir = 'index')

  with open(query_file) as file:
    rbp_scores = []
    dcg_scores = []
    ap_scores = []
    for qline in file:
      parts = qline.strip().split()
      qid = parts[0]
      query = " ".join(parts[1:])

      # HATI-HATI, doc id saat indexing bisa jadi berbeda dengan doc id
      # yang tertera di qrels
      ranking = []
      try:
        if scoring == Constant.TFIDF:
          for (score, doc) in BSBI_instance.retrieve_tfidf(query, k = k):
              did = int(re.search(r'\/.*\/.*\/(.*)\.txt', doc).group(1))
              ranking.append(qrels[qid][did])
        elif scoring == Constant.OKAPIBM25:
          for (score, doc) in BSBI_instance.retrieve_okapibm25(query, k1= k1, b=b, k = k):
              did = int(re.search(r'\/.*\/.*\/(.*)\.txt', doc).group(1))
              ranking.append(qrels[qid][did])
      except KeyError:
        continue
      rbp_scores.append(rbp(ranking))
      dcg_scores.append(dcg(ranking))
      ap_scores.append(ap(ranking))

  print(f'Hasil evaluasi {scoring} terhadap 30 queries')
  if scoring == Constant.OKAPIBM25:  print(f'k1= {k1}; b={b}')
  print("RBP score =", round(sum(rbp_scores) / len(rbp_scores),4))
  print("DCG score =", round(sum(dcg_scores) / len(dcg_scores),4))
  print("AP score  =", round(sum(ap_scores) / len(ap_scores),4))
  print()
  print("="*45)
  print()

if __name__ == '__main__':
  qrels = load_qrels()

  assert qrels["Q1"][166] == 1, "qrels salah"
  assert qrels["Q1"][300] == 0, "qrels salah"

  eval(qrels, scoring=Constant.TFIDF)
  eval(qrels, k1=1.3, scoring=Constant.OKAPIBM25)
  eval(qrels, k1=1.5, scoring=Constant.OKAPIBM25)
  eval(qrels, k1=1.7, scoring=Constant.OKAPIBM25)
  eval(qrels, k1=1.8, scoring=Constant.OKAPIBM25)
  eval(qrels, k1=2, scoring=Constant.OKAPIBM25)
  eval(qrels, k1=1.3, b=0.5, scoring=Constant.OKAPIBM25)
  eval(qrels, k1=1.5, b=0.5, scoring=Constant.OKAPIBM25)
  eval(qrels, k1=1.7, b=0.5, scoring=Constant.OKAPIBM25)
  eval(qrels, k1=1.8, b=0.5, scoring=Constant.OKAPIBM25)
  eval(qrels, k1=2, b=0.5, scoring=Constant.OKAPIBM25)