
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, nullable=False)
    email = Column(String(256))
    api_key = Column(String(128), unique=True, nullable=True)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    filename = Column(String(512))
    content = Column(Text)
    uploaded_at = Column(TIMESTAMP)

class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    title = Column(Text)
    description = Column(Text)
    type = Column(String(64))
    steps = Column(Text)
    expected_result = Column(Text)
    created_at = Column(TIMESTAMP)

class BugReport(Base):
    __tablename__ = "bug_reports"
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="SET NULL"))
    summary = Column(Text)
    severity = Column(String(32))
    description = Column(Text)
    created_at = Column(TIMESTAMP)
