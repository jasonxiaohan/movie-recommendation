# -*- coding: utf-8 -*-
# @Time    : 2018/10/24 12:36
# @Author  : daixiaohan
# @Email   : jasonxiaohan198@qq.com
# @File    : UserCF.py
# @Software: PyCharm
# 基于用户的协同过滤推荐算法实现

import random

import math
from operator import itemgetter

class UserBasedCF():
    # 初始化相关参数
    def __init__(self):
        # 找到与目标用户兴趣相似的20个用户，为其推荐10部电影
        self.n_sim_user = 20
        self.n_rec_movie = 10

        # 将数据集划分为训练集和测试集
        self.trainSet = {}
        self.testSet = {}

        # 用户相似度矩阵
        self.user_sim_matrix = {}
        self.movie_count = 0

        print('Similar user num =%d'% self.n_sim_user)
        print('Recommended movie number = %d'%self.n_rec_movie)

    # 读文件得到“用户-电影”数据
    def get_dateaset(self, filename, pivot=0.75):
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
        print('TrainSet = %s'%trainSet_len)
        print('TestSet = %s'%testSet_len)

    #  读取电影数据
    def get_movieset(self,filename):
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
                title = movie[1]+","+movie[2]
                genres = movie[3]
            movie_set.setdefault(movieid, {})
            movie_set[movieid] = {"title":title, "genres":genres}
        return movie_set

    # 读文件，返回文件的每一行
    def load_file(self, filename):
        with open(filename, 'r', encoding='UTF-8') as f:
            for i,line in enumerate(f):
                if i == 0: # 去掉文件第一行的title
                    continue
                yield line.strip('\r\n')
        print('Load % s success!'%filename)

    #  计算用户之间的相似度
    def calc_user_sim(self):
        # 构建“电影-用户”倒排索引
        # key = movieID, value = list of userIDs who have seen this movie
        print('Building movie-user table....')
        movie_user = {}
        for user,movies in self.trainSet.items():
            for movie in movies:
                if movie not in movie_user:
                    movie_user[movie] = set()
                movie_user[movie].add(user)
            print('Build movie-user table success!')
        self.movie_count = len(movie_user)
        print('Total movie number = %d'%self.movie_count)

        print('Build user co-rated movies matrix.....')
        for moive,users in movie_user.items():
            for u in users:
                for v in users:
                    if u == v:
                        continue
                    self.user_sim_matrix.setdefault(u, {})
                    self.user_sim_matrix[u].setdefault(v, 0)
                    self.user_sim_matrix[u][v] += 1
        print('Build user co-rated movies matrix success!')

        # 计算相似性，余弦相似度计算
        print('Calculatin user similarity marix...')
        for u, related_users in self.user_sim_matrix.items():
            for v,count in related_users.items():
                self.user_sim_matrix[u][v] = count / math.sqrt(len(self.trainSet[u]) * len(self.trainSet[v]))
        print('Calculate user similarity matrix success!')

    #  针对目标用户u，找到其最相似的k个用户，产生N个推荐
    def recommend(self, user):
        k = self.n_sim_user
        N = self.n_rec_movie
        rank = {}
        watched_movies = self.trainSet[user]

        # v=similar user, wuv=similar factor
        for v,wuv in sorted(self.user_sim_matrix[user].items(), key=itemgetter(1),reverse=True)[0:k]:
            for movie in self.trainSet[v]:
                if movie in watched_movies:
                    continue
                rank.setdefault(movie, 0)
                rank[movie]+=wuv
        return sorted(rank.items(),key=itemgetter(1),reverse=True)[0:N]

    # 产生推荐并通过准确率、召回率和覆盖率进行评估
    def evaluate(self):
        print('Evaluation start....')
        N = self.n_rec_movie
        # 准确率和召回率
        hit = 0
        rec_count = 0
        test_count = 0
        # 覆盖率
        all_rec_movies = set()

        for i,user in enumerate(self.trainSet):
            test_moives = self.testSet.get(user, {})
            rec_moives = self.recommend(user)

            for movie,w in rec_moives:
                if movie in  test_moives:
                    hit += 1
                all_rec_movies.add(movie)
            rec_count += N
            test_count += len(test_moives)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)
        print('precision=%.4f\trecall=%.4f\tcoverate=%.4f' % (precision, recall, coverage))

if __name__ == '__main__':
    rating_file = '../movies/ml-latest-small/ratings.csv'
    movie_file = '../movies/ml-latest-small/movies.csv'
    userCF = UserBasedCF()
    movie_dataset = userCF.get_movieset(movie_file)
    userCF.get_dateaset(rating_file)
    userCF.calc_user_sim()
    userCF.evaluate()
    user_id = input('您要向哪位用户进行推荐？请输入用户编号:')
    sortedResult = userCF.recommend(user_id)
    for movieid,score in sortedResult:
        print("评分：%.2f，电影名称：%s" % (score, movie_dataset[str(movieid)]['title']))

