# -*- coding: utf-8 -*-
# @Time    : 2018/10/24 18:28
# @Author  : daixiaohan
# @Email   : jasonxiaohan198@qq.com
# @File    : ItemCF.py
# @Software: PyCharm
# 基于项目的协同过滤推荐算法实现

import random

import math
from operator import itemgetter

class ItemBasedCF():
    # 初始化参数
    def __init__(self):
        # 找到相似的20部电影，为目标用户推荐10部电影
        self.n_sim_movie = 20
        self.n_rec_moive = 10

        # 将数据集划分为训练集和测试集
        self.trainSet = {}
        self.testSet = {}

        # 用户相似度矩阵
        self.movie_sim_matrix = {}
        self.movie_popular = {}
        self.movie_count = 0

        print('Similar movie number = %d' % self.n_sim_movie)
        print('Recommneded moive number = %d' % self.n_rec_moive)

    #  读取得到“用户-电影”数据
    def get_dataset(self,filename,pivot=0.75):
        trainSet_len = 0
        testSet_len = 0
        for line in self.load_file(filename):
            user,movie,rating,timestamp = line.split(',')
            if random.random() < pivot:
                self.trainSet.setdefault(user, {})
                self.trainSet[user][movie] = rating
                trainSet_len += 1
            else:
                self.testSet.setdefault(user, {})
                self.testSet[user][movie] = rating
                testSet_len += 1
        print('Split trainingSet and testSet success!')
        print('TrainSet = %s ' % trainSet_len)
        print('TestSet = %s' % testSet_len)

    #  读取电影数据
    def get_movieset(self, filename):
        movie_set = {}
        for line in self.load_file(filename):
            movie = line.split(',')
            movieid = 0
            title = ""
            genres = ""
            if len(movie) == 3:
                movieid = movie[0]
                title = movie[1]
                genres = movie[2]
            elif len(movie) == 4:
                movieid = movie[0]
                title = movie[1] + "," + movie[2]
                genres = movie[3]
            movie_set.setdefault(movieid, {})
            movie_set[movieid] = {"title": title, "genres": genres}
        return movie_set

    # 读文件，返回文件的每一行
    def load_file(self, filename):
        with open(filename, 'r', encoding='UTF-8') as f:
            for i, line in enumerate(f):
                if i == 0: # 去掉文件第一行
                    continue
                yield line.strip('\r\n')

    # 计算电影之间的相似度
    def calc_moive_sim(self):
        for user,movies in self.trainSet.items():
            for movie in movies:
                if movie not in self.movie_popular:
                    self.movie_popular[movie] = 0
                self.movie_popular[movie] += 1
        self.movie_count = len(self.movie_popular)
        print('Total movie number = %d'%self.movie_count)

        for user,movies in self.trainSet.items():
            for m1 in movies:
                for m2 in movies:
                    if m1 == m2:
                        continue
                    self.movie_sim_matrix.setdefault(m1, {})
                    self.movie_sim_matrix[m1].setdefault(m2, 0)
                    self.movie_sim_matrix[m1][m2] += 1
        print('Build co-rated users matrix success!')

        # 计算电影之间的相似性
        print('Calculating movie similarity matrix....')
        for m1,related_movies in self.movie_sim_matrix.items():
            for m2,count in related_movies.items():
                # 注意0向量的处理，即某电影的用户数0
                if self.movie_popular[m1] == 0 or self.movie_popular[m2] == 0:
                    self.movie_sim_matrix[m1][m2] = 0
                else:
                    self.movie_sim_matrix[m1][m2] = count / math.sqrt(self.movie_popular[m1] * self.movie_popular[m2])
        print('Calculate movie similarity matrix success!')

    #  针对目标用户U，找到K部相似的电影，并推荐其N部电影
    def recommend(self, user):
        K = self.n_sim_movie
        N = self.n_rec_moive
        rank = {}
        watched_movies = self.trainSet[user]

        for movie,rating in watched_movies.items():
            for related_movie,w in sorted(self.movie_sim_matrix[movie].items(),key=itemgetter(1),reverse=True)[:K]:
                if related_movie in watched_movies:
                    continue
                rank.setdefault(related_movie, 0)
                rank[related_movie] += w * float(rating)
        return sorted(rank.items(),key=itemgetter(1),reverse=True)[:N]

    #  产生推荐并通过准确率、召回率和覆盖率进行评估
    def evaluate(self):
        print('Evaluating start....')
        N = self.n_rec_moive
        # 准确率和召回率
        hit = 0
        rec_count = 0
        test_count = 0
        # 覆盖率
        all_rec_movies = set()
        for i,user in enumerate(self.trainSet):
            test_movies = self.testSet.get(user, {})
            rec_movies = self.recommend(user)
            for movie,w in rec_movies:
                if movie in test_movies:
                    hit += 1
                all_rec_movies.add(movie)
                rec_count += N
                test_count += len(test_movies)
        # 准确率
        precision = hit / (1.0 * rec_count)
        recall =  hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)
        print('precision= %.4f\trecall=%.4f\tcoverage=%.4f'%(precision, recall, coverage))

if __name__ == '__main__':
    rating_file = '../movies/ml-latest-small/ratings.csv'
    movie_file = '../movies/ml-latest-small/movies.csv'
    itemCF = ItemBasedCF()
    movie_dataset = itemCF.get_movieset(movie_file)
    itemCF.get_dataset(rating_file)
    itemCF.calc_moive_sim()
    itemCF.evaluate()
    user_id = input('您要向哪位用户进行推荐？请输入用户编号:')
    sortedResult = itemCF.recommend(user_id)
    for movieid, score in sortedResult:
        print("评分：%.2f，电影名称：%s" % (score, movie_dataset[str(movieid)]['title']))
