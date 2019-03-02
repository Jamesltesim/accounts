from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, desc

app = Flask(__name__)


jg_appkey = 'efdcf160a6757bfea258c3a3'



# 此处是配置SQLALCHEMY_DATABASE_URI, 前面的mysql+mysqlconnetor指的是数据库的类型以及驱动类型
# 后面的username,pwd,addr,port,dbname分别代表用户名、密码、地址、端口以及库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:12345678@127.0.0.1:3306/Accounts'
# 创建1个SQLAlichemy实例
db = SQLAlchemy(app)


# 定义1个类(由db.Model继承)，注意这个类是数据库真实存在的，因为我是针对已有数据库做转化
# 我的数据库结构见下图 其中role是数据库的一张表名
class Users(db.Model):
    __tablename__ = 'users'
    # id是主键db.Column是字段名， db.INT是数据类型
    id = Column(Integer, primary_key=True,autoincrement=True)
    uuid = Column(db.String(45), unique=True)
    name = Column(db.String(45), unique=False)





class Account(db.Model):
    __tablename__ = 'account'
    # id是主键db.Column是字段名， db.INT是数据类型
    id = db.Column(db.INT, primary_key=True,autoincrement=True)
    type = db.Column(db.INT, unique=True)
    operator = db.Column(db.INT, unique=False)
    remark = db.Column(db.String(45), unique=False)
    money = db.Column(db.FLOAT, unique=False)
    time = db.Column(db.String(45), unique=False,nullable=False)
    status = db.Column(db.INT)


    def __init__(self, type, operator):

        self.type = type
        self.operator = operator

    def to_json(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict



@app.route('/approveAccount', methods=['POST'])
def approveAccount():
    uuid = request.get_json().get('uuid')
    accountid = request.get_json().get('accountid')

    user = db.session.query(Users).filter_by(uuid=uuid).first()
    if user:
        account = db.session.query(Account).filter_by(id=accountid).first()

        if account:
            account.status = 1
            db.session.add(account)
            db.session.commit()
            return jsonify({"status": "200"})
        else:
            # 没有账号
            return jsonify({"status": "210"})
    else:
        # 没有该用户
        return jsonify({"status": "211"})


@app.route('/addAccount', methods=['POST'])
def addAccount():
    type = request.get_json().get('type')
    operator = request.get_json().get('operator')
    remark = request.get_json().get('remark')
    money = request.get_json().get('money')

    test_account = Account(type, operator)
    test_account.remark = remark
    test_account.money = money
    test_account.status = 0

    import datetime, time
    i = datetime.datetime.now()

    timestr = ("%s年%s月%s日 %s时%s分%s秒" % (i.year, i.month, i.day, i.hour, i.minute, i.second))
    test_account.time = timestr
    try:
        db.session.add(test_account)
        db.session.commit()
        return jsonify({"status": "200"})

    except Exception:
        return jsonify({"status":220})

@app.route('/selectAccount', methods=['POST'])
def selectAccount():
    uuid = request.get_json().get('uuid')

    user = db.session.query(Users).filter_by(uuid=uuid).first()
    if user :
        accounts = db.session.query(Account).order_by(desc(Account.id)).all()
        list = []
        for account in accounts:
            # print("序号：%s   值：%s" % (accounts.index(account) + 1, account))
            list.append(account.to_json())
        return jsonify({"status":200,"list":list})
    else:
        return jsonify({"status": 230})


# 初始化role 并插入数据库

# test_role = Users()
# test_role.name = 'name1'
# test_role.uuid = 'dhsja1'
# db.session.add(test_role)
#
# db.session.commit()



# #查询数据库
# db.session.query(users).filter_by(id=2).first()  # 查询role表中id为2的第一个匹配项目，用".字段名"获取字段值
# db.session.query(users).all()  # 得到一个list，返回role表里的所有role实例
# db.session.query(users).filter(users.id == 2).first() # 结果与第一种一致
# # 获取指定字段，返回一个生成器 通过遍历来完成相关操作, 也可以强转为list
# db.session.query(users).filter_by(id=2).values('id', 'name', 'name_cn')
# # 模糊查询
# db.session.query(users).filter(users.name_cn.endswith('管理员')).all()  # 获取role表中name_cn字段以管理员结尾的所有内容
# # 修改数据库内容
# user = db.session.query(users).filter_by(id=6).first()  # 将role表中id为6的name改为change
# user.name = 'change'
# db.session.commit()

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
