# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, text
from sqlalchemy.dialects.mysql import LONGTEXT, TEXT, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class DataAdd(Base):
    __tablename__ = 'data_add'

    id = Column(BigInteger, primary_key=True, comment='事件id')
    task_id = Column(BigInteger, comment='任务id')
    plan_id = Column(BigInteger, comment='方案id')
    event_id = Column(BigInteger, comment='事件id\\r\\n事件id')
    newsId = Column(BigInteger, comment='新闻id')
    postId = Column(BigInteger, comment='贴文id')


class DataEvent(Base):
    __tablename__ = 'data_event'

    id = Column(BigInteger, primary_key=True, comment='事件id')
    plan_id = Column(BigInteger, comment='方案id')
    title = Column(TEXT, comment='事件标题')
    introduce = Column(TEXT, comment='事件摘要，这里最好可以将关键词进行高亮显示，加入<em></em>标签')
    newsIds = Column(LONGTEXT, comment='所包含的新闻idList')
    postIds = Column(LONGTEXT, comment='所包含的贴文idList')
    is_add = Column(TINYINT, comment='是否流转进入业务数据库')
    summary = Column(TEXT, comment='AI总结')
    style = Column(VARCHAR(255), comment='事件类型，ai生成')
    prediction = Column(TEXT, comment='发展预测')
    create_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class DataNew(Base):
    __tablename__ = 'data_news'

    id = Column(BigInteger, primary_key=True)
    create_date = Column(DateTime)
    del_flag = Column(TINYINT, comment='0：未删除    1：删除')
    title = Column(TEXT, comment='标题')
    original_title = Column(TEXT)
    original_content = Column(TEXT, comment='原始内容')
    release_time = Column(DateTime, comment='发布时间')
    screenshot = Column(TEXT, comment='截图')
    view_num = Column(VARCHAR(255), comment='浏览数')
    web_url = Column(TEXT, comment='网址url')
    author = Column(VARCHAR(255), comment='作者')
    platform = Column(VARCHAR(255), comment='平台')
    add_time = Column(DateTime, comment='添加时间')
    content = Column(TEXT, comment='请将内容翻译完后写如此字段')
    is_translated = Column(TINYINT, comment='翻译完后将此字段设为1  初始为0')
    emotion = Column(Integer, comment='情感 0正面 1负面 2中立')
    is_emotional_analysed = Column(TINYINT, comment='是否进行过情感分析 初始为0 情感分析后请置1')
    is_es_add = Column(TINYINT, server_default=text("'0'"), comment='是否上传到es')
    images = Column(TEXT)
    screenshot_origin = Column(TEXT)
    images_origin = Column(TEXT)


class DataPerson(Base):
    __tablename__ = 'data_person'

    id = Column(BigInteger, primary_key=True)
    create_date = Column(DateTime)
    del_flag = Column(TINYINT, comment='0：未删除    1：删除')
    uid = Column(VARCHAR(255), comment='人员id')
    avatar = Column(VARCHAR(255), comment='头像')
    name = Column(VARCHAR(255), comment='姓名')
    fan_num = Column(VARCHAR(255), comment='粉丝数')
    add_time = Column(DateTime, comment='添加时间')
    platform = Column(VARCHAR(255), comment='平台')


class DataSimilar(Base):
    __tablename__ = 'data_similar'

    id = Column(BigInteger, primary_key=True)
    plan_id = Column(BigInteger)
    news_ids = Column(TEXT, comment='相似的新闻数组')
    event_id = Column(BigInteger, comment='所属事件id')


class DataSocialComment(Base):
    __tablename__ = 'data_social_comment'

    id = Column(BigInteger, primary_key=True)
    create_date = Column(DateTime)
    del_flag = Column(TINYINT, comment='0：未删除    1：删除')
    uid = Column(VARCHAR(255), comment='人员id')
    post_id = Column(TEXT, comment='帖子id')
    comment_Uid = Column(VARCHAR(255), comment='评论人id')
    comment_Name = Column(VARCHAR(255), comment='评论人名')
    comment_Avatar = Column(TEXT, comment='评论人头像')
    comment_content = Column(TEXT, comment='翻译后的评论内容  请将内容翻译完后写如此字段')
    comment_Original_Content = Column(TEXT, comment='原始评论内容')
    is_Translated = Column(TINYINT, server_default=text("'0'"), comment='是否翻译，翻译完请将此列置为1')
    comment_Time = Column(DateTime, comment='评论时间')
    add_Time = Column(DateTime, comment='添加时间')
    platform = Column(VARCHAR(255), comment='平台')
    comment_Avatar_origin = Column(TEXT)


class DataSocialPost(Base):
    __tablename__ = 'data_social_post'

    id = Column(BigInteger, primary_key=True)
    create_Date = Column(DateTime)
    del_Flag = Column(TINYINT, comment='0：未删除    1：删除')
    uid = Column(VARCHAR(255), comment='人员id')
    title = Column(TEXT, comment='标题')
    original_title = Column(TEXT)
    content = Column(TEXT, comment='翻译后的内容')
    original_Content = Column(TEXT, comment='原始内容英文')
    is_Translated = Column(TINYINT, comment='是否进行翻译过，是1，否0')
    url = Column(VARCHAR(255), comment='url')
    view_Num = Column(BigInteger, comment='浏览数')
    reply_Num = Column(BigInteger, comment='回复数')
    forward_Num = Column(BigInteger, comment='转发数')
    like_Num = Column(BigInteger, comment='点赞数')
    post_Time = Column(DateTime, comment='发帖时间')
    screenshot = Column(VARCHAR(255), comment='截图')
    add_Time = Column(DateTime, comment='添加时间')
    platform = Column(VARCHAR(255), comment='平台')
    emotion = Column(Integer, comment='0：正面 1：负面 2：中立 ')
    is_Emotional_Analysed = Column(TINYINT, comment='是否进行过情感分析 是1 否0')
    is_es_add = Column(TINYINT)
    images = Column(TEXT)
    post_id = Column(VARCHAR(255))
    screenshot_origin = Column(VARCHAR(255))


class DataTask(Base):
    __tablename__ = 'data_task'

    id = Column(BigInteger, primary_key=True)
    plan_id = Column(BigInteger)
    news_id_list = Column(LONGTEXT, comment='List<newsId>')
    post_id_list = Column(LONGTEXT, comment='List<postId>')
    status = Column(Integer, comment='0未完成 1模型已完成待接收 2接收完毕')
    create_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    keywords = Column(VARCHAR(255), comment='检索关键词')
    update_date = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='修改时间')
