import os
import pickle
import contextlib
import heapq
import time
import nltk

from index import InvertedIndexReader, InvertedIndexWriter
from util import IdMap, sorted_intersect
from compression import StandardPostings, VBEPostings
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from tqdm import tqdm
"""
SOURCE:
https://ristek.link/sourcecodebsbi

"""
class BSBIIndex:
    """
    Attributes
    ----------
    term_id_map(IdMap): Untuk mapping terms ke termIDs
    doc_id_map(IdMap): Untuk mapping relative paths dari dokumen (misal,
                    /collection/0/gamma.txt) to docIDs
    data_dir(str): Path ke data
    output_dir(str): Path ke output index files
    postings_encoding: Lihat di compression.py, kandidatnya adalah StandardPostings,
                    VBEPostings, dsb.
    index_name(str): Nama dari file yang berisi inverted index
    """
    def __init__(self, data_dir, output_dir, postings_encoding, index_name = "main_index"):
        self.term_id_map = IdMap()
        self.doc_id_map = IdMap()
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.index_name = index_name
        self.postings_encoding = postings_encoding

        # Untuk menyimpan nama-nama file dari semua intermediate inverted index
        self.intermediate_indices = []

    def save(self):
        """Menyimpan doc_id_map and term_id_map ke output directory via pickle"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'wb') as f:
            pickle.dump(self.term_id_map, f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'wb') as f:
            pickle.dump(self.doc_id_map, f)

    def load(self):
        """Memuat doc_id_map and term_id_map dari output directory"""

        with open(os.path.join(self.output_dir, 'terms.dict'), 'rb') as f:
            self.term_id_map = pickle.load(f)
        with open(os.path.join(self.output_dir, 'docs.dict'), 'rb') as f:
            self.doc_id_map = pickle.load(f)

    def parse_block(self, block_dir_relative):
        """
        Lakukan parsing terhadap text file sehingga menjadi sequence of
        <termID, docID> pairs.

        Gunakan tools available untuk Stemming Bahasa Indonesia Seperti
        PySastrawi:  https://github.com/har07/PySastrawi

        JANGAN LUPA BUANG STOPWORDS! di PySastrawi juga ada daftar Indonesian
        stopwords.

        Untuk "sentence segmentation" dan "tokenization", bisa menggunakan
        regex atau boleh juga menggunakan tools lain yang berbasis machine
        learning.

        Parameters
        ----------
        block_dir_relative : str
            Relative Path ke directory yang mengandung text files untuk sebuah block.

            CATAT bahwa satu folder di collection dianggap merepresentasikan satu block.
            Konsep block di soal tugas ini berbeda dengan konsep block yang terkait
            dengan operating systems.

        Returns
        -------
        List[Tuple[Int, Int]]
            Returns all the td_pairs extracted from the block
            Mengembalikan semua pasangan <termID, docID> dari sebuah block (dalam hal
            ini sebuah sub-direktori di dalam folder collection)

        Harus menggunakan self.term_id_map dan self.doc_id_map untuk mendapatkan
        termIDs dan docIDs. Dua variable ini harus persis untuk semua pemanggilan
        parse_block(...).
        """
        stemmer = StemmerFactory().create_stemmer()
        stop_word_remover = StopWordRemoverFactory().create_stop_word_remover()

        td_pairs = []
        dir_path = os.path.join(self.data_dir, block_dir_relative)

        for doc_name in os.listdir(dir_path):
            with open(os.path.join(dir_path, doc_name), 'r') as f:
                for line in f.readlines():
                    tokenize = nltk.word_tokenize(line)
                    stemmed = stemmer.stem(" ".join(tokenize))
                    stop_word_cleanup = stop_word_remover.remove(stemmed)
                    for token in stop_word_cleanup:
                        term_id = self.term_id_map[token]
                        doc_id = self.doc_id_map[os.path.join(block_dir_relative, doc_name)]
                        td_pairs.append((term_id, doc_id))
        return td_pairs

    def invert_write(self, td_pairs, index):
        """
        Melakukan inversion td_pairs (list of <termID, docID> pairs) dan
        menyimpan mereka ke index. Disini diterapkan konsep BSBI dimana 
        hanya di-mantain satu dictionary besar untuk keseluruhan block.
        Namun dalam teknik penyimpanannya digunakan srategi dari SPIMI
        yaitu penggunaan struktur data hashtable (dalam Python bisa
        berupa Dictionary)

        ASUMSI: td_pairs CUKUP di memori

        Parameters
        ----------
        td_pairs: List[Tuple[Int, Int]]
            List of termID-docID pairs
        index: InvertedIndexWriter
            Inverted index pada disk (file) yang terkait dengan suatu "block"
        """
        term_dict = {}
        for term_id, doc_id in td_pairs:
            if term_id not in term_dict:
                term_dict[term_id] = set()
            term_dict[term_id].add(doc_id)
        for term_id in sorted(term_dict.keys()):
            index.append(term_id, sorted(list(term_dict[term_id])))

    def merge(self, indices, merged_index):
        """
        Lakukan merging ke semua intermediate inverted indices menjadi
        sebuah single index.

        Ini adalah bagian yang melakukan EXTERNAL MERGE SORT

        Parameters
        ----------
        indices: List[InvertedIndexReader]
            A list of intermediate InvertedIndexReader objects, masing-masing
            merepresentasikan sebuah intermediate inveted index yang iterable
            di sebuah block.

        merged_index: InvertedIndexWriter
            Instance InvertedIndexWriter object yang merupakan hasil merging dari
            semua intermediate InvertedIndexWriter objects.
        """
        last_term = ''
        last_postings = []

        for term_id, postings in heapq.merge(*indices, key = lambda x: self.term_id_map[x[0]]):
            if term_id != last_term:
                if last_term != '':
                    merged_index.append(last_term, last_postings)
                last_term = term_id
                last_postings = postings
            else:
                i, j = 0, 0
                new_postings = []
                while i<len(postings) and j<len(last_postings):
                    if postings[i]<last_postings[j]:
                        new_postings.append(postings[i])
                        i += 1
                    elif postings[i]>last_postings[j]:
                        new_postings.append(last_postings[j])
                        j += 1
                    else:
                        new_postings.append(postings[i])
                        i += 1
                        j += 1
                if i < len(postings):
                    new_postings.extend(postings[i:len(postings)])
                elif j < len(last_postings):
                    new_postings.extend(postings[j:len(last_postings)])
                last_postings = new_postings
                del new_postings
        if last_term:
            merged_index.append(last_term, last_postings)

    def retrieve(self, query):
        """
        Melakukan boolean retrieval untuk mengambil semua dokumen yang
        mengandung semua kata pada query. Jangan lupa lakukan pre-processing
        yang sama dengan yang dilakukan pada proses indexing!
        (Stemming dan Stopwords Removal)

        Parameters
        ----------
        query: str
            Query tokens yang dipisahkan oleh spasi

            contoh: Query "universitas indonesia depok" artinya adalah
                    boolean query "universitas AND indonesia AND depok"

        Result
        ------
        List[str]
            Daftar dokumen terurut yang mengandung sebuah query tokens.
            Harus mengembalikan EMPTY LIST [] jika tidak ada yang match.

        JANGAN LEMPAR ERROR/EXCEPTION untuk terms yang TIDAK ADA di collection.
        """
        tokenize = nltk.word_tokenize(query)
        stemmed = StemmerFactory().create_stemmer().stem(" ".join(tokenize))
        stop_word_cleanup = StopWordRemoverFactory().create_stop_word_remover().remove(stemmed)
        

        if len(self.term_id_map) == 0 or len(self.doc_id_map) == 0:
            self.load()

        query_list = stop_word_cleanup
        heap = []
        with InvertedIndexReader(self.index_name, directory=self.output_dir, postings_encoding=
                                 self.postings_encoding) as mapper:
            for token in query_list:
                postings = mapper[self.term_id_map[token]]
                heapq.heappush(heap, (len(postings),postings))
            while len(heap)>1:
                list1 = heapq.heappop(heap)[1]
                list2 = heapq.heappop(heap)[1]
                tmp = sorted_intersect(list1, list2)
                heapq.heappush(heap, (len(tmp), tmp))
        result = [self.doc_id_map[doc_id] for doc_id in heap[0][1]]
        print(len(result))
        return result


    def index(self):
        """
        Base indexing code
        BAGIAN UTAMA untuk melakukan Indexing dengan skema BSBI (blocked-sort
        based indexing)

        Method ini scan terhadap semua data di collection, memanggil parse_block
        untuk parsing dokumen dan memanggil invert_write yang melakukan inversion
        di setiap block dan menyimpannya ke index yang baru.
        """
        # loop untuk setiap sub-directory di dalam folder collection (setiap block)
        for block_dir_relative in tqdm(sorted(next(os.walk(self.data_dir))[1])):
            td_pairs = self.parse_block(block_dir_relative)
            index_id = 'intermediate_index_'+block_dir_relative
            self.intermediate_indices.append(index_id)
            with InvertedIndexWriter(index_id, self.postings_encoding, directory = self.output_dir) as index:
                self.invert_write(td_pairs, index)
                td_pairs = None
    
        self.save()

        with InvertedIndexWriter(self.index_name, self.postings_encoding, directory = self.output_dir) as merged_index:
            with contextlib.ExitStack() as stack:
                indices = [stack.enter_context(InvertedIndexReader(index_id, self.postings_encoding, directory=self.output_dir))
                               for index_id in self.intermediate_indices]
                self.merge(indices, merged_index)


if __name__ == "__main__":

    BSBI_instance = BSBIIndex(data_dir = 'collection', \
                              postings_encoding = VBEPostings, \
                              output_dir = 'index')
    BSBI_instance.index() # memulai indexing!
