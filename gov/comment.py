class Comment(object):
    # 初始化中给对象属性赋值
    def __init__(self, userName , content, hotNum, place):
        self.userName = userName
        self.content = content
        self.hotNum = hotNum
        self.place = place
