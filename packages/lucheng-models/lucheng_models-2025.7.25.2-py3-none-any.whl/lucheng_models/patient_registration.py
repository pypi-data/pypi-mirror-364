from sqlalchemy import create_engine, Column, String, Float, DateTime, func, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import BIGINT
from dateutil.parser import parse

Base = declarative_base()


class PatientRegistration(Base):
    __tablename__ = 'patient_registration'

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True, comment='主键ID')
    name = Column(String(50), nullable=False, comment='姓名')
    gender = Column(String(10), nullable=False, comment='性别')
    身份证号 = Column(String(18), nullable=False, comment='身份证号')
    address = Column(String(200), nullable=False, comment='地址')
    phone = Column(String(20), nullable=False, comment='电话')
    diagnosis = Column(String(500), comment='诊断信息')
    fee_type = Column(String(20), nullable=False, comment='费别')
    serial_number = Column(String(50), nullable=False, comment='门诊序号')
    medical_insurance_number = Column(String(50), comment='医保号')
    department = Column(String(50), nullable=False, comment='科室')
    registration_doctor = Column(String(50), server_default='未选择', comment='挂号医生')
    registration_type = Column(String(20), nullable=False, comment='挂号类型')
    registration_time = Column(DateTime, nullable=False, comment='挂号时间')
    consultation_fee = Column(Float, nullable=False, server_default='0.0', comment='诊疗费')
    registration_fee = Column(Float, nullable=False, server_default='0.0', comment='挂号费')
    fund = Column(Float, comment='基金')
    cash = Column(Float, nullable=False, comment='现金')
    诊疗医生 = Column(String(50), nullable=False, comment='诊疗医生')
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment='创建时间')

    # 新增字段 (使用中文列名)
    是否本机构建档 = Column(Enum('是', '否'), comment='是否在本机构建立健康档案')
    是否外机构建档 = Column(Enum('是', '否'), comment='是否在外机构建立健康档案')
    建档日期 = Column(DateTime, comment='健康档案创建时间')
    是否本机构签约 = Column(Enum('是', '否'), comment='是否与本机构签约')
    是否外机构签约 = Column(Enum('是', '否'), comment='是否与外机构签约')
    签约日期 = Column(Date, comment='本次签约日期')
    首次签约日期 = Column(Date, comment='首次签约日期')
    团队名称 = Column(String(100), comment='家庭医生团队名称')
    签约医生姓名 = Column(String(50), comment='签约医生姓名')
    签约来源 = Column(String(100), comment='签约来源渠道')
    就诊日期 = Column(Date, comment='就诊日期')
    institution_name = Column(String(100), comment='机构名称')

    __table_args__ = (
        {'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8mb4',
         'mysql_row_format': 'DYNAMIC'},
    )


def save_or_update_patient_record(data: dict, result: dict, db_url: str, institution_name: str = None):
    """
    保存或更新患者挂号记录，包含新增的签约建档信息

    参数:
    data: 包含患者基本数据的字典
    result: 包含签约建档信息的字典
    db_url: 数据库连接URL (e.g. 'mysql+pymysql://user:password@localhost/db_name')
    """
    # 创建数据库引擎和会话
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 转换结果数据类型
        # 处理日期字段
        for date_field in ['挂号时间', '档案创建时间', '签约日期', '首次签约日期', '就诊日期']:
            if not (result.get(date_field) and result[date_field].strip()):
                result[date_field] = None
                continue

            try:
                result[date_field] = parse(result[date_field].strip())
            except ValueError:
                result[date_field] = None

        # 处理空值
        for field in ['是否本机构建档', '是否外机构建档', '是否本机构签约', '是否外机构签约']:
            result[field] = result.get(field) if result.get(field) in ['是', '否'] else None

        # 查询是否存在匹配记录
        existing_record = session.query(PatientRegistration).filter(
            PatientRegistration.身份证号 == data['身份证'],
            PatientRegistration.serial_number == data['门诊序号'],
            PatientRegistration.诊疗医生 == data['诊疗医生'],
            PatientRegistration.registration_time == data['挂号时间']
        ).first()

        for field in ['现金', '诊疗费', '挂号费', '基金']:
            data[field] = float(data.get(field, 0.0)) if data.get(field) not in [None, ''] else None

        # 准备数据字典 - 基础数据
        record_data = {
            'name': data['姓名'],
            'gender': data['性别'],
            '身份证号': data['身份证'],
            'address': data['地址'],
            'phone': data['电话'],
            'diagnosis': data['诊断'],
            'fee_type': data['费别'],
            'serial_number': data['门诊序号'],
            'medical_insurance_number': data['医保号'],
            'department': data['科室'],
            'registration_doctor': data['挂号医生'] if data.get('挂号医生') else '未选择',
            'registration_type': data['挂号类型'],
            'registration_time': data['挂号时间'],
            'consultation_fee': data['诊疗费'],
            'registration_fee': data['挂号费'],
            'fund': data['基金'],
            'cash': data['现金'],
            '诊疗医生': data['诊疗医生']
        }

        # 添加结果数据 (使用中文键名)
        record_data.update({
            '是否本机构建档': result.get('是否本机构建档'),
            '是否外机构建档': result.get('是否外机构建档'),
            '建档日期': result.get('档案创建时间'),
            '是否本机构签约': result.get('是否本机构签约'),
            '是否外机构签约': result.get('是否外机构签约'),
            '签约日期': result.get('签约日期'),
            '首次签约日期': result.get('首次签约日期'),
            '团队名称': result.get('团队名称'),
            '签约医生姓名': result.get('签约医生姓名'),
            '签约来源': result.get('签约来源'),
            '就诊日期': result.get('就诊日期')
        })

        record_data['institution_name'] = institution_name if institution_name else '未知机构'

        # 处理空值诊断信息
        if record_data['diagnosis'] is None or record_data['diagnosis'] == '':
            record_data['diagnosis'] = None

        if existing_record:
            # 更新现有记录 - 包括新增字段
            for key, value in record_data.items():
                setattr(existing_record, key, value)
            session.commit()
            print(f"记录已更新，ID: {existing_record.id}")
            return existing_record.id
        else:
            # 插入新记录 - 包含所有字段
            new_record = PatientRegistration(**record_data)
            session.add(new_record)
            session.commit()
            print(f"新记录已创建，ID: {new_record.id}")
            return new_record.id

    except Exception as e:
        session.rollback()
        print(f"操作失败: {str(e)}")
        raise
    finally:
        session.close()
