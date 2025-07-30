from sqlalchemy import create_engine, Column, Integer, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# 使用已有的Base
Base = declarative_base()


class HealthRecord(Base):
    __tablename__ = 'health_records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_records = Column(Integer, nullable=False, default=0, comment='总建档人数')
    total_signed = Column(Integer, nullable=False, default=0, comment='总签约人数')  # 新增字段
    children_0_6_signed = Column(Integer, nullable=False, default=0, comment='0-6周岁儿童签约人数')
    pregnant_women_signed = Column(Integer, nullable=False, default=0, comment='孕产妇签约人数')
    disabled_signed = Column(Integer, nullable=False, default=0, comment='残疾人签约人数')
    elderly_signed = Column(Integer, nullable=False, default=0, comment='老年人签约人数')
    general_population_signed = Column(Integer, nullable=False, default=0, comment='一般人群签约人数')
    hypertension_managed = Column(Integer, nullable=False, default=0, comment='高血压管理数')
    diabetes_managed = Column(Integer, nullable=False, default=0, comment='糖尿病管理数')
    hypertension_standard_managed = Column(Integer, nullable=False, default=0, comment='高血压规范管理数')
    diabetes_standard_managed = Column(Integer, nullable=False, default=0, comment='糖尿病规范管理数')
    hypertension_count = Column(Integer, nullable=False, default=0, comment='高血压人数')
    diabetes_count = Column(Integer, nullable=False, default=0, comment='糖尿病人数')
    coronary_heart_disease_count = Column(Integer, nullable=False, default=0, comment='冠心病人数')
    stroke_count = Column(Integer, nullable=False, default=0, comment='脑卒中人数')
    copd_count = Column(Integer, nullable=False, default=0, comment='慢阻肺人数')
    created_at = Column(TIMESTAMP, server_default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment='更新时间')


def save_or_update_health_record(data: dict, db_url: str):
    """
    保存或更新健康档案统计记录到health_records表

    参数:
    data: 包含健康档案统计数据的字典，格式如：
        {
            '总档案人数': 67772,
            '总签约人数': 35021,   # 新增字段
            '0-6周岁儿童签约人数': 4474,
            '孕产妇签约人数': 448,
            '残疾人签约人数': 982,
            '老年人签约人数': 9905,
            '一般人群签约人数': 19752,
            '高血压管理数': 6330,
            '糖尿病管理数': 3012,
            '高血压人数': 12516,
            '糖尿病人数': 5721,
            '冠心病人数': 3419,
            '脑卒中人数': 1545,
            '慢阻肺人数': 70,
            '高血压规范管理数量': 5126,
            '糖尿病规范管理数量': 2548
        }
    db_url: 数据库连接URL
    """
    # 创建数据库引擎和会话
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 字段映射字典（前端字段名 -> 数据库字段名）
        field_mapping = {
            '总档案人数': 'total_records',
            '总签约人数': 'total_signed',  # 新增映射
            '0-6周岁儿童签约人数': 'children_0_6_signed',
            '孕产妇签约人数': 'pregnant_women_signed',
            '残疾人签约人数': 'disabled_signed',
            '老年人签约人数': 'elderly_signed',
            '一般人群签约人数': 'general_population_signed',
            '高血压管理数': 'hypertension_managed',
            '糖尿病管理数': 'diabetes_managed',
            '高血压规范管理数量': 'hypertension_standard_managed',
            '糖尿病规范管理数量': 'diabetes_standard_managed',
            '高血压人数': 'hypertension_count',
            '糖尿病人数': 'diabetes_count',
            '冠心病人数': 'coronary_heart_disease_count',
            '脑卒中人数': 'stroke_count',
            '慢阻肺人数': 'copd_count'
        }

        # 准备转换后的数据
        record_data = {}
        for key, value in data.items():
            if key in field_mapping:
                try:
                    # 确保值为整数（空值或非数字处理为0）
                    record_data[field_mapping[key]] = int(value) if value not in [None, ''] else 0
                except (ValueError, TypeError):
                    record_data[field_mapping[key]] = 0

        # 验证必要字段是否存在
        required_fields = ['total_records', 'total_signed']
        for field in required_fields:
            if field not in record_data:
                raise ValueError(f"缺少必要字段: {field}")

        # 查询是否已存在记录（假设只维护一条记录）
        existing_record = session.query(HealthRecord).first()

        if existing_record:
            # 更新现有记录
            for key, value in record_data.items():
                setattr(existing_record, key, value)
            session.commit()
            return existing_record.id
        else:
            # 创建新记录
            new_record = HealthRecord(**record_data)
            session.add(new_record)
            session.commit()
            return new_record.id

    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"数据库操作失败: {str(e)}")
    except Exception as e:
        session.rollback()
        raise Exception(f"操作失败: {str(e)}")
    finally:
        session.close()
