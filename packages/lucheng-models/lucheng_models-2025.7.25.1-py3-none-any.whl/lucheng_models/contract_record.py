from sqlalchemy import create_engine, Column, String, Date, Integer, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import BIGINT
from datetime import datetime

# 使用已有的Base或创建新的
Base = declarative_base()


class ContractRecord(Base):
    __tablename__ = 'contract_records'

    id = Column(BIGINT(unsigned=True), primary_key=True, comment='合同唯一ID（来自原始数据）')
    name = Column(String(100), nullable=False, comment='姓名')
    id_number = Column(String(20), nullable=False, comment='身份证号')
    sign_team = Column(String(100), nullable=False, comment='签约团队名称')
    sign_date = Column(Date, nullable=False, comment='签订时间')
    effective_date = Column(Date, nullable=False, comment='生效时间')
    end_date = Column(Date, nullable=False, comment='结束时间')
    first_date = Column(Date, nullable=False, comment='首次签订时间')
    validity_period = Column(Integer, nullable=False, comment='有效期（单位：年）')
    contract_state = Column(Integer, nullable=False, comment='当前状态')
    is_need_pay = Column(Integer, nullable=False, comment='收费状态（1收费/0免费）')
    created_at = Column(TIMESTAMP, server_default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment='更新时间')


def save_or_update_contract_record(data: dict, db_url: str):
    """
    保存或更新签约记录到contract_records表

    参数:
    data: 包含签约记录数据的字典，格式如：
        {
            "姓名": "闫玉凤",
            "身份证号": "110223195609013922",
            "签约团队": "第10 团队",
            "签订时间": "2024-07-11",
            "生效时间": "2024-07-11",
            "结束时间": "2025-07-10",
            "首次签约时间": "2023-02-16",
            "有效期": "1",
            "当前状态": "2",
            "收费状态": "1",
            "合同ID": "1694815"
        }
    db_url: 数据库连接URL
    """
    # 创建数据库引擎和会话
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 转换日期字段
        # 转换日期字段（增强空值处理）
        date_fields = {
            "签订时间": ("sign_date", True),
            "生效时间": ("effective_date", True),
            "结束时间": ("end_date", True),
            "首次签约时间": ("first_date", False)  # 标记为可空字段
        }
        # 先处理必填日期字段
        for field, (attr, required) in date_fields.items():
            value = data.get(field)
            if value and value.strip():
                try:
                    data[attr] = datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    if required:
                        raise ValueError(f"无效的日期格式: {field}={value}")
                    data[attr] = None  # 允许首次签约时间为NULL
            else:
                if required:
                    raise ValueError(f"缺少必填日期字段: {field}")
                data[attr] = None  # 允许首次签约时间为NULL

        # === 修复点：增强字段转换的容错能力 ===
        # 1. 处理有效期（默认0）
        try:
            data["有效期"] = int(data["有效期"])
        except (ValueError, TypeError):
            data["有效期"] = 0  # 或根据业务设置合理默认值
        # 2. 处理当前状态（默认0）
        try:
            data["当前状态"] = int(data["当前状态"])
        except (ValueError, TypeError):
            data["当前状态"] = 0  # 或根据业务设置合理默认值
        # 3. 关键修复：处理收费状态（映射非数字值）
        fee_status = str(data["收费状态"]).strip()  # 统一转为字符串处理
        if fee_status in ["1", "收费"]:
            data["收费状态"] = 1
        elif fee_status in ["0", "免费"]:
            data["收费状态"] = 0
        else:  # 处理 '未知' 等意外值
            data["收费状态"] = 0  # 根据业务需求选择默认值
        # 4. 处理合同ID（默认0或生成新ID）
        try:
            data["合同ID"] = int(data["合同ID"])
        except (ValueError, TypeError):
            data["合同ID"] = 0  # 注意：如果是主键需确保唯一性

        # 查询是否已存在相同身份证号的记录
        existing_record = session.query(ContractRecord).filter(
            ContractRecord.id_number == data["身份证号"]
        ).first()

        # 准备数据字典（使用转换后的字段名）
        record_data = {
            'id': data["合同ID"],
            'name': data["姓名"],
            'id_number': data["身份证号"],
            'sign_team': data["签约团队"],
            'sign_date': data["sign_date"],       # 使用转换后的值
            'effective_date': data["effective_date"],
            'end_date': data["end_date"],
            'first_date': data["first_date"],     # 可能为None
            'validity_period': data["有效期"],
            'contract_state': data["当前状态"],
            'is_need_pay': data["收费状态"]
        }

        if existing_record:
            # 更新现有记录
            for key, value in record_data.items():
                # 跳过主键ID的更新
                if key != 'id':
                    setattr(existing_record, key, value)
            session.commit()
            # print(f"签约记录已更新，身份证号: {data['身份证号']}")
            return existing_record.id
        else:
            # 插入新记录
            new_record = ContractRecord(**record_data)
            session.add(new_record)
            session.commit()
            # print(f"新签约记录已创建，身份证号: {data['身份证号']}")
            return new_record.id

    except Exception as e:
        session.rollback()
        print(f"操作失败: {str(e)}")
        raise
    finally:
        session.close()

