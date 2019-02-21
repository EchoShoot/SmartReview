from itertools import product
from itertools import groupby

def yield_relate(amount):
	# 模拟生成向量之间的关系
	collection = []
	count = amount  # 向量长度
	for each in product(range(count+1),repeat=4):
		if sum(each) == count:  # 过滤出符合向量长度值
			acc,hit,loss,miss = each
			collection.append([acc,hit,loss,miss])
	# 找规律得出通项 递推公式 A(n) = A(n-1) + (1+n)n/2 数目		
	result = []	
	# 这一步是为了合理排序,将向量按照我们想要的优先级来进行排
	collection = sorted(collection,key=lambda x:x[-1])
	for value,group in groupby(collection,lambda x:x[-1]):
		group = sorted(group,key=lambda x:x[0],reverse=True)
		for value,group in groupby(group,lambda x:x[0]):
			group = sorted(group,key=lambda x:x[1],reverse=True)
			for value,group in groupby(group,lambda x:x[1]):
				group = sorted(group,key=lambda x:x[2],reverse=True)
				for value,group in groupby(group,lambda x:x[2]):
					for value in list(group):
						result.append(value)
	return result

# 以下的方法就是为了求出得分了
def calc_An(n):
	""" 计算 1+2+3...+n 的值 """
	return (1+n)*n/2

def calc_total(n):
	""" 计算递推公式 A(n) = A(n-1) + (1+n)n/2 中 A(n)的值 """
	total = 0
	for i in range(1,n+2):
		total += calc_An(i)
	return total
	
def calc_score(acc,hit,loss,miss):
	""" 计算指定参数所处位置,从而推算出分数 """
	count = acc + hit + loss + miss
	v_miss = calc_total(count-miss)  # 由 miss 的值,得出位置
	v_acc = calc_An(count-miss-acc)  # 由 acc 的值,得出偏移量
	v_hit = count-miss-acc-hit  # 由 hit 的值,得出偏移量
	pos = v_miss-v_acc-v_hit  # 计算位置
	score = (pos-1)/(calc_total(count)-1)  # 位置/计算总共量程 得到 0~1 的分数
	# 都减一是为了由 1~n 转换成 0~(n-1) 进而比例转换到 0~1
	return score
	
def old_scores(result,predict):
	""" 这是以前的旧的打分算法,用来做对比的 """
	loss = 0  # predict:0->result:1 损失的数量, 这是附加分,在主打分上调整分数
	miss = 0  # predict:1->result:0 错误的数量, 这是主打分
	# (错,损)[错数量+损数量<=4] (4错,0损),(3错,0~1损),(2错,0~2损),(1错,0~3损),(0错,0~4损)
	# (0错,0损) 是最高分为1.0 而 (4错,0损) 是最低分为 0.0
	# (2错,2损) 比 (2错,1损) 分数低, (2错,1损) 比 (1错,3损) 分数低
	
	count = len(list(result))  # 错误量+损失量<=总数量
	for p,r in zip(predict,result):
		if p == 0 and r == 1:  # 预测0,实际1 -> 影响不大,大不了就损失!多记一次!
			loss += 1   # 取值范围是  0 <= loss <= count-miss
		if p == 1 and r == 0:  # 预测1,实际0 -> 影响很大,你会错失!最佳复习时间!
			miss += 1   # 取值范围是  0 <= miss <= count-loss
	# 分数从下到上递增,从左到右递增!
	# 0 错   3 2 1 0 损
	# 1 错     2 1 0 损
	# 2 错       1 0 损
	# 3 错         0 损
	# 公式得出位置: (m错,l损) = ((len-m)+1)*(len-m)/2+(len-m-l)
	scores = ((count-miss)+1)*(count-miss)/2+(count-miss-loss)
	total = ((count)+1)*(count)/2+(count)  # 计算总数
	return scores/total  # 计算所处位置所占比例		
	
def new_scores(result,predict):
	""" 这是最新的打分算法 """
	loss = 0  # predict:0->result:1 损失的数量, 影响力 4
	miss = 0  # predict:1->result:0 错误的数量, 影响力 1 (主要影响)
	acc = 0   # predict:0->result:0 正确的数量, 影响力 2
	hit = 0   # predict:1->result:1 节省的数量, 影响力 3
	count = len(list(result))  # 错误量+损失量<=总数量
	for p,r in zip(predict,result):
		if p == 0 and r == 1:  # 预测0,实际1 -> 影响不大,大不了就损失!多记一次!
			loss += 1   # 取值范围是  0 <= loss <= count-miss
		if p == 0 and r == 0:
			acc += 1
		if p == 1 and r == 0:  # 预测1,实际0 -> 影响很大,你会错失!最佳复习时间!
			miss += 1   # 取值范围是  0 <= miss <= count-loss
		if p == 1 and r == 1:
			hit += 1
	return calc_score(acc, hit, loss, miss)	

def yield_predict(amount):
	for acc, hit, loss, miss in yield_relate(amount):
		vector = [(0,0),]*acc + [(1,1),]*hit + [(1,0),]*loss + [(0,1),]*miss
		result,predict = zip(*vector)
		yield result,predict
	

if __name__ == "__main__":
	print('  序号: 旧版评分效果   分数  ')
	for index,value in enumerate(yield_predict(2),start=1):
		result,predict = value
		print("{:4}  {}  {:<4}".format(index,value,old_scores(result, predict)))

	print('  序号: 新版评分效果   分数  ')
	for index,value in enumerate(yield_predict(2),start=1):
		result,predict = value
		print("{:4}  {}  {:<4}".format(index,value,new_scores(result, predict)))		
